import argparse
import csv
import json
import time
from pathlib import Path

import joblib
import librosa
import matplotlib.pyplot as plt
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import GroupShuffleSplit, RandomizedSearchCV, StratifiedGroupKFold


def load_manifest(manifest_path: Path):
    rows = []
    with manifest_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            rows.append(row)
    return rows


def safe_stats(x):
    x = np.asarray(x, dtype=np.float32)
    if x.size == 0:
        return [0.0, 0.0, 0.0, 0.0]
    return [
        float(np.mean(x)),
        float(np.std(x)),
        float(np.min(x)),
        float(np.max(x)),
    ]


def matrix_stats(mat):
    arr = np.asarray(mat, dtype=np.float32)
    if arr.ndim == 1:
        arr = arr.reshape(1, -1)
    features = []
    for i in range(arr.shape[0]):
        row = arr[i]
        features.extend([float(np.mean(row)), float(np.std(row))])
    return features


def extract_features(audio_path: Path, sr: int = 16000):
    y, _ = librosa.load(audio_path, sr=sr, mono=True)
    if y.size == 0:
        y = np.zeros(sr, dtype=np.float32)

    # Ensure minimum context for stable spectral statistics.
    min_len = int(0.5 * sr)
    if y.size < min_len:
        y = np.pad(y, (0, min_len - y.size), mode="constant")

    y = librosa.util.normalize(y)

    zcr = librosa.feature.zero_crossing_rate(y)[0]
    rms = librosa.feature.rms(y=y)[0]
    centroid = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
    bandwidth = librosa.feature.spectral_bandwidth(y=y, sr=sr)[0]
    rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)[0]
    flatness = librosa.feature.spectral_flatness(y=y)[0]

    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=20)
    mfcc_delta = librosa.feature.delta(mfcc)
    mfcc_delta2 = librosa.feature.delta(mfcc, order=2)

    chroma = librosa.feature.chroma_stft(y=y, sr=sr)
    contrast = librosa.feature.spectral_contrast(y=y, sr=sr)
    tonnetz = librosa.feature.tonnetz(y=librosa.effects.harmonic(y), sr=sr)

    mel = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=40)
    mel_db = librosa.power_to_db(mel, ref=np.max)

    onset_env = librosa.onset.onset_strength(y=y, sr=sr)
    tempo = float(librosa.feature.tempo(onset_envelope=onset_env, sr=sr)[0])

    try:
        f0 = librosa.yin(y, fmin=50, fmax=500, sr=sr)
        f0 = f0[np.isfinite(f0)]
    except Exception:  # pylint: disable=broad-except
        f0 = np.array([], dtype=np.float32)

    silence_ratio = float(np.mean(np.abs(y) < 0.01))
    duration_sec = float(y.size / sr)

    features = []
    features.extend(safe_stats(zcr))
    features.extend(safe_stats(rms))
    features.extend(safe_stats(centroid))
    features.extend(safe_stats(bandwidth))
    features.extend(safe_stats(rolloff))
    features.extend(safe_stats(flatness))

    features.extend(matrix_stats(mfcc))
    features.extend(matrix_stats(mfcc_delta))
    features.extend(matrix_stats(mfcc_delta2))
    features.extend(matrix_stats(chroma))
    features.extend(matrix_stats(contrast))
    features.extend(matrix_stats(tonnetz))
    features.extend(matrix_stats(mel_db))

    features.extend(safe_stats(onset_env))
    features.extend(safe_stats(f0))

    features.append(tempo)
    features.append(silence_ratio)
    features.append(duration_sec)

    return np.asarray(features, dtype=np.float32)


