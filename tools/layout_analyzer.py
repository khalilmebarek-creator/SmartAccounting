"""
أداة تحليل تخطيط الشاشات باستخدام OpenCV + pytesseract
تكشف: تداخل العناصر، عناوين خانات مش فوق الخانات، جداول مش متناسقة
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import cv2
import numpy as np
import pytesseract
from PIL import Image

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


def analyze_layout(screenshot_path):
    """Analyze a single screenshot for layout issues."""
    img = cv2.imread(str(screenshot_path))
    if img is None:
        return {"error": f"Cannot read: {screenshot_path}"}

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    h, w = gray.shape
    issues = []

    # 1. Detect text regions with OCR
    data = pytesseract.image_to_data(gray, output_type=pytesseract.Output.DICT,
                                      config="--psm 11")
    texts = []
    for i in range(len(data["text"])):
        txt = data["text"][i].strip()
        # Filter: skip single chars, table separators, low confidence
        if (txt and len(txt) > 1 and data["conf"][i] > 40
                and txt not in ("|", ".", ",", ":", ";", "-", "_", "oOo", "ooo", "ss")):
            texts.append({
                "text": txt,
                "x": data["left"][i],
                "y": data["top"][i],
                "w": data["width"][i],
                "h": data["height"][i],
                "conf": data["conf"][i],
            })

    # 2. Detect overlapping text regions (ignore tiny artifacts)
    for i in range(len(texts)):
        for j in range(i + 1, len(texts)):
            a, b = texts[i], texts[j]
            # Check if they overlap
            overlap_x = max(0, min(a["x"] + a["w"], b["x"] + b["w"]) - max(a["x"], b["x"]))
            overlap_y = max(0, min(a["y"] + a["h"], b["y"] + b["h"]) - max(a["y"], b["y"]))
            if overlap_x > 5 and overlap_y > 5:  # ignore tiny overlaps
                area = overlap_x * overlap_y
                a_area = a["w"] * a["h"]
                b_area = b["w"] * b["h"]
                if a_area > 100 and b_area > 100:  # ignore tiny regions
                    overlap_pct = area / min(a_area, b_area) * 100
                    if overlap_pct > 30:
                        issues.append({
                            "type": "overlap",
                            "severity": "HIGH" if overlap_pct > 60 else "MEDIUM",
                            "detail": f"'{a['text']}' overlaps '{b['text']}' by {overlap_pct:.0f}%",
                            "region": {"x1": a["x"], "y1": a["y"], "x2": b["x"], "y2": b["y"]},
                        })

    # 3. Detect horizontal lines (table separators)
    edges = cv2.Canny(gray, 50, 150)
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, 100, minLineLength=w * 0.2, maxLineGap=10)
    h_lines = []
    if lines is not None:
        for line in lines:
            coords = line.flatten()
            x1, y1, x2, y2 = int(coords[0]), int(coords[1]), int(coords[2]), int(coords[3])
            if abs(y1 - y2) < 5:  # horizontal
                h_lines.append({"x1": x1, "y1": y1, "x2": x2, "y2": y2})
    h_lines.sort(key=lambda l: l["y1"])

    # Check table alignment (horizontal lines should be evenly spaced)
    # Filter out 1-2px lines (they are table borders, not rows)
    h_lines = [l for l in h_lines if (l["y2"] - l["y1"]) < 3 and (l["x2"] - l["x1"]) > w * 0.1]
    if len(h_lines) >= 3:
        gaps = [h_lines[i + 1]["y1"] - h_lines[i]["y1"] for i in range(len(h_lines) - 1)]
        gaps = [g for g in gaps if g > 10]  # ignore tiny gaps (borders)
        if len(gaps) >= 2:
            avg_gap = np.mean(gaps)
            for i, gap in enumerate(gaps):
                deviation = abs(gap - avg_gap) / avg_gap * 100 if avg_gap > 0 else 0
                if deviation > 40:
                    issues.append({
                        "type": "table_misalignment",
                        "severity": "MEDIUM",
                        "detail": f"Row {i + 1} height ({gap}px) deviates {deviation:.0f}% from avg ({avg_gap:.0f}px)",
                        "region": {"y": h_lines[i]["y1"]},
                    })

    # 4. Detect vertical alignment issues
    # Group texts by approximate x position (should form columns)
    x_positions = [t["x"] for t in texts]
    if len(x_positions) >= 5:
        # Find clusters of x positions (columns)
        x_sorted = sorted(set(x_positions))
        columns = []
        current_col = [x_sorted[0]]
        for x in x_sorted[1:]:
            if x - current_col[-1] < 20:  # within 20px = same column
                current_col.append(x)
            else:
                columns.append(np.mean(current_col))
                current_col = [x]
        columns.append(np.mean(current_col))

        # Check if labels are roughly aligned with their column
        for t in texts:
            col_distances = [abs(t["x"] - c) for c in columns]
            if col_distances:
                min_dist = min(col_distances)
                if min_dist > 30:  # 30px off from nearest column
                    issues.append({
                        "type": "alignment",
                        "severity": "LOW",
                        "detail": f"'{t['text']}' is {min_dist:.0f}px from nearest column",
                        "region": {"x": t["x"], "y": t["y"]},
                    })

    # 5. Detect empty/very tall regions (potential spacing issues)
    # Only flag truly excessive blank space (not normal padding)
    _, binary = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    large_gaps = []
    for cnt in contours:
        x, y, cw, ch = cv2.boundingRect(cnt)
        if ch > h * 0.4 and cw > w * 0.4 and ch * cw > h * w * 0.15:  # >15% of screen
            large_gaps.append({"x": x, "y": y, "w": cw, "h": ch})
            if len(large_gaps) >= 2:
                break

    if large_gaps:
        issues.append({
            "type": "large_blank_area",
            "severity": "INFO",
            "detail": f"Found {len(large_gaps)} large blank region(s) - potential wasted space",
            "region": large_gaps[0] if large_gaps else None,
        })

    return {
        "file": str(screenshot_path),
        "size": f"{w}x{h}",
        "texts_found": len(texts),
        "texts": texts[:50],  # first 50
        "h_lines": len(h_lines),
        "issues": issues,
        "summary": {
            "overlaps": sum(1 for i in issues if i["type"] == "overlap"),
            "table_issues": sum(1 for i in issues if i["type"] == "table_misalignment"),
            "alignment_issues": sum(1 for i in issues if i["type"] == "alignment"),
            "blank_areas": sum(1 for i in issues if i["type"] == "large空白区域"),
        },
    }


def annotate_screenshot(screenshot_path, analysis, output_path=None):
    """Draw detected issues on the screenshot."""
    img = cv2.imread(str(screenshot_path))
    if img is None:
        return None

    # Draw overlapping regions in red
    for issue in analysis.get("issues", []):
        if issue["type"] == "overlap":
            r = issue["region"]
            cv2.rectangle(img, (r["x1"], r["y1"]), (r["x2"], r["y2"]), (0, 0, 255), 2)
            cv2.putText(img, "OVERLAP", (r["x1"], r["y1"] - 5),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
        elif issue["type"] == "table_misalignment":
            y = issue["region"]["y"]
            cv2.line(img, (0, y), (img.shape[1], y), (0, 165, 255), 2)

    if output_path is None:
        output_path = Path(screenshot_path).parent.parent / "annotated" / Path(screenshot_path).name
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(output_path), img)
    return str(output_path)


def analyze_all(baseline_dir, output_json=None):
    """Analyze all screenshots in a directory."""
    import json
    baseline_dir = Path(baseline_dir)
    results = {}

    for img_path in sorted(baseline_dir.glob("*.png")):
        print(f"  Analyzing: {img_path.stem}...")
        analysis = analyze_layout(img_path)
        results[img_path.stem] = analysis

        # Annotate
        annotate_screenshot(img_path, analysis)

        s = analysis.get("summary", {})
        total = sum(s.values())
        if total > 0:
            print(f"    Issues: {s}")
        else:
            print(f"    OK")

    if output_json:
        Path(output_json).parent.mkdir(parents=True, exist_ok=True)
        with open(output_json, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"\nJSON report: {output_json}")

    # Summary
    total_issues = sum(
        sum(r.get("summary", {}).values())
        for r in results.values()
    )
    print(f"\n=== SUMMARY: {total_issues} issues across {len(results)} screens ===")
    return results


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="UI Layout Analyzer (OpenCV + pytesseract)")
    parser.add_argument("command", choices=["analyze", "single"])
    parser.add_argument("path", help="Directory or single file to analyze")
    parser.add_argument("--json", help="Output JSON path")
    args = parser.parse_args()

    if args.command == "analyze":
        analyze_all(args.path, args.json)
    elif args.command == "single":
        result = analyze_layout(args.path)
        import json
        print(json.dumps(result, indent=2, ensure_ascii=False))
