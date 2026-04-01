import argparse
import csv
import hashlib
import json
import os
import random
import re
import statistics
import wave
from collections import Counter, defaultdict
from pathlib import Path

import librosa
import numpy as np
import soundfile as sf


FILENAME_RE = re.compile(r"^(\d{2})-(\d{2})-(\d{2})-(\d{2})-(\d{2})-(\d{2})-(\d{2})\.wav$", re.IGNORECASE)

EMOTION_CODE_TO_NAME = {
    "01": "neutral",
    "02": "calm",
    "03": "happy",
    "04": "sad",
    "05": "angry",
    "06": "fearful",
    "07": "disgust",
    "08": "surprised",
}

TARGET_CLASS_MAP = {
    "neutral": "neutral",
    "calm": "neutral",
    "happy": "happy",
    "surprised": "happy",
    "sad": "low",
    "fearful": "low",
    "angry": "distressed",
    "disgust": "distressed",
}


def iter_wavs(root_dir: Path):
    for base, _, files in os.walk(root_dir):
        for name in files:
            if name.lower().endswith(".wav"):
                yield Path(base) / name


def parse_filename(filename: str):
    match = FILENAME_RE.match(filename)
    if not match:
        return None

    modality, vocal_channel, emotion_code, intensity, statement, repetition, actor = match.groups()
    emotion_name = EMOTION_CODE_TO_NAME.get(emotion_code)
    if emotion_name is None:
        return None

    target_class = TARGET_CLASS_MAP[emotion_name]
    return {
        "modality": modality,
        "vocal_channel": vocal_channel,
        "emotion_code": emotion_code,
        "emotion_name": emotion_name,
        "target_class": target_class,
        "intensity": intensity,
        "statement": statement,
        "repetition": repetition,
        "actor": actor,
    }


def hash_file(path: Path, chunk_size: int = 1024 * 1024):
    hasher = hashlib.sha1()
    with path.open("rb") as handle:
        while True:
            block = handle.read(chunk_size)
            if not block:
                break
            hasher.update(block)
    return hasher.hexdigest()


def inspect_wav(path: Path):
    with wave.open(str(path), "rb") as wav_file:
        channels = wav_file.getnchannels()
        sample_rate = wav_file.getframerate()
        sample_width = wav_file.getsampwidth()
        frame_count = wav_file.getnframes()
        duration_sec = frame_count / float(sample_rate)
    return channels, sample_rate, sample_width, frame_count, duration_sec


def canonical_rank(path: Path):
    path_text = str(path).replace("\\", "/").lower()
    # Prefer the official nested package folder over duplicate mirrored folders.
    preferred = 0 if "audio_speech_actors_01-24" in path_text else 1
    return (preferred, len(path_text), path_text)


def build_raw_records(dataset_root: Path):
    records = []
    for wav_path in iter_wavs(dataset_root):
        relative_path = wav_path.relative_to(dataset_root)
        parsed = parse_filename(wav_path.name)

        record = {
            "path": str(wav_path),
            "relative_path": str(relative_path).replace("\\", "/"),
            "filename": wav_path.name,
            "valid_filename": parsed is not None,
            "hash": "",
            "channels": "",
            "sample_rate": "",
            "sample_width": "",
            "frame_count": "",
            "duration_sec": "",
            "error": "",
            "modality": "",
            "vocal_channel": "",
            "emotion_code": "",
            "emotion_name": "",
            "target_class": "",
            "intensity": "",
            "statement": "",
            "repetition": "",
            "actor": "",
        }

        if parsed is not None:
            record.update(parsed)

        try:
            channels, sample_rate, sample_width, frame_count, duration_sec = inspect_wav(wav_path)
            file_hash = hash_file(wav_path)
            record.update(
                {
                    "hash": file_hash,
                    "channels": channels,
                    "sample_rate": sample_rate,
                    "sample_width": sample_width,
                    "frame_count": frame_count,
                    "duration_sec": round(duration_sec, 6),
                }
            )
        except Exception as exc:  # pylint: disable=broad-except
            record["error"] = str(exc)

        records.append(record)

    return records


