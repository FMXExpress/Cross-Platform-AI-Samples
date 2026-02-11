# 23-FLUX-Schnell

This sample showcases **FLUX Schnell** from Replicate Explore using DelphiFMX for Python.

## Why this as Sample #23?
After reviewing the current sample set, the repo already covers strong quality-focused image generation (FLUX.2 Pro, FLUX Kontext Pro, Ideogram v3 Turbo), video generation, speech, transcription, and LLM chat. FLUX Schnell is the next best addition because it adds:

- **Popularity:** FLUX Schnell is one of Replicate Explore's most widely used image models for rapid prompt iteration.
- **Variety:** It focuses on **high-speed, multi-variation ideation** instead of top-end single-image polish.
- **Workflow fit:** It complements existing premium image samples by covering the "generate many options fast" use case.

## Features
- **Prompt-based image generation** via `black-forest-labs/flux-schnell`.
- **Aspect ratio presets** for square, landscape, and portrait outputs.
- **Multi-output generation** (1–4 variations in one request).
- **Automatic result download + preview** (first generated image shown in-app).
- **Inline API key entry** (or automatic prefill from `REPLICATE_API_TOKEN`).

## Prerequisites
```bash
pip install delphifmx replicate
```

## Running the Demo
1. Open `flux_schnell.py`.
2. Enter your Replicate API key.
3. Enter a prompt, select an aspect ratio, and choose output count.
4. Click **Generate Variations**.
5. Wait for the preview and saved image files.
