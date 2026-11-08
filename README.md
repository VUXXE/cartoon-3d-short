# Cartoon 3D Story Shorts (Claude & Gemini Skill)

An advanced agent skill for making ~55–70s viral vertical animated story shorts: 2D characters in a colourful 3D world, with ink outlines, painted scenery, lens blur, gliding cameras, a march score, sound effects, and expressive voice narration.

Everything is rendered using **three.js** inside **Remotion** on your own computer with local GPU hardware acceleration.

Forked and expanded from [mromidev/claude-animated-shorts](https://github.com/mromidev/claude-animated-shorts).

---

## What's New in this Fork

1. **Local Voice AI with Native Expression (Chatterbox-Turbo):**
   - Built-in zero-shot voice cloning with precomputed **Mark** voice preset (`templates/audio/voices/mark_turbo_preset.pt`).
   - Native paralinguistic expression tags synthesized directly into audio: `[chuckle]`, `[laugh]`, `[gasp]`, `[sigh]`, `[cough]`, `[groan]`, `[whispering]`.
   - Multi-engine voice pipeline (`templates/scripts/generate_voice.py`): **Chatterbox-Turbo**, **Kokoro-82M ONNX**, **Piper ONNX**, and Edge-TTS fallback.
   - Word timestamp alignment via `faster-whisper` on GPU/CPU for camera kicks and visual reactions.

2. **Polyfork 3D Premade Asset Library:**
   - Full offline database of [Polyfork Catalog](https://github.com/lucas-martinic/polyfork-catalog) (`references/polyfork/catalog.json`): **3,086 low-poly 3D models** across **47 themed kits** (Medieval Village, Little Tokyo, NYC, Nature, Space Base, Trains, etc.).
   - Asset CLI tool (`scripts/polyfork.py`): Search, inspect, and download optimized GLBs directly to `public/models/`.
   - Three.js loader helper (`templates/bridge/polyfork.ts`): Automatically converts Polyfork models to two-tone Lambert shading and merges into the scene batch with ink outlines.

3. **Linux / Arch GPU Hardware Acceleration:**
   - Chrome / Chromium executable auto-discovery on Linux.
   - WebGL hardware acceleration flags (`--gl=egl`, `--use-gl=egl`, `--enable-gpu-rasterization`).
   - Temp folder redirection (`~/.cache/remotion-tmp`) to prevent `ENOSPC` crashes on RAM-backed `/tmp` systems.

4. **Multi-Agent & Model Support:**
   - Compatible with Claude Code, Google Gemini (Antigravity harness), and OpenAI Codex.

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
Clone or symlink this repository to your agent's skills folder:
- **Claude Code:** `~/.claude/skills/cartoon-3d-short`
- **Gemini / Antigravity:** `~/.agents/skills/cartoon-3d-short` or `~/.gemini/config/skills/cartoon-3d-short`

### 2. Generate Narration Audio with Mark's Voice & Expressions
```bash
# Default: Generates Mark's voice with Chatterbox-Turbo on GPU
python scripts/generate_voice.py --out-dir ~/my-short/voice --script SCRIPT.md

# Inline text with expression tags
python scripts/generate_voice.py --out-dir ~/my-short/voice \
  --text "Wait, you thought that would work? [chuckle] That is ridiculous."
```

### 3. Search and Add Premade 3D Scenery (Polyfork)
```bash
# Search 3,086 assets
python scripts/polyfork.py search "house" --kit medieval-village-kit-ca0b43

# Download GLB directly into your Remotion project
python scripts/polyfork.py download a-frame-cabin-6cb550 --out-dir ./public/models
```

### 4. Render with GPU Acceleration
```bash
# Hardware-accelerated stills (look checks)
node scripts/bridge-stills.mjs out/<name>/x_ 100,400 0.5

# Final 2K vertical render (1440x2560)
npx remotion render src/index.ts <CompositionName> out/<name>/video.mp4 \
  --codec h264 --crf 16 --scale 1.3333 --gl egl \
  --chromium-options='{"args":["--enable-gpu","--use-gl=egl","--ignore-gpu-blocklist","--enable-gpu-rasterization"]}'
```

---

## License
The code and documentation are MIT (see `LICENSE`). The reference frames are included for style study only.
