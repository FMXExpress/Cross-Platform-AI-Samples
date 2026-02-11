# 07-Audio-to-Video

This demo showcases **Lightricks' Audio-to-Video (LTX-2)** model via Replicate.com using DelphiFMX for Python.

## Features
- **Audio-Driven Generation:** Unlike standard T2V, this model uses your audio (speech or music) as the primary creative control to drive timing, pacing, and motion.
- **Synchronized Performance:** Perfect for creating lip-synced character performances or music-driven visual art.
- **Multimodal Controls:** Supports an optional reference image to anchor the visual subject and a text prompt to set the style.
- **High Resolution:** Supports up to 4K output resolutions.
- **Dynamic API Key:** Input your Replicate API key directly in the GUI.

## Prerequisites
```bash
pip install delphifmx replicate
```

## Running the Demo
1. Open `audio_to_video.py`.
2. Enter your Replicate API key.
3. Select an **Audio File** (required).
4. (Optional) Select a **Reference Image**.
5. Click **Generate Audio-Driven Video**.
