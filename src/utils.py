import cv2
import numpy as np
import os
from pathlib import Path
import json
from scipy.io import loadmat
import matplotlib.pyplot as plt
from sklearn.cluster import DBSCAN


def load_image(image_path, grayscale=False):
    """
    Load an image from file.
    
    Args:
        image_path: Path to the image file
        grayscale: If True, convert to grayscale
    
    Returns:
        Loaded image
    """
    if grayscale:
        return cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    return cv2.imread(image_path)


def normalize_image(image):
    """
    Normalize the image to a standard size and format.
    """
    if len(image.shape) == 3:
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return image


def detect_and_compute(image, method='sift', max_features=5000):
    """
    Detect and compute features and keypoints.
    
    Args:
        image: Input grayscale image
        method: Feature detection method ('sift', 'orb', 'akaze')
        max_features: Maximum number of features to detect
    
    Returns:
        keypoints, descriptors
    """
    if method == 'sift':
        detector = cv2.SIFT_create(nfeatures=max_features)
    elif method == 'orb':
        detector = cv2.ORB_create(nfeatures=max_features)
    elif method == 'akaze':
        detector = cv2.AKAZE_create()
    else:
        raise ValueError(f"Unknown method: {method}")
        
    keypoints, descriptors = detector.detectAndCompute(image, None)
    return keypoints, descriptors


def match_features(desc1, desc2, method='sift', ratio_threshold=0.75):
    """
    Match features between two sets of descriptors using FLANN or BFMatcher.
    
    Args:
        desc1: First set of descriptors
        desc2: Second set of descriptors (can be same as desc1 for self-matching)
        method: Feature type ('sift', 'orb', 'akaze')
        ratio_threshold: Ratio test threshold for Lowe's ratio test
    
    Returns:
        List of good matches
    """
    if desc1 is None or desc2 is None or len(desc1) == 0 or len(desc2) == 0:
        return []
    
    # Check if this is self-matching
    is_self_match = desc1 is desc2 or (hasattr(desc1, 'shape') and hasattr(desc2, 'shape') 
                                        and desc1.shape == desc2.shape and np.array_equal(desc1, desc2))
    
    # Use k=3 for self-matching (skip the self-match), k=2 otherwise
    k = 3 if is_self_match else 2
    
    if method in ['sift', 'akaze']:
        # FLANN parameters for SIFT/AKAZE
        FLANN_INDEX_KDTREE = 1
        index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
        search_params = dict(checks=50)
        flann = cv2.FlannBasedMatcher(index_params, search_params)
        matches = flann.knnMatch(desc1, desc2, k=k)
    else:
        # BFMatcher for ORB
        bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=False)
        matches = bf.knnMatch(desc1, desc2, k=k)
    
    # Apply Lowe's ratio test
    good_matches = []
    for match_pair in matches:
        if is_self_match:
            # For self-matching: skip first match (self), use 2nd and 3rd
            if len(match_pair) >= 3:
                m, n = match_pair[1], match_pair[2]  # Use 2nd and 3rd matches
                if m.distance < ratio_threshold * n.distance:
                    good_matches.append(m)
        else:
            # For normal matching: use 1st and 2nd
            if len(match_pair) == 2:
                m, n = match_pair
                if m.distance < ratio_threshold * n.distance:
                    good_matches.append(m)
    
    return good_matches


def filter_matches_by_distance(keypoints, matches, min_distance=10):
    """
    Filter matches that are too close to each other (likely the same feature).
    
    Args:
        keypoints: List of keypoints
        matches: List of matches
        min_distance: Minimum Euclidean distance between matched keypoints
    
    Returns:
        Filtered matches
    """
    filtered_matches = []
    self_matches = 0
    too_close = 0
    
    for match in matches:
        # Skip self-matches (same keypoint matching itself)
        if match.queryIdx == match.trainIdx:
            self_matches += 1
            continue
            
        pt1 = keypoints[match.queryIdx].pt
        pt2 = keypoints[match.trainIdx].pt
        distance = np.sqrt((pt1[0] - pt2[0])**2 + (pt1[1] - pt2[1])**2)
        if distance >= min_distance:
            filtered_matches.append(match)
        else:
            too_close += 1
    
    print(f"  Self-matches removed: {self_matches}, Too close: {too_close}, Kept: {len(filtered_matches)}")
    return filtered_matches


