"""
Test script to demonstrate false positive filtering for repetitive patterns.
This creates a synthetic image with a brick wall pattern to test if the system
correctly identifies it as NOT a forgery.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

import cv2
import numpy as np
from detect import detect_copy_move_forgery

def create_brick_wall_pattern(width=800, height=600):
    """Create a synthetic brick wall pattern."""
    image = np.ones((height, width, 3), dtype=np.uint8) * 180  # Gray background
    
    brick_width = 100
    brick_height = 40
    mortar_thickness = 5
    
    # Draw bricks in a pattern
    for row in range(0, height, brick_height + mortar_thickness):
        offset = (brick_width // 2) if ((row // (brick_height + mortar_thickness)) % 2 == 1) else 0
        for col in range(-brick_width, width, brick_width + mortar_thickness):
            x1 = col + offset
            y1 = row
            x2 = x1 + brick_width
            y2 = y1 + brick_height
            
            # Draw brick with slight color variation
            color = np.random.randint(150, 190, 3).tolist()
            cv2.rectangle(image, (x1, y1), (x2, y2), color, -1)
            
            # Add texture
            for _ in range(20):
                tx = np.random.randint(x1, min(x2, width))
                ty = np.random.randint(y1, min(y2, height))
                if 0 <= tx < width and 0 <= ty < height:
                    image[ty, tx] = np.random.randint(140, 200, 3)
    
    return image

def create_real_forgery(width=800, height=600):
    """Create a synthetic image with actual copy-move forgery."""
    # Create base image with random noise
    image = np.random.randint(100, 200, (height, width, 3), dtype=np.uint8)
    
    # Add some objects
    cv2.circle(image, (200, 200), 60, (255, 100, 100), -1)
    cv2.rectangle(image, (400, 100), (500, 250), (100, 255, 100), -1)
    cv2.ellipse(image, (600, 400), (80, 50), 45, 0, 360, (100, 100, 255), -1)
    
    # Create a copy-move forgery by copying a region
    source_region = image[150:250, 150:250].copy()
    image[400:500, 500:600] = source_region  # Paste the copied region
    
    return image

def main():
    print("="*70)
    print("Testing False Positive Filtering for Repetitive Patterns")
    print("="*70)
    
    # Create test directory
    test_dir = Path("results/test_patterns")
    test_dir.mkdir(exist_ok=True, parents=True)
    
    # Test 1: Brick wall (should NOT detect forgery)
    print("\n[Test 1] Brick Wall Pattern (Repetitive Structure)")
    print("-"*70)
    brick_wall = create_brick_wall_pattern()
    brick_path = test_dir / "brick_wall.png"
    cv2.imwrite(str(brick_path), brick_wall)
    print(f"Created: {brick_path}")
    
    result1 = detect_copy_move_forgery(
        str(brick_path),
        method='sift',
        min_distance=30,
        visualize=False,
        save_output=True,
        output_dir=str(test_dir)
    )
    
    # Test 2: Real forgery (should detect)
    print("\n[Test 2] Image with Real Copy-Move Forgery")
    print("-"*70)
    forged_image = create_real_forgery()
    forged_path = test_dir / "real_forgery.png"
    cv2.imwrite(str(forged_path), forged_image)
    print(f"Created: {forged_path}")
    
    result2 = detect_copy_move_forgery(
        str(forged_path),
        method='sift',
        min_distance=30,
        visualize=False,
        save_output=True,
        output_dir=str(test_dir)
    )
    
    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"Brick Wall:    Forgery={'YES' if result1 and result1['forgery_detected'] else 'NO':<3} " +
          f"(Expected: NO)  {'✓ CORRECT' if not (result1 and result1['forgery_detected']) else '✗ WRONG'}")
    print(f"Real Forgery:  Forgery={'YES' if result2 and result2['forgery_detected'] else 'NO':<3} " +
          f"(Expected: YES) {'✓ CORRECT' if result2 and result2['forgery_detected'] else '✗ WRONG'}")
    print("="*70)
    print(f"\nCheck visualizations in: {test_dir}")

if __name__ == "__main__":
    main()
