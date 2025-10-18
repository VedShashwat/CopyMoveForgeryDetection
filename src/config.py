# Configuration file for Copy-Move Forgery Detection

# Feature Detection Parameters
FEATURE_METHOD = 'sift'  # Options: 'sift', 'orb', 'akaze'
MAX_FEATURES = 5000

# Feature Matching Parameters
RATIO_THRESHOLD = 0.75  # Lowe's ratio test threshold

# Distance Filtering Parameters
MIN_DISTANCE = 50  # Minimum distance between matched keypoints (pixels)

# DBSCAN Clustering Parameters
DBSCAN_EPS = 30  # Maximum distance between samples in a cluster
DBSCAN_MIN_SAMPLES = 3  # Minimum number of samples in a cluster

# Mask Generation Parameters
REGION_SIZE = 20  # Size of region around keypoints for mask generation

# Visualization Parameters
MAX_CLUSTERS_VISUALIZE = 3  # Maximum number of clusters to visualize

# Dataset Paths
COVERAGE_PATH = 'data/COVERAGE'
COMOFOD_PATH = 'data/comofod_small/CoMoFoD_small_v2'
ARCHIVE_PATH = 'data/archive'

# Output Paths
RESULTS_DIR = 'results'

# Processing Parameters
SAVE_VISUALIZATIONS = True
SHOW_VISUALIZATIONS = False
