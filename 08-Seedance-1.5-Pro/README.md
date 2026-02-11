# 08-Seedance-1.5-Pro

This demo showcases **ByteDance's Seedance 1.5 Pro** model via Replicate.com using DelphiFMX for Python.

## Features
- **Joint A/V Generation:** Unlike standard models, Seedance generates audio and video simultaneously in a single pass.
- **Precise Lip-Sync:** Achieving millisecond-level synchronization between audio and character mouth movements.
- **Cinematic Camera Control:** Supports complex camera techniques (dolly, pan, zoom) described in the prompt.
- **Multimodal Flexibility:** Supports both Text-to-Video and Image-to-Video workflows.
- **Dynamic API Key:** Input your Replicate API key directly in the GUI.

## Prerequisites
```bash
pip install delphifmx replicate
```

## Running the Demo
1. Open `seedance_pro.py`.
2. Enter your Replicate API key.
3. (Optional) Select a source image for Image-to-Video.
4. Enter a scene description (include audio/speech cues) and click **Generate A/V Video**.