def cluster_matches(keypoints, matches, eps=30, min_samples=3):
    """
    Cluster matches using DBSCAN to identify copied regions.
    
    Args:
        keypoints: List of keypoints
        matches: List of matches
        eps: Maximum distance between samples in the same cluster
        min_samples: Minimum number of samples in a cluster
    
    Returns:
        cluster_labels, offsets
    """
    if len(matches) == 0:
        return np.array([]), np.array([])
    
    # Calculate offsets (displacement vectors)
    offsets = []
    for match in matches:
        pt1 = keypoints[match.queryIdx].pt
        pt2 = keypoints[match.trainIdx].pt
        offset = (pt2[0] - pt1[0], pt2[1] - pt1[1])
        offsets.append(offset)
    
    offsets = np.array(offsets)
    
    # Cluster offsets using DBSCAN
    clustering = DBSCAN(eps=eps, min_samples=min_samples).fit(offsets)
    
    return clustering.labels_, offsets


def analyze_cluster_validity(keypoints, matches, cluster_labels, min_area=100, max_repetition_ratio=0.3):
    """
    Analyze clusters to filter out false positives from repetitive patterns.
    Uses advanced heuristics to detect brick walls, tiles, grids, and other regular patterns.
    
    Args:
        keypoints: List of keypoints
        matches: List of matches
        cluster_labels: Cluster labels from DBSCAN
        min_area: Minimum area of copied region (in pixels²)
        max_repetition_ratio: Max ratio of offset magnitude variance to mean (higher = more repetitive)
    
    Returns:
        Dictionary with cluster validity information
    """
    unique_labels = np.unique(cluster_labels)
    valid_clusters = []
    cluster_stats = {}
    
    for label in unique_labels:
        if label == -1:  # Skip noise
            continue
        
        # Get matches in this cluster
        cluster_mask = cluster_labels == label
        cluster_matches = [m for i, m in enumerate(matches) if cluster_mask[i]]
        
        if len(cluster_matches) == 0:
            continue
        
        # Calculate cluster statistics
        cluster_points = []
        offset_vectors = []
        offset_magnitudes = []
        offset_angles = []
        
        for match in cluster_matches:
            pt1 = keypoints[match.queryIdx].pt
            pt2 = keypoints[match.trainIdx].pt
            cluster_points.append(pt1)
            
            # Offset vector and magnitude
            dx = pt2[0] - pt1[0]
            dy = pt2[1] - pt1[1]
            offset_vectors.append([dx, dy])
            offset_mag = np.sqrt(dx**2 + dy**2)
            offset_magnitudes.append(offset_mag)
            
            # Offset angle (for detecting grid patterns)
            angle = np.arctan2(dy, dx)
            offset_angles.append(angle)
        
        cluster_points = np.array(cluster_points)
        offset_vectors = np.array(offset_vectors)
        offset_magnitudes = np.array(offset_magnitudes)
        offset_angles = np.array(offset_angles)
        
        # Calculate bounding box area
        if len(cluster_points) > 0:
            x_min, y_min = cluster_points.min(axis=0)
            x_max, y_max = cluster_points.max(axis=0)
            area = (x_max - x_min) * (y_max - y_min)
        else:
            area = 0
        
        # 1. Offset Consistency (original metric)
        offset_mean = offset_magnitudes.mean()
        offset_std = offset_magnitudes.std()
        repetition_score = offset_std / (offset_mean + 1e-6)
        
        # 2. Geometric Regularity Detection (NEW)
        # Check if offset vectors form a regular grid pattern
        angle_std = np.std(offset_angles)
        angle_consistency = angle_std < 0.1  # Very consistent angles = likely grid
        
        # 3. Spatial Distribution Analysis (NEW)
        # Calculate the distribution of source points
        # Repetitive patterns have evenly spaced source points
        if len(cluster_points) > 3:
            # Calculate pairwise distances between source points
            from scipy.spatial.distance import pdist
            pairwise_distances = pdist(cluster_points)
            dist_std = np.std(pairwise_distances)
            dist_mean = np.mean(pairwise_distances)
            spatial_regularity = dist_std / (dist_mean + 1e-6)
            
            # Low spatial regularity = points are evenly spaced = likely pattern
            is_spatially_regular = spatial_regularity < 0.5
        else:
            spatial_regularity = 1.0
            is_spatially_regular = False
        
        # 4. Density Check (NEW)
        # Repetitive patterns tend to have high match density
        if area > 0:
            density = len(cluster_matches) / area
            is_high_density = density > 0.01  # More than 1 match per 100 pixels²
        else:
            density = 0
            is_high_density = False
        
        # 5. Combined Pattern Detection Score (NEW)
        # Higher score = more likely to be a repetitive pattern
        pattern_score = 0
        pattern_reasons = []
        
        if repetition_score > max_repetition_ratio:
            pattern_score += 2
            pattern_reasons.append("inconsistent_offsets")
        
        if angle_consistency and len(cluster_matches) > 10:
            pattern_score += 3
            pattern_reasons.append("geometric_grid")
        
        if is_spatially_regular and len(cluster_matches) > 8:
            pattern_score += 2
            pattern_reasons.append("regular_spacing")
        
        if is_high_density and len(cluster_matches) > 15:
            pattern_score += 1
            pattern_reasons.append("high_density")
        
        # Validity criteria (ENHANCED)
        is_valid = (
            area >= min_area and  # Large enough region
            pattern_score < 3  # Not a repetitive pattern (threshold: 3 points)
        )
        
        # Classification
        if pattern_score >= 5:
            classification = "REPETITIVE_PATTERN"
        elif pattern_score >= 3:
            classification = "LIKELY_PATTERN"
        elif pattern_score >= 1:
            classification = "UNCERTAIN"
        else:
            classification = "VALID_FORGERY"
        
        cluster_stats[label] = {
            'num_matches': len(cluster_matches),
            'area': area,
            'density': density,
            'offset_mean': offset_mean,
            'offset_std': offset_std,
            'repetition_score': repetition_score,
            'angle_std': angle_std,
            'spatial_regularity': spatial_regularity,
            'pattern_score': pattern_score,
            'pattern_reasons': pattern_reasons,
            'classification': classification,
            'is_valid': is_valid
        }
        
        if is_valid:
            valid_clusters.append(label)
    
    return {
        'valid_clusters': valid_clusters,
        'stats': cluster_stats,
        'n_valid': len(valid_clusters),
        'n_total': len([l for l in unique_labels if l != -1])
    }


