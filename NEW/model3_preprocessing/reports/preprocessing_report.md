# RAVDESS Dataset Audit and Preprocessing Report

## 1) Raw Dataset Audit
- Total WAV files discovered: 2880
- Files with valid RAVDESS naming pattern: 2880
- Readable audio files: 2880
- Unique audio hashes: 1439
- Duplicate files detected: 1441

### Emotion Distribution (Raw)
- angry: 384
- calm: 384
- disgust: 384
- fearful: 384
- happy: 384
- neutral: 192
- sad: 384
- surprised: 384

### Target 4-Class Distribution (Raw)
- distressed: 768
- happy: 768
- low: 768
- neutral: 576

### Audio Format Summary (Raw)
- Sample rates: {48000: 2880}
- Channel counts: {1: 2870, 2: 10}
- Duration stats (sec): {'count': 2880, 'min': 2.936271, 'max': 5.271937, 'mean': 3.700665, 'median': 3.670333}

## 2) Cleaning Performed
- Removed mirrored/duplicate audio by hash using canonical path preference.
- Removed entries with invalid filename pattern or unreadable audio.
- Standardized all clean files to mono 16kHz PCM-16 WAV.
- Peak-normalized waveforms to avoid clipping and level mismatch.
- Clean files generated: 1439
- Rejected files: 1441
- Duration stats after cleaning (sec): {'count': 1439, 'min': 2.936271, 'max': 5.271937, 'mean': 3.700871, 'median': 3.670333}

### 4-Class Distribution (Clean)
- distressed: 384
- happy: 383
- low: 384
- neutral: 288

## 3) Balancing Strategy
- Applied class balancing by random undersampling to the smallest class size.
- Class counts before balancing: {'neutral': 288, 'happy': 383, 'low': 384, 'distressed': 384}
- Selected per class: 288
- Total balanced files: 1152

### 4-Class Distribution (Balanced)
- distressed: 288
- happy: 288
- low: 288
- neutral: 288

## 4) Output Artifacts
- reports/raw_manifest.csv
- reports/duplicates_report.csv
- reports/rejected_files.csv
- reports/clean_manifest.csv
- reports/balanced_manifest.csv
- reports/summary.json
- reports/preprocessing_report.md
- processed/clean_16k_mono/
- processed/balanced_16k_mono/
