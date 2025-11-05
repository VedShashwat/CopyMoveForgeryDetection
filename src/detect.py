import cv2
import argparse
import numpy as np
from pathlib import Path
import json
import matplotlib.pyplot as plt
from utils import (
    load_image, normalize_image, detect_and_compute, match_features,
    filter_matches_by_distance, cluster_matches, create_forgery_mask,
    visualize_matches, calculate_metrics, load_coverage_dataset,
    load_comofod_dataset
)


def detect_copy_move_forgery(image_path, method='sift', min_distance=30, 
                              eps=30, min_samples=3, visualize=True, 
                              save_output=True, output_dir='results', run_benchmark=False):
    """
    Detect copy-move forgery in an image using feature-based method.
    
    Args:
        image_path: Path to the image file
        method: Feature detection method ('sift', 'orb', 'akaze')
        min_distance: Minimum distance between matched keypoints
        eps: DBSCAN epsilon parameter
        min_samples: DBSCAN min_samples parameter
        visualize: Whether to show visualizations
        save_output: Whether to save output images
        output_dir: Directory to save output images
        run_benchmark: Whether to run performance comparison with legacy methods
    
    Returns:
        Dictionary containing detection results
    """
    import time
    start_time = time.time()
    
    # Read the image
    image = load_image(image_path)
    if image is None:
        print(f"Error: Could not read image at {image_path}")
        return None

    # Normalize the image
    gray_image = normalize_image(image)
    print(f"Image shape: {gray_image.shape}")

    # Detect and compute features
    print(f"Detecting keypoints using {method}...")
    keypoints, descriptors = detect_and_compute(gray_image, method)
    print(f"Detected {len(keypoints)} keypoints")

    if descriptors is None or len(keypoints) < 10:
        print("Not enough keypoints detected!")
        return None

    # Match features (self-matching)
    print("Matching features...")
    matches = match_features(descriptors, descriptors, method)
    print(f"Found {len(matches)} matches")

    # Filter matches by distance
    print("Filtering matches by distance...")
    matches = filter_matches_by_distance(keypoints, matches, min_distance)
    print(f"After filtering: {len(matches)} matches")

    if len(matches) < min_samples:
        print("Not enough matches after filtering!")
        return None

    # Cluster matches
    print("Clustering matches...")
    cluster_labels, offsets = cluster_matches(keypoints, matches, eps, min_samples)
    unique_labels = np.unique(cluster_labels)
    n_clusters = len(unique_labels) - (1 if -1 in unique_labels else 0)
    print(f"Found {n_clusters} clusters")

    # Analyze cluster validity (filter out repetitive patterns)
    print("Analyzing clusters for false positives...")
    from utils import analyze_cluster_validity
    validity_info = analyze_cluster_validity(keypoints, matches, cluster_labels)
    valid_clusters = validity_info['valid_clusters']
    n_valid = validity_info['n_valid']
    cluster_stats = validity_info['stats']
    
    print(f"Valid clusters after filtering: {n_valid}/{n_clusters}")
    if n_valid < n_clusters:
        print(f"  → Filtered out {n_clusters - n_valid} cluster(s) (likely repetitive patterns)")
        # Show why clusters were filtered
        for label, stats in cluster_stats.items():
            if not stats['is_valid']:
                reasons = ', '.join(stats['pattern_reasons'])
                print(f"     Cluster {label}: {stats['classification']} ({reasons})")
    
    # Create forgery masks for valid clusters only
    masks = []
    for label in valid_clusters:
        mask = create_forgery_mask(gray_image.shape, keypoints, matches, cluster_labels, label)
        masks.append((label, mask))

    # Combine all masks
    combined_mask = np.zeros_like(gray_image)
    for _, mask in masks:
        combined_mask = cv2.bitwise_or(combined_mask, mask)
    
    # Determine final verdict
    forgery_detected = n_valid > 0
    confidence = "HIGH" if n_valid >= 2 else "MEDIUM" if n_valid == 1 else "NONE"

    # Visualize results
    if visualize or save_output:
        # Create visualization
        vis_image = visualize_matches(gray_image, keypoints, matches, cluster_labels)
        
        # Create figure with multiple subplots
        fig = plt.figure(figsize=(16, 12))
        
        # Add main title with verdict
        verdict_text = "🔴 FORGERY DETECTED" if forgery_detected else "✓ NO FORGERY DETECTED"
        verdict_color = 'red' if forgery_detected else 'green'
        fig.suptitle(f'{verdict_text} (Confidence: {confidence})', 
                     fontsize=20, fontweight='bold', color=verdict_color)
        
        # Create subplots
        gs = fig.add_gridspec(2, 2, hspace=0.3, wspace=0.2)
        axes = [fig.add_subplot(gs[i, j]) for i in range(2) for j in range(2)]
        
        # Original image
        axes[0].imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        axes[0].set_title('Original Image', fontsize=14)
        axes[0].axis('off')
        
        # Matched keypoints
        axes[1].imshow(cv2.cvtColor(vis_image, cv2.COLOR_BGR2RGB))
        axes[1].set_title(f'Matched Keypoints\n({len(matches)} matches, {n_valid}/{n_clusters} valid clusters)', 
                         fontsize=14)
        axes[1].axis('off')
        
        # Forgery mask
        axes[2].imshow(combined_mask, cmap='hot')
        axes[2].set_title('Detected Forgery Mask', fontsize=14)
        axes[2].axis('off')
        
        # Overlay
        overlay = image.copy()
        overlay[combined_mask > 0] = [0, 0, 255]  # Red highlighting
        result = cv2.addWeighted(image, 0.7, overlay, 0.3, 0)
        axes[3].imshow(cv2.cvtColor(result, cv2.COLOR_BGR2RGB))
        axes[3].set_title('Forgery Overlay', fontsize=14)
        axes[3].axis('off')
        
        plt.tight_layout(rect=[0, 0, 1, 0.96])
        
        if save_output:
            # Create output directory
            output_path = Path(output_dir)
            output_path.mkdir(exist_ok=True, parents=True)
            
            # Save figure
            image_name = Path(image_path).stem
            output_file = output_path / f"{image_name}_detection.png"
            plt.savefig(output_file, dpi=150, bbox_inches='tight')
            print(f"Saved output to: {output_file}")
            
            # Save mask
            mask_file = output_path / f"{image_name}_mask.png"
            cv2.imwrite(str(mask_file), combined_mask)
        
        if visualize:
            plt.show()
        else:
            plt.close()
    
    # Generate HTML report if saving output
    if save_output:
        from report_generator import generate_html_report
        report_result = {
            'n_keypoints': len(keypoints),
            'n_matches': len(matches),
            'n_clusters': n_clusters,
            'n_valid_clusters': n_valid,
            'mask': combined_mask,
            'forgery_detected': forgery_detected,
            'confidence': confidence,
        }
        generate_html_report(image_path, report_result, output_dir, cluster_stats)
    
    # Print final verdict
    processing_time = time.time() - start_time
    
    print("\n" + "="*60)
    if forgery_detected:
        print(f"🔴 VERDICT: FORGERY DETECTED (Confidence: {confidence})")
        print(f"   → Found {n_valid} valid copied region(s)")
        if n_valid < n_clusters:
            print(f"   → Filtered {n_clusters - n_valid} false positive(s) (repetitive patterns)")
    else:
        print("✓ VERDICT: NO FORGERY DETECTED")
        print("   → Image appears to be authentic")
    print(f"   ⏱️  Processing time: {processing_time:.3f}s")
    print("="*60 + "\n")

    # Prepare result dictionary
    result = {
        'n_keypoints': len(keypoints),
        'n_matches': len(matches),
        'n_clusters': n_clusters,
        'n_valid_clusters': n_valid,
        'mask': combined_mask,
        'forgery_detected': forgery_detected,
        'confidence': confidence,
        'validity_info': validity_info,
        'processing_time': processing_time
    }
    
    # Run benchmark comparison if requested
    if run_benchmark and save_output:
        from benchmark import benchmark_comparison
        benchmark_comparison(image_path, result, output_dir)
    
    return result