def write_csv(path: Path, rows, fieldnames):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def duration_stats(values):
    if not values:
        return {"count": 0, "min": None, "max": None, "mean": None, "median": None}
    return {
        "count": len(values),
        "min": round(min(values), 6),
        "max": round(max(values), 6),
        "mean": round(statistics.mean(values), 6),
        "median": round(statistics.median(values), 6),
    }


def prepare_clean_dataset(records, dataset_root: Path, clean_root: Path, target_sr: int):
    clean_root.mkdir(parents=True, exist_ok=True)

    hash_to_records = defaultdict(list)
    for rec in records:
        if rec["hash"]:
            hash_to_records[rec["hash"]].append(rec)

    keep_paths = set()
    duplicate_rows = []
    for file_hash, items in hash_to_records.items():
        if len(items) == 1:
            keep_paths.add(items[0]["path"])
            continue

        sorted_items = sorted(items, key=lambda item: canonical_rank(Path(item["path"])))
        canonical = sorted_items[0]
        keep_paths.add(canonical["path"])

        for dup in sorted_items[1:]:
            duplicate_rows.append(
                {
                    "hash": file_hash,
                    "canonical_path": canonical["path"],
                    "duplicate_path": dup["path"],
                }
            )

    clean_manifest = []
    rejected_rows = []

    for rec in records:
        if rec["path"] not in keep_paths:
            rejected_rows.append({"path": rec["path"], "reason": "duplicate_of_canonical"})
            continue
        if not rec["valid_filename"]:
            rejected_rows.append({"path": rec["path"], "reason": "invalid_filename_pattern"})
            continue
        if rec["error"]:
            rejected_rows.append({"path": rec["path"], "reason": "audio_read_error"})
            continue

        src_path = Path(rec["path"])
        target_class = rec["target_class"]
        dst_dir = clean_root / target_class
        dst_dir.mkdir(parents=True, exist_ok=True)
        dst_path = dst_dir / src_path.name

        # Ensure unique output filenames even in unlikely collisions.
        if dst_path.exists():
            stem = dst_path.stem
            suffix = dst_path.suffix
            idx = 2
            while True:
                candidate = dst_dir / f"{stem}__{idx}{suffix}"
                if not candidate.exists():
                    dst_path = candidate
                    break
                idx += 1

        audio, _ = librosa.load(src_path, sr=target_sr, mono=True)
        peak = float(np.max(np.abs(audio))) if audio.size else 0.0
        if peak > 0:
            audio = 0.99 * (audio / peak)

        sf.write(dst_path, audio, target_sr, subtype="PCM_16")

        clean_manifest.append(
            {
                **rec,
                "clean_path": str(dst_path),
                "clean_relative": str(dst_path.relative_to(clean_root)).replace("\\", "/"),
                "clean_sample_rate": target_sr,
                "clean_channels": 1,
            }
        )

    return clean_manifest, duplicate_rows, rejected_rows


def prepare_balanced_dataset(clean_manifest, balanced_root: Path, seed: int):
    balanced_root.mkdir(parents=True, exist_ok=True)

    by_class = defaultdict(list)
    for rec in clean_manifest:
        by_class[rec["target_class"]].append(rec)

    if not by_class:
        return [], {"class_counts": {}, "selected_per_class": 0}

    class_counts = {label: len(items) for label, items in by_class.items()}
    selected_per_class = min(class_counts.values())

    rng = random.Random(seed)
    balanced_manifest = []

    for label, items in sorted(by_class.items()):
        items_sorted = sorted(items, key=lambda row: row["clean_path"])
        selected = rng.sample(items_sorted, selected_per_class)

        for rec in selected:
            src_path = Path(rec["clean_path"])
            dst_dir = balanced_root / label
            dst_dir.mkdir(parents=True, exist_ok=True)
            dst_path = dst_dir / src_path.name

            if dst_path.exists():
                stem = dst_path.stem
                suffix = dst_path.suffix
                idx = 2
                while True:
                    candidate = dst_dir / f"{stem}__{idx}{suffix}"
                    if not candidate.exists():
                        dst_path = candidate
                        break
                    idx += 1

            audio, sr = sf.read(src_path)
            sf.write(dst_path, audio, sr, subtype="PCM_16")

            balanced_manifest.append(
                {
                    **rec,
                    "balanced_path": str(dst_path),
                    "balanced_relative": str(dst_path.relative_to(balanced_root)).replace("\\", "/"),
                }
            )

    summary = {
        "class_counts": class_counts,
        "selected_per_class": selected_per_class,
        "balanced_total": len(balanced_manifest),
    }
    return balanced_manifest, summary


