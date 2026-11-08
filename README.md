# Cartoon 3D Story Shorts (Universal AI Agent Skill)

A universal AI agent skill for **Google Gemini**, **Claude Code**, **OpenAI Codex**, and any LLM agent harness to create ~55–70s viral vertical animated story shorts: 2D characters in a colourful 3D world, with ink outlines, painted scenery, depth-of-field lens blur, gliding cameras, a march score, sound effects, and expressive voice narration.

Everything is rendered using **three.js** inside **Remotion** directly on your computer with local GPU hardware acceleration.

Forked and expanded from [mromidev/claude-animated-shorts](https://github.com/mromidev/claude-animated-shorts) into a model-agnostic, universal AI agent skill.

---

## What's New in this Skill

1. **Universal Agent Compatibility:**
   - Works natively with **Google Gemini** (Antigravity / T3 Code), **Claude Code**, and **OpenAI Codex**.
   - Leverages large context windows (1M–2M tokens) for cohesive multi-file world building without brittle sandbox splits.

2. **Local Voice AI with Native Expression (Chatterbox-Turbo):**
   - Built-in zero-shot voice cloning with precomputed **Mark** voice preset (`templates/audio/voices/mark_turbo_preset.pt`).
   - Native paralinguistic expression tags synthesized directly into audio: `[chuckle]`, `[laugh]`, `[gasp]`, `[sigh]`, `[cough]`, `[groan]`, `[whispering]`.
   - Multi-engine voice pipeline (`templates/scripts/generate_voice.py`): **Chatterbox-Turbo**, **Kokoro-82M ONNX**, **Piper ONNX**, and Edge-TTS fallback.
   - Word timestamp alignment via `faster-whisper` on GPU/CPU for camera kicks and visual reactions.

3. **Polyfork 3D Premade Asset Library:**
   - Full offline database of [Polyfork Catalog](https://github.com/lucas-martinic/polyfork-catalog) (`references/polyfork/catalog.json`): **3,086 low-poly 3D models** across **47 themed kits** (Medieval Village, Little Tokyo, NYC, Nature, Space Base, Trains, etc.).
   - Asset CLI tool (`scripts/polyfork.py`): Search, inspect, and download optimized GLBs directly to `public/models/`.
   - Three.js loader helper (`templates/bridge/polyfork.ts`): Automatically converts Polyfork models to two-tone Lambert shading and merges into the scene batch with ink outlines.

4. **Linux / Arch GPU Hardware Acceleration:**
   - Chrome / Chromium executable auto-discovery on Linux.
   - WebGL hardware acceleration flags (`--gl=egl`, `--use-gl=egl`, `--enable-gpu-rasterization`).
   - Temp folder redirection (`~/.cache/remotion-tmp`) to prevent `ENOSPC` crashes on RAM-backed `/tmp` systems.

---

## What's Inside

| Path | Description |
|---|---|
| `SKILL.md` | The skill definition: full pipeline, rules, look values, and verification loops |
| `templates/bridge/` | Complete Three.js & Remotion short template (`Bridge.tsx`, `world.ts`, `toon.ts`, `build.ts`, `story.ts`, `polyfork.ts`, `ink.ts`, etc.) |
| `templates/scripts/` | Tooling: `generate_voice.py`, `polyfork.py`, `bridge-stills.mjs`, `sbs_sheet.py`, `short_qa.py` |
| `templates/audio/` | Synthesized sound system: SFX generator, march music, ducking mix, and Mark voice preset |
| `references/polyfork/` | Complete Polyfork 3D catalog: `catalog.json`, 47 kit markdown indexes, and guides |
| `references/STYLE_BIBLE.md` | Script and visual formula measured from 20 reference shorts |
| `references/reports/` | Seven measured reports: motion, depth, textures, characters, lighting, outlines, grade |
| `references/frames/` | 38 full-size reference frames (540x960) for style comparisons |
| `references/sheets/` | 20 contact sheets (1,200 frames total) |

---

## Quick Start

### 1. Install as an Agent Skill
Clone or symlink this repository to your agent's skills directory:
- **Gemini / Antigravity:** `~/.agents/skills/cartoon-3d-short` or `~/.gemini/config/skills/cartoon-3d-short`
- **Claude Code:** `~/.claude/skills/cartoon-3d-short`
- **Codex / Workspace:** Clone into your project's skills folder

### 2. Instruct Your AI Agent
Tell your agent:
> *"Use the cartoon short skill and make a 60-second animated story short about [Topic]."*

The agent follows `SKILL.md`: researching facts, drafting the beat-formula script, generating Mark's voiceover with expressive tags, staging the 3D world with Polyfork models, running look-checks, and rendering the 2K vertical video with GPU acceleration.

### 3. CLI Voice & Asset Helpers
```bash
# Generate Mark's voice with Chatterbox-Turbo and expressions:
python scripts/generate_voice.py --out-dir ~/my-short/voice \
  --text "Wait, you thought that would work? [chuckle] That is ridiculous."

# Search and download 3D assets from Polyfork:
python scripts/polyfork.py search "house" --kit medieval-village-kit-ca0b43
python scripts/polyfork.py download a-frame-cabin-6cb550 --out-dir ./public/models
```

---

## License
The code and documentation are MIT (see `LICENSE`). The reference frames are included for style study only.
