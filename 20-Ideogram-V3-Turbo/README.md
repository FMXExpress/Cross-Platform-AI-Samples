# 20-Ideogram-V3-Turbo

This sample showcases **Ideogram v3 Turbo** from Replicate Explore using DelphiFMX for Python.

## Why this as Sample #20?
- **Strong follow-up to FLUX.2 [pro]:** Ideogram v3 Turbo is a practical next pick when you want high-quality, prompt-faithful image generation.
- **Fast image workflow:** It keeps the sample focused on a clean prompt-to-image loop with fast iteration.
- **Great cross-use-case model:** Useful for marketing visuals, product mockups, and concept art from the same baseline UI.

## Features
- **Prompt-based text-to-image generation** via `ideogram-ai/ideogram-v3-turbo`.
- **Aspect ratio presets** for square, landscape, and portrait outputs.
- **Automatic result download + preview** in the same desktop app.
- **Inline API key entry** (or automatic prefill from `REPLICATE_API_TOKEN`).

## Prerequisites
```bash
pip install delphifmx replicate
```

## Running the Demo
1. Open `ideogram_v3_turbo.py`.
2. Enter your Replicate API key.
3. Enter a prompt and pick an aspect ratio.
4. Click **Generate Image**.
5. Wait for the image to appear and save locally.
