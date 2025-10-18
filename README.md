# CopyMoveForgeryDetection

A computer vision project for copy-move forgery detection on unlabeled datasets **without using Deep Learning**. This implementation uses traditional computer vision techniques including feature detection, matching, and clustering algorithms.

## Overview

Copy-move forgery is a common type of image manipulation where a region of an image is copied and pasted to another location in the same image. This project implements multiple algorithms to detect such manipulations using:

- **Feature Detection**: SIFT, ORB, AKAZE
- **Feature Matching**: FLANN and BFMatcher
- **Clustering**: DBSCAN for identifying forged regions
- **Evaluation**: Precision, Recall, F1-Score, Accuracy metrics

## Project Structure

```
CopyMoveForgeryDetection/
├── data/                           # Datasets
│   ├── COVERAGE/                   # COVERAGE dataset
│   │   ├── image/                  # Original and tampered images
│   │   ├── mask/                   # Ground truth masks
│   │   └── label/                  # Annotations
│   ├── comofod_small/              # CoMoFoD dataset
│   │   └── CoMoFoD_small_v2/       # Images and masks
│   └── archive/                    # Additional datasets
│       └── copymove_annotations/   # COCO-based annotations
├── src/                            # Source code
│   ├── detect.py                   # Main detection script
│   └── utils.py                    # Utility functions
├── results/                        # Output directory
├── notebooks/                      # Jupyter notebooks (for experiments)
├── tests/                          # Unit tests
└── docs/                           # Documentation
```

## Features

### Detection Methods

1. **SIFT (Scale-Invariant Feature Transform)**
   - Robust to scale and rotation
   - Good for detecting complex transformations
   - Default method

2. **ORB (Oriented FAST and Rotated BRIEF)**
   - Faster than SIFT
   - Good for real-time applications
   - Binary descriptors

3. **AKAZE (Accelerated-KAZE)**
   - Good for non-linear scale spaces
   - Fast and accurate

### Algorithm Pipeline

1. **Feature Detection**: Extract keypoints and descriptors from the image
2. **Self-Matching**: Match features within the same image
3. **Distance Filtering**: Remove matches that are too close (likely same feature)
4. **Clustering**: Use DBSCAN to group matches with similar offsets
5. **Mask Generation**: Create binary masks highlighting forged regions
6. **Evaluation**: Compare with ground truth (if available)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/VedShashwat/CopyMoveForgeryDetection.git
cd CopyMoveForgeryDetection
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Process a Single Image

```bash
python src/detect.py --image path/to/image.jpg
```

With custom parameters:
```bash
python src/detect.py --image path/to/image.jpg --method orb --min_distance 60 --eps 25
```

### Evaluate on COVERAGE Dataset

```bash
python src/detect.py --dataset coverage --data_dir data/COVERAGE
```

### Evaluate on CoMoFoD Dataset

```bash
python src/detect.py --dataset comofod --data_dir data/comofod_small/CoMoFoD_small_v2 --method sift
```

### Command-Line Arguments

- `--image`: Path to a single image file
- `--dataset`: Dataset to evaluate (`coverage` or `comofod`)
- `--data_dir`: Path to dataset directory
- `--method`: Feature detection method (`sift`, `orb`, `akaze`) [default: sift]
- `--min_distance`: Minimum distance between matched keypoints [default: 50]
- `--eps`: DBSCAN epsilon parameter [default: 30]
- `--min_samples`: DBSCAN min_samples parameter [default: 3]
- `--max_images`: Maximum number of images to process
- `--no_visualize`: Do not show visualizations

## Datasets

### COVERAGE Dataset
- 100 pairs of original and forged images
- Various tampering types: rotation, scaling, translation, illumination, free-form, combination
- High-quality ground truth masks
- Path: `data/COVERAGE/`

### CoMoFoD Dataset (Small Version)
- Multiple forged images per original
- Different transformations applied
- Includes masks for evaluation
- Path: `data/comofod_small/CoMoFoD_small_v2/`

### Archive Dataset
- COCO-based annotations
- JSON format with detailed transformation information
- Path: `data/archive/`

## Output

The detection results include:

1. **Visualization Images**:
   - Original image
   - Matched keypoints with clusters
   - Detected forgery mask
   - Overlay of detected regions

2. **Metrics** (when ground truth available):
   - Precision
   - Recall
   - F1-Score
   - Accuracy

3. **JSON Results**:
   - Number of keypoints detected
   - Number of matches found
   - Number of clusters identified
   - Per-image metrics

## Algorithm Parameters

### Feature Detection
- `max_features`: Maximum number of features to detect (default: 5000)

### Matching
- `ratio_threshold`: Lowe's ratio test threshold (default: 0.75)

### Clustering (DBSCAN)
- `eps`: Maximum distance between samples in a cluster (default: 30)
- `min_samples`: Minimum samples in a cluster (default: 3)

### Post-Processing
- `min_distance`: Minimum distance between matched keypoints (default: 50)
- `region_size`: Size of region around keypoints for mask (default: 20)

## Performance Considerations

- **SIFT**: Slower but more accurate, good for complex transformations
- **ORB**: Faster, good for simple transformations
- **AKAZE**: Balanced speed and accuracy

Typical processing time:
- SIFT: 2-5 seconds per image
- ORB: 0.5-2 seconds per image
- AKAZE: 1-3 seconds per image

(Times vary based on image size and complexity)

## Evaluation Metrics

The system calculates the following metrics:

- **Precision**: TP / (TP + FP)
- **Recall**: TP / (TP + FN)
- **F1-Score**: 2 × (Precision × Recall) / (Precision + Recall)
- **Accuracy**: (TP + TN) / (TP + FP + FN + TN)

Where:
- TP: True Positives (correctly detected forgery pixels)
- FP: False Positives (incorrectly detected as forgery)
- FN: False Negatives (missed forgery pixels)
- TN: True Negatives (correctly identified as authentic)

## Future Enhancements

- [ ] Block-based detection methods
- [ ] DCT (Discrete Cosine Transform) based detection
- [ ] PCA (Principal Component Analysis) based detection
- [ ] GPU acceleration
- [ ] Real-time video forgery detection
- [ ] Web interface for easy usage

## References

- B. Wen, Y. Zhu, R. Subramanian, T. Ng, X. Shen, and S. Winkler, "COVERAGE - A Novel Database for Copy-Move Forgery Detection," IEEE ICIP, 2016.
- CoMoFoD Dataset: Copy-Move Forgery Detection benchmark
- Lowe, D.G., "Distinctive Image Features from Scale-Invariant Keypoints," IJCV, 2004.

## License

This project is for academic and research purposes only. The datasets are subject to their respective licenses.

## Contributors

- VedShashwat

## Acknowledgments

- COVERAGE Dataset creators
- CoMoFoD Dataset creators
- OpenCV community
