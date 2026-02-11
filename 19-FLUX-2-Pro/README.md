# 19-FLUX-2-Pro

This sample showcases **FLUX.2 [pro]** from Replicate Explore using DelphiFMX for Python.

## Why this as Sample #19?
- **Top Explore placement:** FLUX.2 [pro] appears at the top of Replicate Explore and is one of the strongest image generation options right now.
- **Great quality/simplicity balance:** You can get high-end results with only a prompt and aspect ratio.
- **Useful baseline model:** Ideal as a default text-to-image reference workflow for future image-app variants.

## Features
- **Prompt-based text-to-image generation** via `black-forest-labs/flux-2-pro`.
- **Aspect ratio presets** for square, landscape, and portrait outputs.
- **Automatic result download + preview** in the same desktop app.
- **Inline API key entry** (or automatic prefill from `REPLICATE_API_TOKEN`).

## Prerequisites
```bash
pip install delphifmx replicate
```

## Running the Demo
1. Open `flux_2_pro.py`.
2. Enter your Replicate API key.
3. Enter a prompt and pick an aspect ratio.
4. Click **Generate Image**.
5. Wait for the image to appear and save locally.
