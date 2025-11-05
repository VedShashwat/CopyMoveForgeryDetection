"""
Enhanced Demo Script for Copy-Move Forgery Detection
Showcases all new features: HTML reports, benchmarking, pattern filtering
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from detect import detect_copy_move_forgery

def main():
    print("="*80)
    print("🔍 COPY-MOVE FORGERY DETECTION - ENHANCED DEMO")
    print("="*80)
    print()
    
    # Find sample images
    data_dir = Path("data")
    
    # COVERAGE dataset
    coverage_samples = list((data_dir / "COVERAGE" / "image").glob("*.tif"))
    if coverage_samples:
        print("[1/2] Testing on COVERAGE dataset sample with full analysis...")
        print("-" * 80)
        
        sample = coverage_samples[0]
        result = detect_copy_move_forgery(
            str(sample),
            method='sift',
            min_distance=30,
            visualize=False,
            save_output=True,
            output_dir='results/enhanced_demo',
            run_benchmark=True  # Run performance comparison
        )
        
        if result:
            print(f"\n✅ Detection completed!")
            print(f"   📊 Check results/enhanced_demo/ for:")
            print(f"      • HTML report with interactive charts")
            print(f"      • Performance comparison with legacy methods")
            print(f"      • Visual detection outputs")
        print()
    
    # CoMoFoD dataset
    comofod_samples = list((data_dir / "comofod_small" / "CoMoFoD_small_v2").glob("*_F.png"))
    if comofod_samples:
        print("[2/2] Testing on CoMoFoD dataset sample...")
        print("-" * 80)
        
        sample = comofod_samples[0]
        result = detect_copy_move_forgery(
            str(sample),
            method='orb',
            min_distance=30,
            visualize=False,
            save_output=True,
            output_dir='results/enhanced_demo',
            run_benchmark=False  # Skip benchmark for second image
        )
        
        if result:
            print(f"\n✅ Detection completed!")
        print()
    
    print("="*80)
    print("✨ DEMO COMPLETED!")
    print("="*80)
    print()
    print("📁 Results saved in: results/enhanced_demo/")
    print()
    print("🌐 Open the HTML reports in your browser:")
    print("   • *_report.html - Individual detection reports")
    print("   • comparison_table.html - Performance comparison")
    print()
    print("📊 View performance charts:")
    print("   • performance_comparison.png - Visual comparison with legacy methods")
    print()
    print("🎯 Key Features Demonstrated:")
    print("   ✓ Advanced repetitive pattern filtering (brick walls, tiles)")
    print("   ✓ HTML reports with interactive visualizations")
    print("   ✓ Performance benchmarking against legacy methods")
    print("   ✓ Detailed cluster analysis with classification")
    print("   ✓ Clear forgery verdict with confidence levels")
    print()

if __name__ == "__main__":
    main()