def write_markdown_report(
    report_path: Path,
    raw_records,
    clean_manifest,
    balanced_manifest,
    duplicate_rows,
    rejected_rows,
    balance_summary,
):
    raw_count = len(raw_records)
    valid_filename_count = sum(1 for row in raw_records if row["valid_filename"])
    readable_count = sum(1 for row in raw_records if not row["error"])
    unique_hash_count = len({row["hash"] for row in raw_records if row["hash"]})

    emotion_counter = Counter(row["emotion_name"] for row in raw_records if row["emotion_name"])
    class_counter_raw = Counter(row["target_class"] for row in raw_records if row["target_class"])
    class_counter_clean = Counter(row["target_class"] for row in clean_manifest)
    class_counter_balanced = Counter(row["target_class"] for row in balanced_manifest)

    sample_rates = Counter(int(row["sample_rate"]) for row in raw_records if row["sample_rate"] != "")
    channels = Counter(int(row["channels"]) for row in raw_records if row["channels"] != "")

    durations_raw = [float(row["duration_sec"]) for row in raw_records if row["duration_sec"] != ""]
    durations_clean = [float(row["duration_sec"]) for row in clean_manifest if row["duration_sec"] != ""]

    lines = []
    lines.append("# RAVDESS Dataset Audit and Preprocessing Report")
    lines.append("")
    lines.append("## 1) Raw Dataset Audit")
    lines.append(f"- Total WAV files discovered: {raw_count}")
    lines.append(f"- Files with valid RAVDESS naming pattern: {valid_filename_count}")
    lines.append(f"- Readable audio files: {readable_count}")
    lines.append(f"- Unique audio hashes: {unique_hash_count}")
    lines.append(f"- Duplicate files detected: {len(duplicate_rows)}")
    lines.append("")
    lines.append("### Emotion Distribution (Raw)")
    for label, count in sorted(emotion_counter.items()):
        lines.append(f"- {label}: {count}")
    lines.append("")
    lines.append("### Target 4-Class Distribution (Raw)")
    for label, count in sorted(class_counter_raw.items()):
        lines.append(f"- {label}: {count}")
    lines.append("")
    lines.append("### Audio Format Summary (Raw)")
    lines.append(f"- Sample rates: {dict(sorted(sample_rates.items()))}")
    lines.append(f"- Channel counts: {dict(sorted(channels.items()))}")
    lines.append(f"- Duration stats (sec): {duration_stats(durations_raw)}")
    lines.append("")

    lines.append("## 2) Cleaning Performed")
    lines.append("- Removed mirrored/duplicate audio by hash using canonical path preference.")
    lines.append("- Removed entries with invalid filename pattern or unreadable audio.")
    lines.append("- Standardized all clean files to mono 16kHz PCM-16 WAV.")
    lines.append("- Peak-normalized waveforms to avoid clipping and level mismatch.")
    lines.append(f"- Clean files generated: {len(clean_manifest)}")
    lines.append(f"- Rejected files: {len(rejected_rows)}")
    lines.append(f"- Duration stats after cleaning (sec): {duration_stats(durations_clean)}")
    lines.append("")
    lines.append("### 4-Class Distribution (Clean)")
    for label, count in sorted(class_counter_clean.items()):
        lines.append(f"- {label}: {count}")
    lines.append("")

    lines.append("## 3) Balancing Strategy")
    lines.append("- Applied class balancing by random undersampling to the smallest class size.")
    lines.append(f"- Class counts before balancing: {balance_summary.get('class_counts', {})}")
    lines.append(f"- Selected per class: {balance_summary.get('selected_per_class', 0)}")
    lines.append(f"- Total balanced files: {balance_summary.get('balanced_total', 0)}")
    lines.append("")
    lines.append("### 4-Class Distribution (Balanced)")
    for label, count in sorted(class_counter_balanced.items()):
        lines.append(f"- {label}: {count}")
    lines.append("")

    lines.append("## 4) Output Artifacts")
    lines.append("- reports/raw_manifest.csv")
    lines.append("- reports/duplicates_report.csv")
    lines.append("- reports/rejected_files.csv")
    lines.append("- reports/clean_manifest.csv")
    lines.append("- reports/balanced_manifest.csv")
    lines.append("- reports/summary.json")
    lines.append("- reports/preprocessing_report.md")
    lines.append("- processed/clean_16k_mono/")
    lines.append("- processed/balanced_16k_mono/")
    lines.append("")
    report_path.write_text("\n".join(lines), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="Audit and preprocess RAVDESS for ARIA Model 3")
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("voice dataset ravdess"),
        help="Path to raw RAVDESS root folder",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=Path("NEW/model3_preprocessing"),
        help="Output root folder for reports and processed files",
    )
    parser.add_argument("--target-sr", type=int, default=16000, help="Target sample rate for standardized audio")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for class balancing")
    args = parser.parse_args()

    dataset_root = args.input.resolve()
    output_root = args.output_root.resolve()

    reports_dir = output_root / "reports"
    processed_dir = output_root / "processed"
    clean_root = processed_dir / "clean_16k_mono"
    balanced_root = processed_dir / "balanced_16k_mono"

    reports_dir.mkdir(parents=True, exist_ok=True)
    processed_dir.mkdir(parents=True, exist_ok=True)

    if not dataset_root.exists():
        raise FileNotFoundError(f"Input dataset directory not found: {dataset_root}")

    print(f"[1/4] Auditing raw dataset: {dataset_root}")
    raw_records = build_raw_records(dataset_root)

    raw_fieldnames = [
        "path",
        "relative_path",
        "filename",
        "valid_filename",
        "hash",
        "channels",
        "sample_rate",
        "sample_width",
        "frame_count",
        "duration_sec",
        "error",
        "modality",
        "vocal_channel",
        "emotion_code",
        "emotion_name",
        "target_class",
        "intensity",
        "statement",
        "repetition",
        "actor",
    ]
    write_csv(reports_dir / "raw_manifest.csv", raw_records, raw_fieldnames)

    print("[2/4] Cleaning and standardizing audio")
    clean_manifest, duplicate_rows, rejected_rows = prepare_clean_dataset(
        raw_records,
        dataset_root=dataset_root,
        clean_root=clean_root,
        target_sr=args.target_sr,
    )

    write_csv(reports_dir / "duplicates_report.csv", duplicate_rows, ["hash", "canonical_path", "duplicate_path"])
    write_csv(reports_dir / "rejected_files.csv", rejected_rows, ["path", "reason"])

    clean_fieldnames = raw_fieldnames + ["clean_path", "clean_relative", "clean_sample_rate", "clean_channels"]
    write_csv(reports_dir / "clean_manifest.csv", clean_manifest, clean_fieldnames)

    print("[3/4] Creating balanced dataset")
    balanced_manifest, balance_summary = prepare_balanced_dataset(
        clean_manifest,
        balanced_root=balanced_root,
        seed=args.seed,
    )

    balanced_fieldnames = clean_fieldnames + ["balanced_path", "balanced_relative"]
    write_csv(reports_dir / "balanced_manifest.csv", balanced_manifest, balanced_fieldnames)

    summary = {
        "raw_total_files": len(raw_records),
        "raw_valid_filename": sum(1 for r in raw_records if r["valid_filename"]),
        "raw_readable": sum(1 for r in raw_records if not r["error"]),
        "raw_unique_hashes": len({r["hash"] for r in raw_records if r["hash"]}),
        "duplicates_removed": len(duplicate_rows),
        "rejected_files": len(rejected_rows),
        "clean_total_files": len(clean_manifest),
        "balanced_total_files": len(balanced_manifest),
        "balance_summary": balance_summary,
    }
    (reports_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print("[4/4] Writing preprocessing report")
    write_markdown_report(
        reports_dir / "preprocessing_report.md",
        raw_records,
        clean_manifest,
        balanced_manifest,
        duplicate_rows,
        rejected_rows,
        balance_summary,
    )

    print("Done. Summary:")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
