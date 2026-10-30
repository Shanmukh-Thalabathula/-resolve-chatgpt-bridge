# Easy steps: ChatGPT to DaVinci Resolve Free

This folder has three files:

- `chatgpt_to_resolve.py` — the converter. It turns your edit list into a timeline file.
- `cut_list_template.csv` — an example spreadsheet-style edit list. Make a copy and fill in your own video names and timecodes.
- `README.md` — these instructions.

The bridge does not open or control DaVinci Resolve. It prepares an EDL timeline file, which you then import into Resolve.

## Part 1: Prepare your video and cut list

1. Put your video files somewhere you can find them, such as `C:\Videos\MyProject`. Do not move them after creating the cut list.
2. Decide the frame rate for your project (commonly 24, 25, or 30 fps). If you already have a Resolve project, use its frame rate. Otherwise, you will set it when you create the project in Part 2.
3. In ChatGPT, describe the order of shots and the time in/out for each shot. You can upload a clip for help identifying moments, but check the timecodes yourself if exact frame accuracy matters. ChatGPT cannot read files just from a path on your computer.
4. Ask ChatGPT to return CSV with exactly these columns: `clip_name,source_file,source_in,source_out`. Example:

   ```csv
   clip_name,source_file,source_in,source_out
   Opening shot,C:\Videos\MyProject\shot_01.mp4,00:00:02:00,00:00:06:12
   Interview answer,C:\Videos\MyProject\interview.mp4,00:01:14:00,00:01:22:00
   ```

   Timecodes mean `hours:minutes:seconds:frames`. For a 30 fps project, `00:00:02:15` means 2 seconds and 15 frames. `source_out` is the first frame you do not want included.
5. Open `cut_list_template.csv` in Excel, Notepad, or another text editor. Use **Save As** to save a copy named `cut_list.csv` in the same bridge folder. Replace the sample rows with your own rows. Keep the first/header row exactly as shown. Avoid opening and saving CSV in software that changes the paths or timecodes; check the saved text if unsure.

## Part 2: Open DaVinci Resolve and prepare the project

6. Start DaVinci Resolve. Create a new project, or open the project where you want this edit.
7. If creating a project, set the project frame rate to match the rate you chose in Part 1. In Resolve, open **File → Project Settings → Master Settings**, set **Timeline frame rate** and **Playback frame rate**, then save. Resolve may lock the frame rate after you add media or a timeline.
8. Keep Resolve open. You do not need to import the video files first; the EDL import may ask you to locate or relink them. If you prefer, you can import the files to the Media Pool first.

## Part 3: Convert the cut list into an EDL

9. Open the bridge folder in File Explorer. Click the address bar, type `powershell`, and press Enter. A PowerShell window opens in that folder.
10. Type this command and press Enter, replacing `30` with your frame rate:

   ```powershell
   py .\chatgpt_to_resolve.py .\cut_list.csv --fps 30
   ```

11. If it worked, PowerShell says it wrote `cut_list.edl`. That new EDL file should appear in the bridge folder. If PowerShell says `py` is not recognized, install Python 3 from python.org and select the option to add Python to PATH during installation, then try again.

## Part 4: Import the EDL into Resolve

12. Switch back to the open Resolve project.
13. Choose **File → Import Timeline → Import AAF, EDL, XML…** (the wording may vary slightly by Resolve version).
14. Select `cut_list.edl` from the bridge folder. Accept the import options for a new timeline.
15. If Resolve asks where the clips are, point it to the folder containing your original videos, or use **Relink** / **Change Source Folder** to locate them. The source file paths are included in EDL comments to help you identify clips.
16. Open the new timeline and watch it from beginning to end. Check every edit and make any adjustments. This bridge makes a single video track with hard cuts; you add titles, transitions, sound, color, and export settings in Resolve.

## If something goes wrong

- **“CSV needs columns…”** — check that the first line is exactly `clip_name,source_file,source_in,source_out`.
- **Invalid timecode** — use `HH:MM:SS:FF`, such as `00:00:12:08`; frame number must be smaller than the fps.
- **Media offline** — relink the original video files in Resolve.
- **Timeline timing looks wrong** — the `--fps` value, Resolve project rate, and timecodes must all use the same frame rate.
- **No direct ChatGPT-to-Resolve button** — this file handoff is the bridge for Resolve Free. ChatGPT writes the edit plan; the script makes an EDL; Resolve imports and edits it.
