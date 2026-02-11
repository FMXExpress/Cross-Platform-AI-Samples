# 24-Qwen2.5-VL

This sample showcases **Qwen2.5-VL 72B Instruct** from Replicate Explore using DelphiFMX for Python.

## Why this as Sample #24?
After reviewing samples #1–#23, this repo already has strong coverage for:
- Image generation and editing (FLUX family, Ideogram, Nano Banana, Qwen Image Edit)
- Video generation/upscaling/talking head pipelines
- Speech + transcription + music generation
- Text-first LLM assistants/chat

The next best addition from Replicate Explore is **Qwen2.5-VL** because it scores high on both popularity and variety:

- **Popularity:** Qwen2.5-VL is one of the widely used open multimodal instruction models on Replicate for OCR + visual reasoning workflows.
- **Variety:** It introduces a dedicated **vision-language analysis** workflow (image understanding, text extraction, chart/document interpretation), which is different from pure generation demos.
- **Workflow fit:** Complements existing create/edit samples with a practical “understand what is in this image” assistant.

## Features
- Analyze an image using `qwen/qwen2.5-vl-72b-instruct`
- Supports either:
  - **Local image file** upload (auto-converted to data URI), or
  - **Image URL** input
- Custom prompt for OCR, scene understanding, or reasoning tasks
- Adjustable `max_tokens` preset
- Polling-based status updates and response viewer
- API key input with optional auto-prefill from `REPLICATE_API_TOKEN`

## Prerequisites
```bash
pip install delphifmx replicate
```

## Running the Demo
1. Open `qwen25_vl.py`.
2. Enter your Replicate API key.
3. Choose a local image or paste an image URL.
4. Enter your prompt (for example: “Extract all text and summarize key points.”).
5. Click **Analyze with Qwen2.5-VL**.
6. View the response in the output panel.
