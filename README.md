# MakeMeDinner

**Multimodal AI Cooking Assistant for the AMD Developer Hackathon**

> "Point your camera at your fridge. We'll tell you what to cook."

MakeMeDinner is a vision-first AI cooking assistant built for the AMD Developer Hackathon (Vision & Multimodal AI track). It combines on-device ingredient recognition, recipe generation, and voice-guided cooking instructions — all optimized for AMD ROCm GPU acceleration.

---

## Hackathon Track

**Vision & Multimodal AI** — MakeMeDinner demonstrates real-time vision understanding (ingredient detection from camera/photos), natural language recipe generation, and text-to-speech guidance in a unified multimodal pipeline.

---

## Features

1. **Snap & Scan** — Take a photo of your fridge or pantry. AMD-optimized vision models (CLIP + fine-tuned classifier) identify available ingredients.
2. **Smart Recipe Match** — LLM suggests recipes you can make right now, ranked by match percentage.
3. **Missing Item List** — Auto-generates a shopping list for recipes you almost have.
4. **Voice Chef Mode** — Step-by-step cooking instructions read aloud via TTS. Hands-free for the kitchen.
5. **Dietary Filters** — Vegan, keto, halal, allergies — all respected in recipe matching.
6. **Leftover Wizard** — Input "I have 2 eggs and leftover rice" via voice or text. Get fried rice recipes.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                       CLIENT (Browser/App)                  │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────────┐  │
│  │ Camera Input │  │ Voice Input  │  │  Recipe Display  │  │
│  └──────┬───────┘  └──────┬───────┘  └─────────────────┘  │
└─────────┼────────────────┼───────────────────────────────────┘
          │                │
          ▼                ▼
┌─────────────────────────────────────────────────────────────┐
│              AMD DEVELOPER CLOUD (ROCm/MI300X)              │
│  ┌──────────────────┐    ┌──────────────────────────────┐   │
│  │  Vision Encoder  │    │        LLM Engine            │   │
│  │  (CLIP/SigLIP)   │───▶│    (Llama-3.1-8B-Instruct) │   │
│  │  Ingredient Det  │    │    Recipe Gen + TTS          │   │
│  └──────────────────┘    └──────────────────────────────┘   │
│                        Supabase (Auth + DB)                  │
└─────────────────────────────────────────────────────────────┘
```

---

## Tech Stack

| Component | Technology | AMD Optimized |
|-----------|-----------|---------------|
| Vision | CLIP / SigLIP | ROCm PyTorch |
| LLM | Llama-3.1-8B-Instruct | vLLM on MI300X |
| TTS | Coqui TTS / Piper | ONNX Runtime ROCm |
| Backend | Supabase Edge Functions | Deno Deploy |
| DB | Supabase PostgreSQL | — |
| Demo | Vanilla JS + WebRTC | — |

---

## Quick Start

```bash
# Clone
git clone https://github.com/xmrtdao/makemedinner.git
cd makemedinner

# Set env
export SUPABASE_URL=https://your-project.supabase.co
export SUPABASE_ANON_KEY=your-anon-key

# Run demo locally (python3)
cd demo && python3 -m http.server 8080
```

Open `http://localhost:8080` → Allow camera → Snap your ingredients.

---

## Project Structure

```
makemedinner/
├── README.md
├── demo/
│   └── index.html          # Interactive webcam demo
├── vision/
│   ├── model.py            # CLIP-based ingredient classifier
│   ├── labels.json         # 200+ ingredient classes
│   └── requirements.txt
├── recipes/
│   ├── prompt_template.txt # LLM system prompt for chef
│   └── sample_recipes.json # Seed recipe database
├── tts/
│   ├── generate.py         # Piper/Coqui TTS wrapper
│   └── voices/
├── supabase/
│   ├── schema.sql          # ingredients, recipes, user_profiles
│   └── functions/
│       ├── scan-ingredients/   # Vision inference endpoint
│       ├── suggest-recipes/    # LLM recipe matching
│       └── speak-instruction/  # TTS streaming endpoint
└── deploy/
    └── huggingface-space/  # Gradio wrapper for HF demo
```

---

## API Endpoints (Edge Functions)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/scan-ingredients` | POST | Accepts base64 image, returns detected ingredients with confidence |
| `/suggest-recipes` | POST | Takes ingredient list + dietary prefs, returns ranked recipes |
| `/speak-instruction` | POST | Returns audio URL for a cooking step |
| `/save-pantry` | POST | Persist user's pantry to DB |

---

## Vision Model

We fine-tuned a CLIP-style vision encoder on the [Recipe1M+](http://pic2recipe.csail.mit.edu/) ingredient subset using ROCm. The model classifies 200+ common cooking ingredients from a single photo.

Training command:
```bash
python vision/train.py \
  --model openai/clip-vit-base-patch32 \
  --dataset data/ingredients \
  --epochs 10 \
  --batch-size 64 \
  --device cuda  # AMD MI300X via ROCm
```

---

## Demo

Try the live demo: [https://huggingface.co/spaces/xmrtdao/makemedinner](https://huggingface.co/spaces/xmrtdao/makemedinner)

Or run the static demo locally:
```bash
cd demo
python3 -m http.server 8080
```

The demo uses WebRTC to capture your camera, sends frames to the vision endpoint, and renders real-time ingredient tags + recipe cards.

---

## Team

- **Joe Lee** (DevGruGold / XMRT DAO) — Vision pipeline, edge functions, demo
- **David Elze** (Cuddlefish Labs) — LLM fine-tuning, ROCm optimization, TTS

---

## Hackathon Submission

- **Event:** AMD Developer Hackathon on lablab.ai
- **Track:** Vision & Multimodal AI
- **Repo:** https://github.com/xmrtdao/makemedinner
- **Build in Public:** Tweet thread coming @AIatAMD @lablabai
- **Tags:** `#AMDHackathon`, `#ROCm`, `#MultimodalAI`, `#VisionAI`, `#AICooking`

---

## License

MIT — open source, build in public.
