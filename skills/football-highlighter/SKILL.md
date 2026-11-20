---
name: football-highlighter
description: Build football match highlights and goal clips from a full match video using audio spikes, event data, and smart 9:16 crop. Use when asked to make match highlights, goal clips, or reels.
---

# Football Highlighter

## Goal
Turn a full match video into a short vertical highlight reel or individual goal clips.

## Inputs
- Source match video (mp4/mkv)
- Optional match config JSON with kickoff offsets and goals
- Optional event CSV / WhoScored / Scoresway URL

## Workflow
1. Detect highlights:
   - Audio spikes (crowd noise) for exciting moments
   - Optional YOLO ball/player tracking for saves, shots, goals
   - Event data (goals, corners, fouls) if available
2. Refine goal times using audio peak detection (+-120s window)
3. Cut windows (15s before to 90s after peak)
4. Crop to 9:16 or 1:1 with ball tracking or center crop
5. Apply score overlay and color grade
6. Output individual clips or merged reel

## Commands
```
python fh.py highlights match.mp4 --strategy combined --crop smart --aspect 9:16
python fh.py goals match.mp4 -c match_config.json
```

## Match Config Format
```json
{
  "match": {"home": "Team A", "away": "Team B", "competition": "League", "date": "2026-01-01"},
  "kickoff_offsets": {"first_half": 354, "second_half": 3589},
  "goals": [{"minute": 6, "scorer": "Player", "team": "home", "score_after": "1-0"}]
}
```

## Rules
- Prefer real event data over audio-only detection
- Keep clips 7-60s, hook in first second
- Credit source, no piracy or fake news
- Output to jobs/<id>/edits/
```