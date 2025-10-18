#!/usr/bin/env python3
"""
Simple script to run copy-move forgery detection on example images
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from detect import detect_copy_move_forgery, evaluate_on_dataset


def main():
    """Run detection on sample images"""
    
    print("=" * 60)
    print("Copy-Move Forgery Detection - Quick Demo")
    print("=" * 60)
    
    # Check if COVERAGE dataset exists
    coverage_path = Path('data/COVERAGE')
    if coverage_path.exists():
        print("\n[1/3] Testing on COVERAGE dataset sample...")
        sample_image = coverage_path / 'image' / '1t.tif'
        
        if sample_image.exists():
            result = detect_copy_move_forgery(
                str(sample_image),
                method='sift',
                min_distance=50,
                eps=30,
                min_samples=3,
                visualize=True,
                save_output=True,
                output_dir='results/demo'
            )
            
            if result:
                print(f"\n✓ Detection completed!")
                print(f"  Keypoints detected: {result['n_keypoints']}")
                print(f"  Matches found: {result['n_matches']}")
                print(f"  Clusters identified: {result['n_clusters']}")
                print(f"  Forgery detected: {'Yes' if result['forgery_detected'] else 'No'}")
            else:
                print("\n✗ Detection failed!")
        else:
            print(f"  Sample image not found: {sample_image}")
    else:
        print(f"\n⚠ COVERAGE dataset not found at {coverage_path}")
        print("  Please download and extract the dataset first.")
    
    # Check if CoMoFoD dataset exists
    comofod_path = Path('data/comofod_small/CoMoFoD_small_v2')
    if comofod_path.exists():
        print("\n[2/3] Testing on CoMoFoD dataset sample...")
        
        # Find first forged image
        forged_images = list(comofod_path.glob('*_F.*'))
        if forged_images:
            sample_image = forged_images[0]
            print(f"  Processing: {sample_image.name}")
            
            result = detect_copy_move_forgery(
                str(sample_image),
                method='orb',  # Using ORB for speed
                min_distance=50,
                eps=30,
                min_samples=3,
                visualize=False,
                save_output=True,
                output_dir='results/demo'
            )
            
            if result:
                print(f"\n✓ Detection completed!")
                print(f"  Forgery detected: {'Yes' if result['forgery_detected'] else 'No'}")
            else:
                print("\n✗ Detection failed!")
        else:
            print("  No forged images found in dataset")
    else:
        print(f"\n⚠ CoMoFoD dataset not found at {comofod_path}")
    
    # Evaluation summary
    print("\n[3/3] Summary")
    print("-" * 60)
    results_dir = Path('results/demo')
    if results_dir.exists():
        result_files = list(results_dir.glob('*.png'))
        print(f"✓ Generated {len(result_files)} output files")
        print(f"  Check the 'results/demo' directory for visualizations")
    else:
        print("✗ No output files generated")
    
    print("\n" + "=" * 60)
    print("Demo completed!")
    print("\nNext steps:")
    print("  1. Check results in the 'results/demo' directory")
    print("  2. Try: python src/detect.py --help for more options")
    print("  3. See docs/QUICKSTART.md for detailed examples")
    print("=" * 60)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\nError: {e}")
        print("\nPlease ensure:")
        print("  1. All dependencies are installed: pip install -r requirements.txt")
        print("  2. Dataset files are in the correct directories")
        print("  3. You have write permissions for the results directory")
        sys.exit(1)
