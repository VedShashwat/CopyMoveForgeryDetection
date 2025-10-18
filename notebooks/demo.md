# Copy-Move Forgery Detection - Demo Notebook

This notebook demonstrates how to use the copy-move forgery detection system.

## Setup

First, ensure all required packages are installed:

```bash
pip install -r requirements.txt
```

## Import Libraries

```python
import sys
sys.path.append('../src')

import cv2
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

from utils import (
    load_image, normalize_image, detect_and_compute, 
    match_features, filter_matches_by_distance, 
    cluster_matches, create_forgery_mask, 
    visualize_matches, calculate_metrics
)
from detect import detect_copy_move_forgery
```

## Example 1: Process a Single Image

```python
# Load and process an image
image_path = '../data/COVERAGE/image/1t.tif'  # Tampered image

result = detect_copy_move_forgery(
    image_path,
    method='sift',
    min_distance=50,
    eps=30,
    min_samples=3,
    visualize=True,
    save_output=True,
    output_dir='../results/demo'
)

if result:
    print(f"Forgery detected: {result['forgery_detected']}")
    print(f"Number of clusters found: {result['n_clusters']}")
```

## Example 2: Compare Different Methods

```python
methods = ['sift', 'orb', 'akaze']
image_path = '../data/COVERAGE/image/1t.tif'

results = {}
for method in methods:
    print(f"\n=== Testing {method.upper()} ===")
    result = detect_copy_move_forgery(
        image_path,
        method=method,
        visualize=False,
        save_output=False
    )
    if result:
        results[method] = result

# Compare results
for method, result in results.items():
    print(f"\n{method.upper()}:")
    print(f"  Keypoints: {result['n_keypoints']}")
    print(f"  Matches: {result['n_matches']}")
    print(f"  Clusters: {result['n_clusters']}")
```

## Example 3: Evaluate with Ground Truth

```python
from utils import load_coverage_dataset

# Load dataset
dataset = load_coverage_dataset('../data/COVERAGE')
print(f"Loaded {len(dataset)} images")

# Process first image
item = dataset[0]
print(f"\nProcessing image {item['id']}...")

# Detect forgery
result = detect_copy_move_forgery(
    item['tampered'],
    method='sift',
    visualize=False,
    save_output=False
)

if result and item['forged_mask']:
    # Load ground truth
    gt_mask = cv2.imread(item['forged_mask'], cv2.IMREAD_GRAYSCALE)
    
    # Calculate metrics
    metrics = calculate_metrics(result['mask'], gt_mask)
    
    print(f"\nEvaluation Metrics:")
    print(f"  Precision: {metrics['precision']:.3f}")
    print(f"  Recall: {metrics['recall']:.3f}")
    print(f"  F1 Score: {metrics['f1_score']:.3f}")
    print(f"  Accuracy: {metrics['accuracy']:.3f}")
```

## Example 4: Visualize Feature Matching Process

```python
# Load image
image_path = '../data/COVERAGE/image/1t.tif'
image = load_image(image_path)
gray = normalize_image(image)

# Detect features
keypoints, descriptors = detect_and_compute(gray, method='sift')
print(f"Detected {len(keypoints)} keypoints")

# Match features
matches = match_features(descriptors, descriptors, method='sift')
print(f"Found {len(matches)} raw matches")

# Filter matches
matches = filter_matches_by_distance(keypoints, matches, min_distance=50)
print(f"After filtering: {len(matches)} matches")

# Cluster matches
cluster_labels, offsets = cluster_matches(keypoints, matches, eps=30, min_samples=3)
n_clusters = len(np.unique(cluster_labels)) - (1 if -1 in cluster_labels else 0)
print(f"Identified {n_clusters} clusters")

# Visualize
vis_image = visualize_matches(gray, keypoints, matches, cluster_labels)
plt.figure(figsize=(12, 8))
plt.imshow(cv2.cvtColor(vis_image, cv2.COLOR_BGR2RGB))
plt.title(f'Feature Matching: {len(matches)} matches, {n_clusters} clusters')
plt.axis('off')
plt.show()
```

## Example 5: Parameter Tuning

```python
# Test different parameter combinations
image_path = '../data/COVERAGE/image/1t.tif'

# Test different min_distance values
min_distances = [30, 50, 70, 100]
for dist in min_distances:
    result = detect_copy_move_forgery(
        image_path,
        min_distance=dist,
        visualize=False,
        save_output=False
    )
    if result:
        print(f"min_distance={dist}: {result['n_matches']} matches, {result['n_clusters']} clusters")

# Test different DBSCAN eps values
eps_values = [20, 30, 40, 50]
for eps in eps_values:
    result = detect_copy_move_forgery(
        image_path,
        eps=eps,
        visualize=False,
        save_output=False
    )
    if result:
        print(f"eps={eps}: {result['n_matches']} matches, {result['n_clusters']} clusters")
```

## Tips for Better Results

1. **Feature Detection Method**:
   - Use SIFT for complex transformations (rotation, scaling)
   - Use ORB for speed
   - Use AKAZE for balanced performance

2. **Parameter Tuning**:
   - Increase `min_distance` for larger copied regions
   - Adjust `eps` based on image size (larger images need larger eps)
   - Increase `min_samples` to reduce false positives

3. **Image Preprocessing**:
   - Ensure good image quality
   - Consider resizing very large images for faster processing
   - Enhance contrast if needed

## Conclusion

This notebook demonstrated:
- Basic usage of the detection system
- Comparison of different feature detection methods
- Evaluation with ground truth masks
- Parameter tuning for better results

For more examples and batch processing, see the main `detect.py` script.