def evaluate_on_dataset(dataset_name, data_dir, method='sift', max_images=None):
    """
    Evaluate forgery detection on a dataset.
    
    Args:
        dataset_name: Name of the dataset ('coverage' or 'comofod')
        data_dir: Path to the dataset directory
        method: Feature detection method
        max_images: Maximum number of images to process (None for all)
    
    Returns:
        Evaluation results
    """
    # Load dataset
    if dataset_name.lower() == 'coverage':
        dataset = load_coverage_dataset(data_dir)
    elif dataset_name.lower() == 'comofod':
        dataset = load_comofod_dataset(data_dir)
    else:
        raise ValueError(f"Unknown dataset: {dataset_name}")
    
    print(f"Loaded {len(dataset)} images from {dataset_name} dataset")
    
    if max_images:
        dataset = dataset[:max_images]
    
    results = []
    for i, item in enumerate(dataset):
        print(f"\n[{i+1}/{len(dataset)}] Processing {item['id']}...")
        
        # Detect forgery
        detection_result = detect_copy_move_forgery(
            item['tampered'], 
            method=method, 
            visualize=False, 
            save_output=True,
            output_dir=f'results/{dataset_name}'
        )
        
        if detection_result is None:
            print(f"Detection failed for {item['id']}")
            continue
        
        # Load ground truth mask if available
        gt_mask = None
        mask_path = item.get('forged_mask') or item.get('mask')
        if mask_path and Path(mask_path).exists():
            gt_mask = cv2.imread(mask_path, cv2.IMREAD_GRAYSCALE)
        
        # Calculate metrics
        metrics = None
        if gt_mask is not None:
            metrics = calculate_metrics(detection_result['mask'], gt_mask)
            print(f"  Precision: {metrics['precision']:.3f}, Recall: {metrics['recall']:.3f}, F1: {metrics['f1_score']:.3f}")
        
        results.append({
            'id': item['id'],
            'detection': detection_result,
            'metrics': metrics
        })
    
    # Calculate average metrics
    valid_results = [r for r in results if r['metrics'] is not None]
    if valid_results:
        avg_metrics = {
            'precision': np.mean([r['metrics']['precision'] for r in valid_results]),
            'recall': np.mean([r['metrics']['recall'] for r in valid_results]),
            'f1_score': np.mean([r['metrics']['f1_score'] for r in valid_results]),
            'accuracy': np.mean([r['metrics']['accuracy'] for r in valid_results])
        }
        print(f"\n=== Average Metrics ===")
        print(f"Precision: {avg_metrics['precision']:.3f}")
        print(f"Recall: {avg_metrics['recall']:.3f}")
        print(f"F1 Score: {avg_metrics['f1_score']:.3f}")
        print(f"Accuracy: {avg_metrics['accuracy']:.3f}")
    
    return results