def create_forgery_mask(image_shape, keypoints, matches, cluster_labels, cluster_id, region_size=20):
    """
    Create a binary mask highlighting the forged region.
    
    Args:
        image_shape: Shape of the original image
        keypoints: List of keypoints
        matches: List of matches
        cluster_labels: Cluster labels from DBSCAN
        cluster_id: ID of the cluster to visualize
        region_size: Size of the region around each keypoint
    
    Returns:
        Binary mask
    """
    mask = np.zeros(image_shape[:2], dtype=np.uint8)
    
    for i, match in enumerate(matches):
        if cluster_labels[i] == cluster_id:
            # Mark both source and target regions
            pt1 = keypoints[match.queryIdx].pt
            pt2 = keypoints[match.trainIdx].pt
            
            cv2.circle(mask, (int(pt1[0]), int(pt1[1])), region_size, 255, -1)
            cv2.circle(mask, (int(pt2[0]), int(pt2[1])), region_size, 255, -1)
    
    # Apply morphological operations to smooth the mask
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15))
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    
    return mask


def visualize_matches(image, keypoints, matches, cluster_labels=None, max_clusters=3):
    """
    Visualize feature matches on the image.
    
    Args:
        image: Original image
        keypoints: List of keypoints
        matches: List of matches
        cluster_labels: Optional cluster labels
        max_clusters: Maximum number of clusters to visualize
    
    Returns:
        Visualization image
    """
    output = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR) if len(image.shape) == 2 else image.copy()
    
    if cluster_labels is None:
        # Draw all matches
        for match in matches:
            pt1 = keypoints[match.queryIdx].pt
            pt2 = keypoints[match.trainIdx].pt
            cv2.circle(output, (int(pt1[0]), int(pt1[1])), 5, (0, 255, 0), 2)
            cv2.circle(output, (int(pt2[0]), int(pt2[1])), 5, (0, 0, 255), 2)
            cv2.line(output, (int(pt1[0]), int(pt1[1])), (int(pt2[0]), int(pt2[1])), (255, 0, 0), 1)
    else:
        # Draw matches by cluster with different colors
        colors = [(0, 255, 0), (255, 0, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255), (0, 255, 255)]
        unique_labels = np.unique(cluster_labels)
        cluster_count = 0
        
        for label in unique_labels:
            if label == -1:  # Skip noise
                continue
            if cluster_count >= max_clusters:
                break
                
            color = colors[cluster_count % len(colors)]
            cluster_matches = [m for i, m in enumerate(matches) if cluster_labels[i] == label]
            
            for match in cluster_matches:
                pt1 = keypoints[match.queryIdx].pt
                pt2 = keypoints[match.trainIdx].pt
                cv2.circle(output, (int(pt1[0]), int(pt1[1])), 5, color, 2)
                cv2.circle(output, (int(pt2[0]), int(pt2[1])), 5, color, 2)
                cv2.line(output, (int(pt1[0]), int(pt1[1])), (int(pt2[0]), int(pt2[1])), color, 1)
            
            cluster_count += 1
    
    return output


