# 13-LTX-2-Distilled

This demo showcases **Lightricks' LTX-2 Distilled** model via Replicate.com using DelphiFMX for Python.

## Features
- **Fast Production Quality:** A speed-optimized version of LTX-2 that generates up to 1080p video with synchronized sound in seconds.
- **Native A/V Sync:** Creates video and audio (dialogue, ambient, music) simultaneously in one pass for perfect synchronization.
- **Hybrid Workflow:** Supports both Text-to-Video and Image-to-Video.
- **Quantized Performance:** Uses FP8 quantization to double performance while maintaining 4K-capable quality.
- **Dynamic API Key:** Input your Replicate API key directly in the GUI.

## Prerequisites
```bash
pip install delphifmx replicate
```

## Running the Demo
1. Open `ltx2_distilled.py`.
2. Enter your Replicate API key.
3. (Optional) Select a source image for I2V.
4. Enter a scene description (include sound cues) and click **Generate Fast A/V**.