def main():
    """
    Main function to detect copy-move forgery.
    """
    parser = argparse.ArgumentParser(description='Copy-Move Forgery Detection')
    parser.add_argument('--image', type=str, help='Path to a single image file')
    parser.add_argument('--dataset', type=str, choices=['coverage', 'comofod'], help='Dataset to evaluate')
    parser.add_argument('--data_dir', type=str, help='Path to dataset directory')
    parser.add_argument('--method', type=str, default='sift', choices=['sift', 'orb', 'akaze'], 
                        help='Feature detection method')
    parser.add_argument('--min_distance', type=int, default=30, help='Minimum distance between matched keypoints')
    parser.add_argument('--eps', type=int, default=30, help='DBSCAN epsilon parameter')
    parser.add_argument('--min_samples', type=int, default=3, help='DBSCAN min_samples parameter')
    parser.add_argument('--max_images', type=int, default=None, help='Maximum number of images to process')
    parser.add_argument('--no_visualize', action='store_true', help='Do not show visualizations')
    parser.add_argument('--benchmark', action='store_true', help='Run performance comparison with legacy methods')
    
    args = parser.parse_args()
    
    if args.image:
        # Process single image
        print(f"Processing single image: {args.image}")
        result = detect_copy_move_forgery(
            args.image, 
            method=args.method,
            min_distance=args.min_distance,
            eps=args.eps,
            min_samples=args.min_samples,
            visualize=not args.no_visualize,
            save_output=True,
            run_benchmark=args.benchmark
        )
        
        if result:
            print(f"\n=== Detection Results ===")
            print(f"Keypoints: {result['n_keypoints']}")
            print(f"Matches: {result['n_matches']}")
            print(f"Clusters: {result['n_clusters']}")
            print(f"Forgery Detected: {result['forgery_detected']}")
    
    elif args.dataset and args.data_dir:
        # Evaluate on dataset
        print(f"Evaluating on {args.dataset} dataset...")
        results = evaluate_on_dataset(
            args.dataset,
            args.data_dir,
            method=args.method,
            max_images=args.max_images
        )
        
        # Save results
        output_file = Path('results') / f"{args.dataset}_evaluation_{args.method}.json"
        output_file.parent.mkdir(exist_ok=True, parents=True)
        
        # Convert results to JSON-serializable format
        json_results = []
        for r in results:
            json_r = {
                'id': r['id'],
                'detection': {
                    'n_keypoints': r['detection']['n_keypoints'],
                    'n_matches': r['detection']['n_matches'],
                    'n_clusters': r['detection']['n_clusters'],
                    'forgery_detected': r['detection']['forgery_detected']
                } if r['detection'] else None,
                'metrics': r['metrics']
            }
            json_results.append(json_r)
        
        with open(output_file, 'w') as f:
            json.dump(json_results, f, indent=2)
        
        print(f"\nResults saved to: {output_file}")
    
    else:
        parser.print_help()
        print("\nExamples:")
        print("  # Process a single image")
        print("  python detect.py --image path/to/image.jpg")
        print("\n  # Evaluate on COVERAGE dataset")
        print("  python detect.py --dataset coverage --data_dir data/COVERAGE")
        print("\n  # Evaluate on CoMoFoD dataset with ORB features")
        print("  python detect.py --dataset comofod --data_dir data/comofod_small/CoMoFoD_small_v2 --method orb")


if __name__ == "__main__":
    main()
