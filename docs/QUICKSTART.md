# Quick Start Guide

## Prerequisites

- Python 3.8 or higher
- pip package manager

## Installation

1. **Clone the repository**:
```bash
git clone https://github.com/VedShashwat/CopyMoveForgeryDetection.git
cd CopyMoveForgeryDetection
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

## Quick Examples

### Example 1: Detect Forgery in a Single Image

```bash
cd src
python detect.py --image ../data/COVERAGE/image/1t.tif
```

This will:
- Detect copy-move forgery in the image
- Display visualization windows
- Save results to `../results/` directory

### Example 2: Batch Process COVERAGE Dataset

```bash
python detect.py --dataset coverage --data_dir ../data/COVERAGE --max_images 10
```

This will:
- Process first 10 images from COVERAGE dataset
- Calculate metrics using ground truth masks
- Save results and visualizations
- Generate a JSON file with evaluation results

### Example 3: Try Different Detection Methods

**SIFT (Recommended for accuracy)**:
```bash
python detect.py --image ../data/COVERAGE/image/1t.tif --method sift
```

**ORB (Faster)**:
```bash
python detect.py --image ../data/COVERAGE/image/1t.tif --method orb
```

**AKAZE (Balanced)**:
```bash
python detect.py --image ../data/COVERAGE/image/1t.tif --method akaze
```

### Example 4: Custom Parameters

```bash
python detect.py --image ../data/COVERAGE/image/1t.tif \
  --method sift \
  --min_distance 60 \
  --eps 25 \
  --min_samples 4
```

Parameters explained:
- `--min_distance 60`: Require matched keypoints to be at least 60 pixels apart
- `--eps 25`: DBSCAN clustering radius (smaller = tighter clusters)
- `--min_samples 4`: Minimum 4 matches to form a cluster

### Example 5: Evaluate on CoMoFoD Dataset

```bash
python detect.py --dataset comofod \
  --data_dir ../data/comofod_small/CoMoFoD_small_v2 \
  --method sift \
  --max_images 20
```

## Understanding the Output

### Console Output
```
Image shape: (512, 512)
Detecting keypoints using sift...
Detected 5243 keypoints
Matching features...
Found 8762 matches
Filtering matches by distance...
After filtering: 342 matches
Clustering matches...
Found 2 clusters
```

### Visual Output
The visualization includes 4 panels:
1. **Original Image**: The input image
2. **Matched Keypoints**: Shows detected matches colored by cluster
3. **Forgery Mask**: Binary mask of detected forged regions (white = forged)
4. **Forgery Overlay**: Original image with detected regions highlighted in red

### Metrics (if ground truth available)
```
Precision: 0.842
Recall: 0.756
F1: 0.797
Accuracy: 0.983
```

## Directory Structure After Running

```
CopyMoveForgeryDetection/
├── results/
│   ├── 1t_detection.png       # Visualization
│   ├── 1t_mask.png             # Binary mask
│   ├── coverage/               # Dataset-specific results
│   └── coverage_evaluation_sift.json
```

## Troubleshooting

### Issue: "No keypoints detected"
**Solution**: The image might be too uniform or low quality
- Try a different image
- Increase `max_features` parameter
- Try a different detection method

### Issue: "Not enough matches"
**Solution**: The parameters might be too restrictive
- Decrease `min_distance` (try 30-40)
- Increase `ratio_threshold` (default 0.75, try 0.8)

### Issue: "Too many false positives"
**Solution**: Make clustering more strict
- Increase `min_samples` (try 4-5)
- Decrease `eps` (try 20-25)

### Issue: "ImportError: No module named cv2"
**Solution**: OpenCV not properly installed
```bash
pip uninstall opencv-python opencv-contrib-python
pip install opencv-contrib-python
```

## Parameter Tuning Guide

### For Large Copied Regions
```bash
--min_distance 80 --eps 40 --min_samples 5
```

### For Small Copied Regions
```bash
--min_distance 30 --eps 20 --min_samples 2
```

### For Complex Transformations (rotation, scaling)
```bash
--method sift --min_distance 50 --eps 35
```

### For Simple Translations
```bash
--method orb --min_distance 40 --eps 25
```

## Next Steps

1. **Explore the demo notebook**: `notebooks/demo.md`
2. **Read the full documentation**: Check `README.md`
3. **Try different datasets**: Process your own images
4. **Tune parameters**: Experiment with different settings
5. **Contribute**: Submit issues or pull requests

## Getting Help

If you encounter issues:
1. Check this guide and the README
2. Review example commands above
3. Try different parameters
4. Check the dataset paths are correct
5. Ensure all dependencies are installed

## Tips for Best Results

1. **Start with default parameters** and adjust based on results
2. **Use SIFT** for most accurate detection
3. **Process a few images first** before batch processing
4. **Save your results** for later analysis
5. **Compare different methods** on the same image

Happy Forgery Detection! 🔍
