#!/usr/bin/env python3
"""Convert a ChatGPT cut-list CSV into a CMX 3600 EDL for DaVinci Resolve."""
import argparse, csv, hashlib, re, sys
from pathlib import Path

def tc_to_frames(tc: str, fps: int) -> int:
    match = re.fullmatch(r"(\d{2,}):(\d{2}):(\d{2}):(\d{2})", (tc or "").strip())
    if not match:
        raise ValueError(f"Invalid timecode {tc!r}; expected HH:MM:SS:FF")
    hh, mm, ss, ff = map(int, match.groups())
    if mm >= 60 or ss >= 60 or ff >= fps:
        raise ValueError(f"Timecode {tc!r} is out of range for {fps} fps")
    return (((hh * 60 + mm) * 60 + ss) * fps) + ff

def frames_to_tc(frames: int, fps: int) -> str:
    hh, rem = divmod(frames, fps * 3600)
    mm, rem = divmod(rem, fps * 60)
    ss, ff = divmod(rem, fps)
    return f"{hh:02d}:{mm:02d}:{ss:02d}:{ff:02d}"

def reel_name(source: str) -> str:
    clean = re.sub(r"[^A-Z0-9]", "", Path(source).stem.upper())
    suffix = hashlib.sha1(source.encode("utf-8")).hexdigest()[:3].upper()
    return (clean[:5] + suffix)[:8].ljust(8, "0")

def convert(csv_path: Path, edl_path: Path, fps: int) -> int:
    if fps not in (24, 25, 30, 50, 60):
        raise ValueError("Frame rate must be one of 24, 25, 30, 50, or 60")
    with csv_path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        required = {"clip_name", "source_file", "source_in", "source_out"}
        if not reader.fieldnames or not required.issubset(reader.fieldnames):
            raise ValueError("CSV needs columns: clip_name, source_file, source_in, source_out")
        rows = [row for row in reader if any((value or "").strip() for value in row.values())]
    if not rows:
        raise ValueError("CSV has no edit rows")
    lines = ["TITLE: ChatGPT Cut List", "FCM: NON-DROP FRAME", ""]
    timeline_cursor = 0
    for number, row in enumerate(rows, 1):
        name = (row.get("clip_name") or "").strip() or f"Clip {number}"
        source = (row.get("source_file") or "").strip()
        if not source:
            raise ValueError(f"Row {number}: source_file is empty")
        src_in, src_out = tc_to_frames(row.get("source_in", ""), fps), tc_to_frames(row.get("source_out", ""), fps)
        duration = src_out - src_in
        if duration <= 0:
            raise ValueError(f"Row {number}: source_out must be after source_in")
        rec_in, rec_out = timeline_cursor, timeline_cursor + duration
        lines.append(f"{number:03d}  {reel_name(source)} V     C        {frames_to_tc(src_in, fps)} {frames_to_tc(src_out, fps)} {frames_to_tc(rec_in, fps)} {frames_to_tc(rec_out, fps)}")
        lines.extend((f"* FROM CLIP NAME: {name}", f"* SOURCE FILE: {source}", ""))
        timeline_cursor = rec_out
    edl_path.parent.mkdir(parents=True, exist_ok=True)
    edl_path.write_text("\n".join(lines), encoding="utf-8")
    return len(rows)

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("cut_list", type=Path, help="CSV: clip_name, source_file, source_in, source_out")
    parser.add_argument("-o", "--output", type=Path, help="Output .edl path (default: next to CSV)")
    parser.add_argument("--fps", type=int, required=True, help="Rate: 24, 25, 30, 50, or 60")
    args = parser.parse_args()
    target = args.output or args.cut_list.with_suffix(".edl")
    try:
        count = convert(args.cut_list, target, args.fps)
    except (OSError, ValueError, csv.Error) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2
    print(f"Wrote {count} edits to {target}")
    print("Import the EDL as a timeline in Resolve, then relink media if prompted.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
