"""
Unit tests for copy-move forgery detection utilities
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import unittest
import numpy as np
import cv2
from utils import (
    normalize_image, detect_and_compute, match_features,
    filter_matches_by_distance, cluster_matches, calculate_metrics
)


class TestUtils(unittest.TestCase):
    
    def setUp(self):
        """Create a simple test image"""
        self.test_image = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        self.gray_image = cv2.cvtColor(self.test_image, cv2.COLOR_BGR2GRAY)
    
    def test_normalize_image(self):
        """Test image normalization"""
        normalized = normalize_image(self.test_image)
        self.assertEqual(len(normalized.shape), 2)  # Should be grayscale
        self.assertEqual(normalized.shape, (100, 100))
    
    def test_detect_and_compute_sift(self):
        """Test SIFT feature detection"""
        keypoints, descriptors = detect_and_compute(self.gray_image, method='sift')
        self.assertIsNotNone(keypoints)
        self.assertTrue(hasattr(keypoints, '__iter__'))  # Check if iterable (tuple or list)
        self.assertGreater(len(keypoints), 0)  # Should detect some keypoints
    
    def test_detect_and_compute_orb(self):
        """Test ORB feature detection"""
        keypoints, descriptors = detect_and_compute(self.gray_image, method='orb')
        self.assertIsNotNone(keypoints)
        self.assertTrue(hasattr(keypoints, '__iter__'))  # Check if iterable (tuple or list)
        self.assertGreater(len(keypoints), 0)  # Should detect some keypoints
    
    def test_detect_and_compute_akaze(self):
        """Test AKAZE feature detection"""
        keypoints, descriptors = detect_and_compute(self.gray_image, method='akaze')
        self.assertIsNotNone(keypoints)
        self.assertTrue(hasattr(keypoints, '__iter__'))  # Check if iterable (tuple or list)
        self.assertGreater(len(keypoints), 0)  # Should detect some keypoints
    
    def test_match_features(self):
        """Test feature matching"""
        keypoints, descriptors = detect_and_compute(self.gray_image, method='sift')
        if descriptors is not None and len(descriptors) > 0:
            matches = match_features(descriptors, descriptors, method='sift')
            self.assertTrue(isinstance(matches, list) or hasattr(matches, '__iter__'))
    
    def test_calculate_metrics(self):
        """Test metric calculation"""
        # Create simple binary masks
        pred_mask = np.zeros((100, 100), dtype=np.uint8)
        pred_mask[25:75, 25:75] = 255
        
        gt_mask = np.zeros((100, 100), dtype=np.uint8)
        gt_mask[30:70, 30:70] = 255
        
        metrics = calculate_metrics(pred_mask, gt_mask)
        
        self.assertIsNotNone(metrics)
        self.assertIn('precision', metrics)
        self.assertIn('recall', metrics)
        self.assertIn('f1_score', metrics)
        self.assertIn('accuracy', metrics)
        
        # Check value ranges
        self.assertGreaterEqual(metrics['precision'], 0)
        self.assertLessEqual(metrics['precision'], 1)
        self.assertGreaterEqual(metrics['recall'], 0)
        self.assertLessEqual(metrics['recall'], 1)


class TestForgeryDetection(unittest.TestCase):
    
    def test_filter_matches_by_distance(self):
        """Test distance-based match filtering"""
        # Create mock keypoints
        kp1 = cv2.KeyPoint(10, 10, 1)
        kp2 = cv2.KeyPoint(15, 15, 1)  # Close
        kp3 = cv2.KeyPoint(100, 100, 1)  # Far
        keypoints = [kp1, kp2, kp3]
        
        # Create mock matches
        match1 = cv2.DMatch(0, 1, 0)  # Close match
        match2 = cv2.DMatch(0, 2, 0)  # Far match
        matches = [match1, match2]
        
        filtered = filter_matches_by_distance(keypoints, matches, min_distance=10)
        
        # Should keep only the far match
        self.assertEqual(len(filtered), 1)
    
    def test_cluster_matches(self):
        """Test match clustering"""
        # Create mock keypoints with similar offsets
        keypoints = [
            cv2.KeyPoint(10, 10, 1),
            cv2.KeyPoint(20, 20, 1),
            cv2.KeyPoint(30, 30, 1),
            cv2.KeyPoint(110, 10, 1),
            cv2.KeyPoint(120, 20, 1),
            cv2.KeyPoint(130, 30, 1),
        ]
        
        # Create matches with consistent offset
        matches = [
            cv2.DMatch(0, 3, 0),  # offset (100, 0)
            cv2.DMatch(1, 4, 0),  # offset (100, 0)
            cv2.DMatch(2, 5, 0),  # offset (100, 0)
        ]
        
        labels, offsets = cluster_matches(keypoints, matches, eps=5, min_samples=2)
        
        self.assertEqual(len(labels), len(matches))
        self.assertEqual(len(offsets), len(matches))


if __name__ == '__main__':
    unittest.main()
