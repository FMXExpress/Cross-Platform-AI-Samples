# 15-ACE-Step-Music-Gen

This demo showcases **ACE-Step**, a foundation model for music generation via Replicate.com using DelphiFMX for Python.

## Features
- **High Performance:** 15x faster than typical LLM-based music generation (generates 4 minutes of music in ~20s on A100).
- **Musical Coherence:** Superior alignment across melody, harmony, and rhythm.
- **Duration Control:** Explicitly set the length of the generated track.
- **Dynamic API Key:** Input your Replicate API key directly in the GUI.
- **Cross-Platform:** Runs on Windows, macOS, and Linux via DelphiFMX.

## Prerequisites
```bash
pip install delphifmx replicate
```

## Running the Demo
1. Open `ace_step_music_gen.py`.
2. Enter your Replicate API key.
3. Enter a music description (e.g., "Upbeat jazz with a fast tempo").
4. Click **Generate Music**.
