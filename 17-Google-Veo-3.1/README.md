# 17-Google-Veo-3.1

This demo showcases **Google's Veo 3.1** video generation model via Replicate.com using DelphiFMX for Python.

## Features
- **Synchronized Audio:** Automatically generates native audio (dialogue, ambient sound, or music) synchronized with the visuals.
- **High-Fidelity Cinematic Video:** Superior prompt adherence and realistic motion at 720p or 1080p.
- **Multimodal Control:** Supports Text-to-Video and Image-to-Video (I2V) workflows with reference image support.
- **Flexible Duration:** Choose between 4, 6, or 8-second clips.
- **Dynamic API Key:** Input your Replicate API key directly in the GUI.

## Prerequisites
```bash
pip install delphifmx replicate
```

## Running the Demo
1. Open `google_veo.py`.
2. Enter your Replicate API key.
3. (Optional) Select a reference image for Image-to-Video animation.
4. Enter a detailed prompt describing the scene and sounds.
5. Click **Generate Video**.
