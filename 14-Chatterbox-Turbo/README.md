# 14-Chatterbox-Turbo

This demo showcases **Resemble AI's Chatterbox Turbo** model via Replicate.com using DelphiFMX for Python.

## Features
- **Ultra-Low Latency:** The fastest open-source TTS model from Resemble AI, built on a streamlined 350M parameter architecture.
- **Paralinguistic Tags:** Native support for adding distinct realism using tags like `[cough]`, `[laugh]`, and `[chuckle]`.
- **High-Fidelity Audio:** Reducing generation steps while retaining excellent audio quality.
- **Dynamic API Key:** Input your Replicate API key directly in the GUI.
- **Cross-Platform:** Runs on Windows, macOS, and Linux via DelphiFMX.

## Prerequisites
```bash
pip install delphifmx replicate
```

## Running the Demo
1. Open `chatterbox_turbo.py`.
2. Enter your Replicate API key.
3. Select a voice ID.
4. Enter text (include tags like `[laugh]` for fun) and click **Speak Text**.