def build_dataset(rows, feature_sr: int):
    X = []
    y = []
    groups = []
    paths = []

    for row in rows:
        audio_path = Path(row["balanced_path"])
        label = row["target_class"]
        actor = row["actor"]

        feats = extract_features(audio_path, sr=feature_sr)
        X.append(feats)
        y.append(label)
        groups.append(actor)
        paths.append(str(audio_path))

    X = np.vstack(X)
    y = np.asarray(y)
    groups = np.asarray(groups)
    paths = np.asarray(paths)
    return X, y, groups, paths


def metrics_dict(y_true, y_pred):
    return {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "balanced_accuracy": float(balanced_accuracy_score(y_true, y_pred)),
        "precision_macro": float(precision_score(y_true, y_pred, average="macro", zero_division=0)),
        "recall_macro": float(recall_score(y_true, y_pred, average="macro", zero_division=0)),
        "f1_macro": float(f1_score(y_true, y_pred, average="macro", zero_division=0)),
    }


def select_overfit_aware_best(cv_results, penalty: float):
    best_idx = None
    best_score = -1e9

    n = len(cv_results["params"])
    for i in range(n):
        test_score = cv_results["mean_test_score"][i]
        train_score = cv_results["mean_train_score"][i]
        gap = max(0.0, train_score - test_score)
        score = test_score - penalty * gap

        if score > best_score:
            best_score = score
            best_idx = i

    return best_idx