def load_coverage_dataset(data_dir):
    """
    Load COVERAGE dataset information.
    
    Args:
        data_dir: Path to COVERAGE data directory
    
    Returns:
        List of dictionaries containing image paths and annotations
    """
    dataset = []
    image_dir = Path(data_dir) / "image"
    mask_dir = Path(data_dir) / "mask"
    label_dir = Path(data_dir) / "label"
    
    # Load labels
    tf_label = loadmat(label_dir / "TFlabel.mat")['TFlabel'].flatten()
    
    for i in range(1, 101):
        original_path = image_dir / f"{i}.tif"
        tampered_path = image_dir / f"{i}t.tif"
        
        if original_path.exists() and tampered_path.exists():
            dataset.append({
                'id': i,
                'original': str(original_path),
                'tampered': str(tampered_path),
                'copy_mask': str(mask_dir / f"{i}copy.tif"),
                'paste_mask': str(mask_dir / f"{i}paste.tif"),
                'forged_mask': str(mask_dir / f"{i}forged.tif"),
                'tampering_type': int(tf_label[i-1])
            })
    
    return dataset


def load_comofod_dataset(data_dir):
    """
    Load CoMoFoD dataset information.
    
    Args:
        data_dir: Path to CoMoFoD data directory
    
    Returns:
        List of dictionaries containing image paths
    """
    dataset = []
    data_path = Path(data_dir)
    
    # Get all original images (those ending with _O.png or _O.jpg)
    image_files = list(data_path.glob("*_O.*"))
    
    for original_path in image_files:
        # Extract base name (e.g., "064" from "064_O.png")
        base_name = original_path.stem.split('_')[0]
        
        # Find corresponding forged images
        forged_files = list(data_path.glob(f"{base_name}_F*.*"))
        
        for forged_path in forged_files:
            # Find corresponding mask
            mask_name = forged_path.stem.replace('_F', '_M') + forged_path.suffix
            mask_path = data_path / mask_name
            
            dataset.append({
                'id': forged_path.stem,
                'original': str(original_path),
                'tampered': str(forged_path),
                'mask': str(mask_path) if mask_path.exists() else None
            })
    
    return dataset


def calculate_metrics(predicted_mask, ground_truth_mask):
    """
    Calculate detection metrics.
    
    Args:
        predicted_mask: Predicted forgery mask (binary)
        ground_truth_mask: Ground truth mask (binary)
    
    Returns:
        Dictionary containing precision, recall, F1 score, and accuracy
    """
    if ground_truth_mask is None:
        return None
    
    # Ensure masks are binary
    predicted_mask = (predicted_mask > 127).astype(np.uint8)
    ground_truth_mask = (ground_truth_mask > 127).astype(np.uint8)
    
    # Calculate true positives, false positives, false negatives, true negatives
    tp = np.sum((predicted_mask == 1) & (ground_truth_mask == 1))
    fp = np.sum((predicted_mask == 1) & (ground_truth_mask == 0))
    fn = np.sum((predicted_mask == 0) & (ground_truth_mask == 1))
    tn = np.sum((predicted_mask == 0) & (ground_truth_mask == 0))
    
    # Calculate metrics
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1_score = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
    accuracy = (tp + tn) / (tp + fp + fn + tn) if (tp + fp + fn + tn) > 0 else 0
    
    return {
        'precision': precision,
        'recall': recall,
        'f1_score': f1_score,
        'accuracy': accuracy,
        'tp': tp,
        'fp': fp,
        'fn': fn,
        'tn': tn
    }
