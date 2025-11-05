"""
HTML Report Generator for Copy-Move Forgery Detection
Generates comprehensive visual reports with charts and analysis
"""

import json
import base64
from io import BytesIO
from pathlib import Path
from datetime import datetime
import numpy as np
import cv2
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend


def generate_html_report(image_path, result, output_dir, cluster_stats=None):
    """
    Generate a comprehensive HTML report for detection results.
    
    Args:
        image_path: Path to the analyzed image
        result: Detection result dictionary
        output_dir: Directory to save the report
        cluster_stats: Detailed cluster statistics
    """
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True, parents=True)
    
    image_name = Path(image_path).stem
    report_file = output_path / f"{image_name}_report.html"
    
    # Load images
    original_img = cv2.imread(image_path)
    if original_img is None:
        print(f"Warning: Could not load image for report: {image_path}")
        return
    
    original_img_rgb = cv2.cvtColor(original_img, cv2.COLOR_BGR2RGB)
    
    # Create visualization images
    mask_img = result.get('mask', np.zeros_like(original_img[:,:,0]))
    
    # Create overlay
    overlay = original_img.copy()
    overlay[mask_img > 0] = [0, 0, 255]  # Red
    overlay_img = cv2.addWeighted(original_img, 0.7, overlay, 0.3, 0)
    overlay_img_rgb = cv2.cvtColor(overlay_img, cv2.COLOR_BGR2RGB)
    
    # Convert images to base64
    def img_to_base64(img):
        if len(img.shape) == 2:  # Grayscale
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
        buffer = BytesIO()
        plt.imsave(buffer, img, format='png')
        buffer.seek(0)
        return base64.b64encode(buffer.read()).decode()
    
    original_b64 = img_to_base64(original_img_rgb)
    mask_b64 = img_to_base64(mask_img)
    overlay_b64 = img_to_base64(overlay_img_rgb)
    
    # Create cluster analysis chart
    if cluster_stats:
        cluster_chart_b64 = create_cluster_analysis_chart(cluster_stats)
    else:
        cluster_chart_b64 = ""
    
    # Get result metrics
    forgery_detected = result.get('forgery_detected', False)
    confidence = result.get('confidence', 'NONE')
    n_keypoints = result.get('n_keypoints', 0)
    n_matches = result.get('n_matches', 0)
    n_clusters = result.get('n_clusters', 0)
    n_valid = result.get('n_valid_clusters', 0)
    
    # Generate HTML
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Copy-Move Forgery Detection Report - {image_name}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: 'Georgia', 'Times New Roman', serif;
            background: #f5f5f5;
            padding: 20px;
            color: #2c3e50;
            line-height: 1.6;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border: 1px solid #ddd;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .header {{
            background: #2c3e50;
            color: white;
            padding: 30px 40px;
            border-bottom: 4px solid {'#c0392b' if forgery_detected else '#27ae60'};
        }}
        .header h1 {{
            font-size: 1.8em;
            font-weight: normal;
            margin-bottom: 5px;
            letter-spacing: 0.5px;
        }}
        .header .subtitle {{
            font-size: 0.9em;
            opacity: 0.8;
            font-style: italic;
        }}
        .report-info {{
            background: #ecf0f1;
            padding: 15px 40px;
            border-bottom: 1px solid #bdc3c7;
            font-family: 'Courier New', monospace;
            font-size: 0.85em;
        }}
        .report-info table {{
            width: 100%;
        }}
        .report-info td {{
            padding: 3px 0;
        }}
        .report-info td:first-child {{
            font-weight: bold;
            width: 150px;
        }}
        .verdict-section {{
            padding: 30px 40px;
            border-bottom: 2px solid #ecf0f1;
            background: {'#fdeaea' if forgery_detected else '#eafde7'};
        }}
        .verdict {{
            font-size: 1.5em;
            font-weight: bold;
            margin-bottom: 10px;
            color: {'#c0392b' if forgery_detected else '#27ae60'};
            text-transform: uppercase;
            letter-spacing: 2px;
        }}
        .confidence {{
            font-size: 1.1em;
            color: #7f8c8d;
            margin-bottom: 15px;
        }}
        .verdict-note {{
            background: white;
            border-left: 4px solid {'#c0392b' if forgery_detected else '#27ae60'};
            padding: 15px;
            margin-top: 15px;
            font-size: 0.95em;
        }}
        .content {{
            padding: 30px 40px;
        }}
        .section {{
            margin-bottom: 40px;
        }}
        .section h2 {{
            font-size: 1.4em;
            color: #2c3e50;
            border-bottom: 2px solid #3498db;
            padding-bottom: 8px;
            margin-bottom: 20px;
            font-weight: normal;
        }}
        .metrics-table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
            font-family: 'Courier New', monospace;
        }}
        .metrics-table th {{
            background: #34495e;
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: normal;
            border: 1px solid #2c3e50;
        }}
        .metrics-table td {{
            padding: 10px 12px;
            border: 1px solid #ddd;
            background: #fff;
        }}
        .metrics-table tr:nth-child(even) td {{
            background: #f9f9f9;
        }}
        .metrics-table .metric-name {{
            font-weight: bold;
            width: 200px;
        }}
        .images-section {{
            margin-bottom: 30px;
        }}
        .image-container {{
            margin-bottom: 25px;
            border: 1px solid #ddd;
            padding: 15px;
            background: #fafafa;
        }}
        .image-container h3 {{
            font-size: 1.1em;
            color: #34495e;
            margin-bottom: 10px;
            font-weight: normal;
            border-bottom: 1px solid #ddd;
            padding-bottom: 5px;
        }}
        .image-container img {{
            width: 100%;
            border: 1px solid #ccc;
            display: block;
        }}
        .cluster-table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
            font-size: 0.9em;
        }}
        .cluster-table th {{
            background: #34495e;
            color: white;
            padding: 10px;
            text-align: left;
            font-weight: normal;
            border: 1px solid #2c3e50;
        }}
        .cluster-table td {{
            padding: 8px 10px;
            border: 1px solid #ddd;
            background: #fff;
        }}
        .cluster-table tr:nth-child(even) td {{
            background: #f9f9f9;
        }}
        .status-valid {{
            color: #27ae60;
            font-weight: bold;
        }}
        .status-filtered {{
            color: #e67e22;
            font-weight: bold;
        }}
        .status-uncertain {{
            color: #f39c12;
            font-weight: bold;
        }}
        .pattern-score {{
            font-family: 'Courier New', monospace;
            background: #ecf0f1;
            padding: 2px 6px;
            border-radius: 3px;
        }}
        .footer {{
            background: #2c3e50;
            color: white;
            padding: 20px 40px;
            text-align: center;
            font-size: 0.85em;
            border-top: 4px solid #3498db;
        }}
        .footer a {{
            color: #3498db;
            text-decoration: none;
        }}
        .note {{
            background: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 12px;
            margin: 15px 0;
            font-size: 0.9em;
        }}
        .chart-container {{
            margin: 20px 0;
            border: 1px solid #ddd;
            padding: 10px;
            background: white;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Copy-Move Forgery Detection Report</h1>
            <div class="subtitle">Advanced Pattern Recognition with Multi-Metric Analysis</div>
        </div>
        
        <div class="report-info">
            <table>
                <tr>
                    <td>Image File:</td>
                    <td>{Path(image_path).name}</td>
                </tr>
                <tr>
                    <td>Image Path:</td>
                    <td>{image_path}</td>
                </tr>
                <tr>
                    <td>Report Generated:</td>
                    <td>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</td>
                </tr>
                <tr>
                    <td>Analysis Method:</td>
                    <td>SIFT Feature Detection + DBSCAN Clustering + Pattern Filtering</td>
                </tr>
            </table>
        </div>
        
        <div class="verdict-section">
            <div class="verdict">
                {'Forgery Detected' if forgery_detected else 'No Forgery Detected'}
            </div>
            <div class="confidence">
                Confidence Level: {confidence}
            </div>
            <div class="verdict-note">
                <strong>Analysis Summary:</strong> {'This image contains suspicious regions that match the characteristics of copy-move forgery. The detected clusters have been validated using multi-metric pattern analysis to filter out false positives from repetitive patterns.' if forgery_detected else 'No significant evidence of copy-move manipulation was found in this image. All detected feature matches were classified as natural repetitive patterns or insufficient to indicate forgery.'}
            </div>
        </div>
        
        <div class="content">
            <div class="section">
                <h2>1. Detection Metrics</h2>
                <table class="metrics-table">
                    <thead>
                        <tr>
                            <th class="metric-name">Metric</th>
                            <th>Value</th>
                            <th>Description</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td class="metric-name">Keypoints Detected</td>
                            <td><strong>{n_keypoints}</strong></td>
                            <td>SIFT interest points found in the image</td>
                        </tr>
                        <tr>
                            <td class="metric-name">Feature Matches</td>
                            <td><strong>{n_matches}</strong></td>
                            <td>Self-similar feature correspondences (distance threshold: 30px)</td>
                        </tr>
                        <tr>
                            <td class="metric-name">Clusters Formed</td>
                            <td><strong>{n_clusters}</strong></td>
                            <td>Spatial groupings using DBSCAN (eps=30, min_samples=3)</td>
                        </tr>
                        <tr>
                            <td class="metric-name">Valid Clusters</td>
                            <td><strong>{n_valid}</strong></td>
                            <td>Clusters classified as potential forgery (pattern score &lt; 3)</td>
                        </tr>
                        <tr>
                            <td class="metric-name">Filtered Clusters</td>
                            <td><strong>{n_clusters - n_valid}</strong></td>
                            <td>Clusters rejected as repetitive patterns (pattern score ≥ 3)</td>
                        </tr>
                    </tbody>
                </table>
            </div>
            
            <div class="section">
                <h2>2. Visual Analysis</h2>
                <div class="images-section">
                    <div class="image-container">
                        <h3>2.1 Original Image</h3>
                        <img src="data:image/png;base64,{original_b64}" alt="Original Image">
                        <p style="margin-top: 8px; font-size: 0.9em; color: #7f8c8d;">Input image as provided for analysis.</p>
                    </div>
                    
                    <div class="image-container">
                        <h3>2.2 Detection Mask</h3>
                        <img src="data:image/png;base64,{mask_b64}" alt="Detection Mask">
                        <p style="margin-top: 8px; font-size: 0.9em; color: #7f8c8d;">Binary mask showing regions classified as forgery (white = suspicious, black = clean).</p>
                    </div>
                    
                    <div class="image-container">
                        <h3>2.3 Forgery Overlay</h3>
                        <img src="data:image/png;base64,{overlay_b64}" alt="Forgery Overlay">
                        <p style="margin-top: 8px; font-size: 0.9em; color: #7f8c8d;">Detected forgery regions overlaid in red (30% opacity) on the original image.</p>
                    </div>
                </div>
            </div>
            
            {generate_cluster_section(cluster_stats, cluster_chart_b64) if cluster_stats else ''}
        </div>
        
        <div class="footer">
            <p><strong>Copy-Move Forgery Detection System</strong> | Multi-Metric Pattern Analysis Engine</p>
            <p style="margin-top: 8px; opacity: 0.8;">SIFT-based Feature Detection • DBSCAN Clustering • Advanced Pattern Filtering</p>
            <p style="margin-top: 8px; font-size: 0.8em;">For research and educational purposes. Results should be verified by forensic experts.</p>
        </div>
    </div>
</body>
</html>
"""
    
    # Write HTML file
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"📄 HTML report generated: {report_file}")
    return report_file


def generate_cluster_section(cluster_stats, chart_b64):
    """Generate HTML for cluster analysis section."""
    if not cluster_stats:
        return ""
    
    rows = ""
    for label, stats in cluster_stats.items():
        classification = stats.get('classification', 'UNKNOWN')
        is_valid = stats.get('is_valid', False)
        
        # Determine status class
        if is_valid:
            status_class = 'status-valid'
            status_text = 'VALID'
        elif 'PATTERN' in classification:
            status_class = 'status-filtered'
            status_text = 'FILTERED'
        else:
            status_class = 'status-uncertain'
            status_text = 'UNCERTAIN'
        
        rows += f"""
        <tr>
            <td>{label}</td>
            <td>{stats.get('num_matches', 0)}</td>
            <td>{stats.get('area', 0):.1f}</td>
            <td>{stats.get('repetition_score', 0):.3f}</td>
            <td><span class="pattern-score">{stats.get('pattern_score', 0)}</span></td>
            <td>{classification.replace('_', ' ')}</td>
            <td class="{status_class}">{status_text}</td>
        </tr>
        """
    
    chart_html = f'<div class="chart-container"><img src="data:image/png;base64,{chart_b64}" style="width: 100%;"></div>' if chart_b64 else ''
    
    return f"""
    <div class="section">
        <h2>3. Cluster Analysis</h2>
        <p style="margin-bottom: 15px; font-size: 0.95em;">
            Each cluster is analyzed for repetitive patterns using five independent heuristics:
            offset consistency, geometric regularity, spatial distribution, density analysis, and combined pattern scoring.
            Clusters with pattern score ≥ 3 are classified as natural repetitive patterns and filtered out.
        </p>
        
        <div class="note">
            <strong>Pattern Score Interpretation:</strong><br>
            • Score 0-2: Likely forgery (VALID)<br>
            • Score 3-4: Likely repetitive pattern (FILTERED)<br>
            • Score 5+: Definite repetitive pattern (FILTERED)
        </div>
        
        <table class="cluster-table">
            <thead>
                <tr>
                    <th>Cluster</th>
                    <th>Matches</th>
                    <th>Area (px²)</th>
                    <th>Rep. Score</th>
                    <th>Pattern Score</th>
                    <th>Classification</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
                {rows}
            </tbody>
        </table>
        {chart_html}
    </div>
    """


def create_cluster_analysis_chart(cluster_stats):
    """Create a chart showing cluster analysis metrics."""
    if not cluster_stats:
        return ""
    
    # Set professional style
    plt.style.use('seaborn-v0_8-darkgrid')
    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    fig.patch.set_facecolor('white')
    fig.suptitle('Cluster Pattern Analysis Metrics', fontsize=14, fontweight='bold', y=0.995)
    
    labels = list(cluster_stats.keys())
    
    # Colors based on validity
    colors = ['#27ae60' if stats['is_valid'] else '#e74c3c' for stats in cluster_stats.values()]
    
    # 1. Number of matches per cluster
    matches = [stats['num_matches'] for stats in cluster_stats.values()]
    axes[0, 0].bar(labels, matches, color=colors, alpha=0.8, edgecolor='black', linewidth=0.5)
    axes[0, 0].set_title('Feature Matches per Cluster', fontsize=11, pad=10)
    axes[0, 0].set_xlabel('Cluster ID', fontsize=9)
    axes[0, 0].set_ylabel('Number of Matches', fontsize=9)
    axes[0, 0].grid(axis='y', alpha=0.3, linestyle='--')
    axes[0, 0].set_axisbelow(True)
    
    # 2. Area vs Repetition Score
    areas = [stats['area'] for stats in cluster_stats.values()]
    rep_scores = [stats['repetition_score'] for stats in cluster_stats.values()]
    for i, (area, score, color, label) in enumerate(zip(areas, rep_scores, colors, labels)):
        axes[0, 1].scatter(area, score, c=color, s=120, alpha=0.7, edgecolors='black', linewidth=0.5)
        axes[0, 1].annotate(label, (area, score), fontsize=8, ha='center', va='bottom')
    axes[0, 1].set_title('Spatial Coverage vs. Repetition', fontsize=11, pad=10)
    axes[0, 1].set_xlabel('Area (px²)', fontsize=9)
    axes[0, 1].set_ylabel('Repetition Score', fontsize=9)
    axes[0, 1].axhline(y=0.3, color='#f39c12', linestyle='--', linewidth=1.5, label='Threshold (0.3)', alpha=0.7)
    axes[0, 1].legend(fontsize=8, loc='best')
    axes[0, 1].grid(alpha=0.3, linestyle='--')
    
    # 3. Pattern Score
    pattern_scores = [stats.get('pattern_score', 0) for stats in cluster_stats.values()]
    axes[1, 0].bar(labels, pattern_scores, color=colors, alpha=0.8, edgecolor='black', linewidth=0.5)
    axes[1, 0].set_title('Pattern Detection Score', fontsize=11, pad=10)
    axes[1, 0].set_xlabel('Cluster ID', fontsize=9)
    axes[1, 0].set_ylabel('Pattern Score', fontsize=9)
    axes[1, 0].axhline(y=3, color='#f39c12', linestyle='--', linewidth=1.5, label='Threshold (3)', alpha=0.7)
    axes[1, 0].legend(fontsize=8, loc='best')
    axes[1, 0].grid(axis='y', alpha=0.3, linestyle='--')
    axes[1, 0].set_axisbelow(True)
    
    # 4. Classification distribution
    classifications = {}
    for stats in cluster_stats.values():
        cls = stats.get('classification', 'UNKNOWN').replace('_', ' ')
        classifications[cls] = classifications.get(cls, 0) + 1
    
    pie_colors = {'VALID FORGERY': '#27ae60', 'LIKELY PATTERN': '#e74c3c', 
                  'REPETITIVE PATTERN': '#c0392b', 'UNCERTAIN': '#f39c12'}
    colors_list = [pie_colors.get(k, '#95a5a6') for k in classifications.keys()]
    
    wedges, texts, autotexts = axes[1, 1].pie(classifications.values(), labels=classifications.keys(), 
                                               autopct='%1.0f%%', colors=colors_list, startangle=90,
                                               textprops={'fontsize': 9})
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontweight('bold')
    axes[1, 1].set_title('Classification Distribution', fontsize=11, pad=10)
    
    plt.tight_layout()
    
    # Convert to base64
    buffer = BytesIO()
    plt.savefig(buffer, format='png', dpi=120, bbox_inches='tight', facecolor='white')
    buffer.seek(0)
    plt.close()
    
    return base64.b64encode(buffer.read()).decode()
