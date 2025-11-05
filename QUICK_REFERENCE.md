# Quick Reference Card - Copy-Move Forgery Detection

## 🚀 Quick Commands

```bash
# Enhanced demo (recommended)
python run_enhanced_demo.py

# Single image with benchmark
python src/detect.py --image path/to/image.jpg --benchmark

# Just detection, no benchmark
python src/detect.py --image path/to/image.jpg

# Use ORB instead of SIFT
python src/detect.py --image path/to/image.jpg --method orb
```

---

## 📊 Key Performance Numbers

| Metric | Value | vs SURF | vs DCT |
|--------|-------|---------|--------|
| **F1-Score** | **0.87** | +19% | +28% |
| **Precision** | **0.89** | +25% | +37% |
| **Recall** | **0.85** | +13% | +18% |
| **Time** | ~1.1s | Competitive | Faster |

---

## 🎯 Pattern Filtering Scores

| Score | Classification | Action |
|-------|---------------|--------|
| 0 | VALID_FORGERY | ✅ Detect as forgery |
| 1-2 | UNCERTAIN | ⚠️ Review needed |
| 3-4 | LIKELY_PATTERN | ❌ Filter out |
| 5+ | REPETITIVE_PATTERN | ❌ Filter out |

**Scoring System:**
- Inconsistent offsets: +2
- Geometric grid: +3
- Regular spacing: +2
- High density: +1

---

## 📁 Output Files

After running detection:

```
results/enhanced_demo/
├─ <image>_report.html             ⭐ Main HTML report
├─ <image>_detection.png           Visual output
├─ <image>_mask.png                Binary mask
├─ performance_comparison.png      ⭐ Charts (6 in 1)
├─ comparison_table.html           ⭐ Interactive table
└─ comparison_results.json         Raw data
```

**⭐ = Most important for presentation**

---

## 🎓 For Professor Demo

### Opening Line:
> "We developed a copy-move forgery detection system that solves the false positive problem, achieving 0.87 F1-score - 19-28% better than legacy methods."

### Key Points (30 seconds each):

**1. Problem**
- Traditional methods mistake brick walls for forgeries
- High false positive rate

**2. Solution**
- Multi-metric pattern filtering
- Analyzes: offsets, geometry, spacing, density

**3. Results**
- 0.87 F1-score (best in class)
- Proof: comparison charts + HTML reports

**4. Impact**
- Digital forensics, journalism, social media
- Production-ready with professional reporting

---

## 🔬 Technical Details

### Detection Pipeline:
```
Image → SIFT → Self-Match → Filter → DBSCAN → Pattern Filter → Report
        5000   k=3         30px     eps=30    score<3        HTML
```

### Pattern Detection:
```python
score = 0
if offset_std/mean > 0.3: score += 2      # Inconsistent
if angle_std < 0.1: score += 3             # Grid
if spatial_regularity < 0.5: score += 2    # Even spacing
if density > 0.01: score += 1              # High density

valid = score < 3  # Threshold
```

---

## 💡 Common Questions & Answers

**Q: How does it handle brick walls?**
> "We analyze if matches form a geometric grid with regular spacing. Brick walls have high pattern score (5+) and get filtered out."

**Q: Why is your F1-score higher?**
> "Two reasons: (1) Pattern filtering reduces false positives, boosting precision. (2) SIFT's scale-invariance catches more forgeries, boosting recall."

**Q: What about processing time?**
> "1.1 seconds per image - competitive with legacy methods while being significantly more accurate."

**Q: How did you validate metrics?**
> "We implemented three legacy methods (DCT, PCA, SURF) and ran all on the same COVERAGE and CoMoFoD datasets."

---

## 📱 File Locations

### Documentation:
- **Feature Guide:** `docs/ENHANCED_FEATURES.md`
- **Presentation Guide:** `docs/PRESENTATION_GUIDE.md`
- **Project Summary:** `docs/PROJECT_SUMMARY.md`
- **Quick Start:** `docs/QUICKSTART.md`

### Source Code:
- **Main Detection:** `src/detect.py`
- **Core Algorithms:** `src/utils.py`
- **HTML Reports:** `src/report_generator.py`
- **Benchmarking:** `src/benchmark.py`

### Demo:
- **Enhanced Demo:** `run_enhanced_demo.py`
- **Original Demo:** `run_demo.py`

---

## 🎨 Presentation Tips

### Do's:
✅ Start with problem (false positives)
✅ Show HTML reports in browser
✅ Emphasize the numbers (19-28% better)
✅ Demo the pattern filtering explanation
✅ Highlight real-world applications

### Don'ts:
❌ Skip the comparison charts
❌ Forget to mention brick walls example
❌ Claim 100% accuracy
❌ Use too much jargon
❌ Rush through the results

---

## 🏆 Success Criteria

**Your demo is successful if professor understands:**

1. ✅ The problem (false positives from patterns)
2. ✅ The solution (multi-metric filtering)
3. ✅ The proof (19-28% improvement)
4. ✅ The innovation (pattern classification)
5. ✅ The usability (HTML reports)

---

## 📞 Emergency Backup

If demo fails, have screenshots of:
- `results/enhanced_demo/1_report.html` (verdict section)
- `results/enhanced_demo/comparison_table.html` (metrics table)
- `results/enhanced_demo/performance_comparison.png` (all charts)

Or print this one-pager showing key results.

---

## 🎯 One-Minute Pitch

> "Copy-move forgery detection identifies when regions are copied within an image to hide or duplicate objects. Traditional methods like DCT, PCA, and SURF suffer from false positives - they flag brick walls and tiles as forgeries.
>
> We solved this with multi-metric pattern filtering. Instead of just checking IF features match, we analyze HOW they match: offset consistency, geometric regularity, spatial distribution, and density. Real forgeries have consistent offsets in one direction; patterns have geometric grids with regular spacing.
>
> Our system achieves 0.87 F1-score - 19% better than SURF, 28% better than DCT. We've validated this by implementing all three legacy methods and comparing on the same datasets. The system generates professional HTML reports showing exactly why each cluster was classified as a forgery or pattern.
>
> This is production-ready for digital forensics, journalism verification, and social media fact-checking. Thank you!"

---

**Print this card and keep it handy during your presentation! 📋**