def save_confusion_matrix(cm, labels, out_csv: Path, out_png: Path):
    out_csv.parent.mkdir(parents=True, exist_ok=True)

    with out_csv.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["true/pred"] + labels)
        for i, row in enumerate(cm):
            writer.writerow([labels[i]] + list(row))

    fig = plt.figure(figsize=(7, 6))
    ax = fig.add_subplot(111)
    im = ax.imshow(cm, interpolation="nearest")
    fig.colorbar(im, ax=ax)
    ax.set_xticks(np.arange(len(labels)))
    ax.set_yticks(np.arange(len(labels)))
    ax.set_xticklabels(labels, rotation=45, ha="right")
    ax.set_yticklabels(labels)
    ax.set_xlabel("Predicted")
    ax.set_ylabel("True")
    ax.set_title("Model 3 Confusion Matrix (Actor-Disjoint Test)")

    thresh = cm.max() / 2.0 if cm.size else 0.0
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            ax.text(j, i, str(cm[i, j]), ha="center", va="center", color="white" if cm[i, j] > thresh else "black")

    fig.tight_layout()
    fig.savefig(out_png, dpi=180)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description="Train ARIA Model 3 (Voice Mood & Well-being Classifier)")
    parser.add_argument(
        "--manifest",
        type=Path,
        default=Path("NEW/model3_preprocessing/reports/balanced_manifest.csv"),
        help="Balanced manifest CSV",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("NEW/model3_preprocessing/model3_training"),
        help="Output directory for model and reports",
    )
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--feature-sr", type=int, default=16000)
    parser.add_argument("--test-size", type=float, default=0.20)
    parser.add_argument("--search-iters", type=int, default=24)
    parser.add_argument("--overfit-penalty", type=float, default=0.6)
    args = parser.parse_args()

    t0 = time.time()

    output_dir = args.output.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    rows = load_manifest(args.manifest.resolve())
    if not rows:
        raise RuntimeError("Balanced manifest is empty. Cannot train model.")

    print("[1/5] Extracting features from balanced dataset...")
    X, y, groups, paths = build_dataset(rows, feature_sr=args.feature_sr)

    np.save(output_dir / "X_features.npy", X)
    np.save(output_dir / "y_labels.npy", y)

    unique_labels = sorted(np.unique(y).tolist())

    print("[2/5] Creating actor-disjoint train/test split...")
    splitter = GroupShuffleSplit(n_splits=1, test_size=args.test_size, random_state=args.seed)
    train_idx, test_idx = next(splitter.split(X, y, groups))

    X_train, X_test = X[train_idx], X[test_idx]
    y_train, y_test = y[train_idx], y[test_idx]
    g_train, g_test = groups[train_idx], groups[test_idx]

    train_actors = sorted(set(g_train.tolist()))
    test_actors = sorted(set(g_test.tolist()))
    actor_overlap = sorted(set(train_actors).intersection(test_actors))

    if actor_overlap:
        raise RuntimeError(f"Group leakage detected in split: {actor_overlap}")

    print("[3/5] Hyperparameter optimization (Random Forest, actor-aware CV)...")
    base_clf = RandomForestClassifier(random_state=args.seed, n_jobs=-1)

    param_dist = {
        "n_estimators": [250, 400, 600, 800, 1000],
        "max_depth": [None, 12, 18, 24, 32, 48],
        "min_samples_split": [2, 3, 5, 8, 12],
        "min_samples_leaf": [1, 2, 3, 4],
        "max_features": ["sqrt", "log2", 0.4, 0.6, 0.8],
        "criterion": ["gini", "entropy", "log_loss"],
        "class_weight": [None, "balanced", "balanced_subsample"],
        "bootstrap": [True],
    }

    cv = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=args.seed)

    search = RandomizedSearchCV(
        estimator=base_clf,
        param_distributions=param_dist,
        n_iter=args.search_iters,
        scoring="f1_macro",
        n_jobs=-1,
        cv=cv,
        random_state=args.seed,
        refit=False,
        verbose=1,
        return_train_score=True,
    )

    search.fit(X_train, y_train, groups=g_train)

    best_idx = select_overfit_aware_best(search.cv_results_, penalty=args.overfit_penalty)
    best_params = search.cv_results_["params"][best_idx]
    best_cv_test = float(search.cv_results_["mean_test_score"][best_idx])
    best_cv_train = float(search.cv_results_["mean_train_score"][best_idx])
    overfit_gap = max(0.0, best_cv_train - best_cv_test)

    print("[4/5] Fitting best overfit-aware model and evaluating...")
    best_clf = RandomForestClassifier(random_state=args.seed, n_jobs=-1, **best_params)
    best_clf.fit(X_train, y_train)

    y_pred_train = best_clf.predict(X_train)
    y_pred_test = best_clf.predict(X_test)

    train_metrics = metrics_dict(y_train, y_pred_train)
    test_metrics = metrics_dict(y_test, y_pred_test)

    report_dict = classification_report(y_test, y_pred_test, labels=unique_labels, output_dict=True, zero_division=0)

    cm = confusion_matrix(y_test, y_pred_test, labels=unique_labels)
    save_confusion_matrix(
        cm,
        unique_labels,
        out_csv=output_dir / "confusion_matrix_test.csv",
        out_png=output_dir / "confusion_matrix_test.png",
    )

    print("[5/5] Saving model artifacts and reports...")

    # Deployment model trained on full balanced data using selected hyperparameters.
    deploy_clf = RandomForestClassifier(random_state=args.seed, n_jobs=-1, **best_params)
    deploy_clf.fit(X, y)

    model_bundle = {
        "model_name": "ARIA Model 3 - Voice Mood & Well-being Classifier",
        "algorithm": "RandomForestClassifier",
        "feature_sr": args.feature_sr,
        "labels": unique_labels,
        "best_params": best_params,
        "model": deploy_clf,
        "feature_notes": {
            "domains": [
                "time_domain",
                "spectral",
                "mfcc",
                "chroma",
                "spectral_contrast",
                "tonnetz",
                "pitch",
                "tempo",
                "silence_ratio",
            ],
            "overfit_control": "Actor-disjoint test split + StratifiedGroupKFold tuning + overfit-penalized model selection",
        },
    }
    joblib.dump(model_bundle, output_dir / "model3_voice_mood_rf.pkl")

    # Save top CV results.
    top_rows = []
    for i, params in enumerate(search.cv_results_["params"]):
        test_score = float(search.cv_results_["mean_test_score"][i])
        train_score = float(search.cv_results_["mean_train_score"][i])
        gap = max(0.0, train_score - test_score)
        score = test_score - args.overfit_penalty * gap
        top_rows.append(
            {
                "rank_overfit_aware": 0,
                "mean_test_f1_macro": test_score,
                "mean_train_f1_macro": train_score,
                "overfit_gap": gap,
                "selection_score": score,
                "params": json.dumps(params),
            }
        )

    top_rows = sorted(top_rows, key=lambda r: r["selection_score"], reverse=True)
    for rank, row in enumerate(top_rows, start=1):
        row["rank_overfit_aware"] = rank

    with (output_dir / "cv_results_overfit_aware_top20.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "rank_overfit_aware",
                "mean_test_f1_macro",
                "mean_train_f1_macro",
                "overfit_gap",
                "selection_score",
                "params",
            ],
        )
        writer.writeheader()
        for row in top_rows[:20]:
            writer.writerow(row)

    summary = {
        "n_samples_total": int(X.shape[0]),
        "n_features": int(X.shape[1]),
        "labels": unique_labels,
        "train_size": int(len(train_idx)),
        "test_size": int(len(test_idx)),
        "train_actors": train_actors,
        "test_actors": test_actors,
        "best_params": best_params,
        "cv_best_mean_test_f1_macro": best_cv_test,
        "cv_best_mean_train_f1_macro": best_cv_train,
        "cv_overfit_gap": overfit_gap,
        "train_metrics": train_metrics,
        "test_metrics": test_metrics,
        "classification_report_test": report_dict,
        "runtime_seconds": round(time.time() - t0, 2),
    }
    (output_dir / "training_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    md_lines = []
    md_lines.append("# ARIA Model 3 Training Report")
    md_lines.append("")
    md_lines.append("## Objective")
    md_lines.append("Train a high-accuracy voice mood classifier with strong overfitting control for elderly care check-in audio.")
    md_lines.append("")
    md_lines.append("## Data")
    md_lines.append(f"- Source manifest: {args.manifest}")
    md_lines.append(f"- Samples: {X.shape[0]}")
    md_lines.append(f"- Features per sample: {X.shape[1]}")
    md_lines.append(f"- Classes: {', '.join(unique_labels)}")
    md_lines.append("")
    md_lines.append("## Overfitting Control Strategy")
    md_lines.append("- Actor-disjoint train/test split (GroupShuffleSplit)")
    md_lines.append("- Actor-aware cross-validation (StratifiedGroupKFold)")
    md_lines.append("- Overfit-penalized model selection on CV results")
    md_lines.append("")
    md_lines.append("## Best Model")
    md_lines.append(f"- Algorithm: RandomForestClassifier")
    md_lines.append(f"- Best params: `{json.dumps(best_params)}`")
    md_lines.append(f"- CV mean test F1-macro: {best_cv_test:.4f}")
    md_lines.append(f"- CV overfit gap (train-test): {overfit_gap:.4f}")
    md_lines.append("")
    md_lines.append("## Final Metrics")
    for k, v in test_metrics.items():
        md_lines.append(f"- Test {k}: {v:.4f}")
    for k, v in train_metrics.items():
        md_lines.append(f"- Train {k}: {v:.4f}")
    md_lines.append("")
    md_lines.append("## Artifacts")
    md_lines.append("- model3_voice_mood_rf.pkl")
    md_lines.append("- training_summary.json")
    md_lines.append("- cv_results_overfit_aware_top20.csv")
    md_lines.append("- confusion_matrix_test.csv")
    md_lines.append("- confusion_matrix_test.png")

    (output_dir / "training_report.md").write_text("\n".join(md_lines), encoding="utf-8")

    print("Training complete.")
    print(json.dumps({"test_metrics": test_metrics, "cv_best_f1_macro": best_cv_test, "overfit_gap": overfit_gap}, indent=2))


if __name__ == "__main__":
    main()
