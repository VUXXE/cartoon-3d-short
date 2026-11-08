---
name: cartoon-3d-short
description: Make a ~55-70 s vertical cartoon story short in the "2D characters in a colourful 3D world" style (flat bean-head cartoon cards with ink outlines, painted 3D town/world with black ink lines, saturated sky, depth-of-field backgrounds, gliding cameras, voice narration, synthesized SFX + march-style music), rendered with three.js inside Remotion. Proven on "The Bridge That Fell for a Song" (2026-10-31). Use when the user asks for another video "like the bridge video", "like the soldiers/bridge short", "in that cartoon 3D style", a history/science story short with cartoon characters in 3D, or says "use the cartoon short skill".
---

# Cartoon 3D story short (three.js + Remotion)

Proven example: **The Bridge That Fell for a Song**. It is an original 67 s short about the 1831 Broughton bridge and 74 soldiers marching in step.
- Code: `src/videos/bridge/` of your Remotion project (composition `BridgeShort`, 1080x1920, 30 fps).
- Script, voice and sound: `~/bridge-short/`.
- Style research: `references/`.

The style reference is a channel studied privately (`references/`: STYLE_BIBLE.md, reports/*.md, frames/).
- Those videos are private study material. Never upload, publish or send them.
- Never copy their scripts, characters or shots. Story, characters and voice are always OUR OWN.
- Never say the channel's name in a voice-over or description.

User rules that apply:
- **Always use Mark for voiceover:** Synthesize narration using **Chatterbox TTS** cloning the **Mark ("Mark - Natural Conversations")** voice (`templates/audio/voices/mark.wav`), with optional expressive tags (`[chuckle]`, `[gasp]`, `[sigh]`).
- **Premade 3D Asset Library (Polyfork):** Use **Polyfork Catalog** (`references/polyfork/`, 3,086 low-poly models across 47 themed kits) whenever assembling 3D scenery, buildings, nature, vehicles, props, or landmarks. Use `python scripts/polyfork.py` to search, inspect, download GLBs, or generate code snippets.
- **Always render with GPU when available:** enforce hardware acceleration across WebGL (EGL/ANGLE), Remotion renders, Whisper alignment, and Chatterbox/Kokoro voice generation.
- No captions or labels in the video.
- English only.
- Voice: one steady conversational tone (or controlled expressive tags).
- Jokes are researched real facts.
- Standard mix: music +3 dB, SFX -6 dB, voice unchanged.
- Final export 2K vertical: 1440x2560, `--scale 1.3333`.
- Model verification (Gemini Vision) verifies every look check.
- Save after every step.
- "Just do it" once the script is approved.

## Pipeline
1. **Topic and facts.** Pick one surprising true story with a physical cause and effect (it should be visual), plus a simple everyday analogy that explains it.
   - Write the facts with their source at the top of `SCRIPT.md`.
2. **Script** (~3.7 words/s, 55-70 s). Beat formula from the bridge short:
   - **Hook:** the absurd fact in one line ("Seventy-four soldiers knocked down an iron bridge just by walking across it.").
   - **Setting:** year, place, pride.
   - **Action:** escalation over three or four beats, each a little bigger.
   - **Snap:** the moment it breaks.
   - **Deadpan double line:** "Luckily ... / Unluckily ...".
   - **Explanation:** one physics idea through an everyday analogy (the kid on a swing).
   - **Consequence:** the rule it created.
   - **Callback twist:** the ending.
   - Never describe on screen what the viewer already sees.
3. **Voice & Word Timings (`voice.wav` + `words.json`).**
   Always use **Mark** via Chatterbox (the default in `scripts/generate_voice.py`):
   ```bash
   # Default: Generates Mark's voice using Chatterbox with GPU acceleration:
   python scripts/generate_voice.py --out-dir ~/bridge-short/voice --script SCRIPT.md

   # With expressive tags & custom emotion dial:
   python scripts/generate_voice.py --out-dir ~/bridge-short/voice --script SCRIPT.md --exaggeration 0.35
   ```
   - **Mark Voice Profile (`templates/audio/voices/mark.wav`):** Natural conversational pacing, warm timbre, articulate storytelling delivery.
   - **Chatterbox Expression Controls:**
     - Tags: `[chuckle]`, `[gasp]`, `[sigh]`, `[pause]`, `[groan]`. These vocal reactions are synthesized in Mark's voice and timestamped into `words.json` so camera kicks and visual reactions land on the exact beat.
     - `--exaggeration`: continuous control from `0.25` (deadpan BBC documentary style) to `0.35` (natural conversational) to `0.65+` (theatrical).
   - **Output Format:**
     - `voice.wav`: 48 kHz mono uncompressed WAV.
     - `words.json`: `[{"w": "soldiers", "s": 0.42, "e": 0.88}, ...]`. Everything in `story.ts` and `mix.py` is timed to `words.json`.
4. **Shot plan** in `story.ts`: copy `templates/bridge/` (the final bridge source, same as `src/videos/bridge/` of your Remotion project) to `src/videos/<name>/`, register a new composition next to `BridgeShort` in `src/Root.tsx`, and rename it.
   - `SHOTS`: id, a/b frames, light day/golden, crowd mode, `tau` story time.
   - `XFADE`: crossfades at place/time changes.
   - `FLASH_AT`: a white flash after the hook.
   - `CAMS`: per-shot keys `{f, dur?, cut?, s: f => {pos, look, fov, roll}}`.
   - `KICKS`: impact flip-shakes.
   - `DOF`/`dofAt`: lens blur per beat.
   - `FOREGROUND`: near framing props.
   - Every visual reaction lands 0-3 frames before its word.
5. **World & Premade 3D Assets (Polyfork).**
   - **Premade Assets from Polyfork Catalog (`references/polyfork/`):**
     - Search 3,086+ low-poly models across 47 themed kits:
       ```bash
       python scripts/polyfork.py search "house" --kit medieval-village-kit-ca0b43
       python scripts/polyfork.py kits
       python scripts/polyfork.py download a-frame-cabin-6cb550 --out-dir ./public/models
       python scripts/polyfork.py snippet a-frame-cabin-6cb550
       ```
     - Load via `loadPolyforkKit(["a-frame-cabin-6cb550", ...])` from `polyfork.ts`.
     - Place in scene via `placePolyforkProp(batch, model, x, y, z, height, yaw)`. Models automatically convert to two-tone cartoon shading (`toLambert()`) and receive the ink outline pass.
   - `lights.ts`: LIGHTS plus the LOOK sky/river/cloud palette per light.
   - `shade.ts`: two-tone shading and `untone()`.
   - `build.ts`: town, houses and Polyfork / Kenney CC0 kit props, recoloured, with sight-line culling of anything blocking a camera.
   - `paint.ts`: HD Canvas2D painted textures with seams painted in as dark tints.
   - `world.ts`: sky shader, fog = horizon colour, river, per-frame posing, sun frozen per shot and camera-relative.
6. **Characters.**
   - `toon.ts`: the Canvas2D `Pen` drawing API, 600x1000 design canvas, soles at y = 975, bean heads, stick limbs, plum variable-width outline, face library.
   - `cast.ts`: camera-facing billboards, crowds, effect cards, blinks, walk cycles. All billboards go on the `NOINK` layer.
   - `cardshade.ts`: cards lit by the scene light, no emissive.
7. **Post** (`Bridge.tsx` + `ink.ts` + `lensblur.ts` + `grade.ts`).
   - Composer order: ink → lens pre → lens main → bloom → NEUTRAL tone map → grade (MSAA 4).
   - Every pixel parameter scales with output height / 1920.
8. **Topic-Adaptive Sound & SFX Generation** (`audio/`: sfx.py, sfx_gen.py, mix.py, music.py, dsp.py).
   - **For any topic:** Do not hardcode sounds from previous shorts. Run `python scripts/generate_sfx.py --project-dir . --render`.
   - The generator scans `SCRIPT.md` and `voice/words.json`, identifies narrative keywords/action beats, builds layered ambience beds, and generates timestamped procedural sound cues from the 48+ DSP generators in `sfx_gen.py` (weather, vehicles, metal stress, cable snaps, impacts, splashes, foley scuffs, cartoon wobbles, and crowds).
   - `audio/mix.py` masters the final audio to ITU-R BS.1770-4 compliance: **-15.0 LUFS**, True Peak **-1.2 dBTP**, with automated speech ducking and section rides.
   - Output: `audio/mix.wav` (48 kHz stereo, exact length), stems (`stem_sfx.wav`, `stem_music.wav`, `stem_voice.wav`), and `cues.md`.
9. **Look checks (GPU-accelerated stills).**
   - Run: `node scripts/bridge-stills.mjs out/<name>/x_ 100,400 0.5` (automatically runs with GPU rasterization and EGL/ANGLE hardware acceleration).
   - Make side-by-sides against reference frames with `python scripts/sbs_sheet.py out.jpg --ours ... --ref ...`.
   - Send the sheet to Gemini Vision: evaluate against target metrics, score 1-10 across 8 dimensions, provide a concise verdict and numbered frame fixes.
10. **Final render (GPU-accelerated).**
    - Always pass GPU hardware acceleration flags:
      ```bash
      # On Linux / Arch (EGL backend):
      npx remotion render src/index.ts <Comp> out/<name>/video.mp4 --codec h264 --crf 16 --scale 1.3333 --gl egl \
        --chromium-options='{"args":["--enable-gpu","--use-gl=egl","--ignore-gpu-blocklist","--enable-gpu-rasterization"]}'

      # On Windows (ANGLE backend):
      npx remotion render src/index.ts <Comp> out/<name>/video.mp4 --codec h264 --crf 16 --scale 1.3333 --gl angle \
        --chromium-options='{"args":["--enable-gpu","--use-gl=angle","--ignore-gpu-blocklist"]}'
      ```
    - Mux with `-map 0:v:0 -map 1:a:0` (Remotion writes a silent audio track).
    - QA: `python scripts/short_qa.py final.mp4 out/<name>/qa shots.json` checks every frame for black, white, frozen and pop frames, plus loudness and sheets.
    - Fix anything it finds, then run a final visual audit.
11. **Deliver.** Provide the final mp4 path, summarize shot count and mix specs.

## Premade 3D Assets: Polyfork Catalog (47 Kits, 3,086 Models)
The skill includes the full offline database of [Polyfork Catalog](https://github.com/lucas-martinic/polyfork-catalog) at `references/polyfork/catalog.json`. All assets are low-poly (300–2,000 tris), Y-up, meter-scaled, centered at y=0, and download directly from `https://polyfork.dev/cdn/<id>.glb`.

### Key Themed Kits:
- **Towns & Architecture:** Medieval Village (`medieval-village-kit-ca0b43`), Little Tokyo (`japanese-suburban-city-street-baa482`), Medieval Japan (`medieval-japan-cb01ad`), Frontier Town (`frontier-town-a0085b`), NYC (`nyc-city-kit-fbca88`), Roadside Americana (`roadside-americana-50d40c`).
- **Nature & Landscape:** Nature & Forest (`nature-forest-kit-f29d6a`), Campground & Lake (`campground-lake-ad32b0`), Prehistoric Valley (`prehistoric-valley-8638dc`), Coral Reef (`coral-reef-a7128a`), Cozy Farm (`cozy-farm-cc979f`).
- **Transportation & Sci-Fi:** Countryside Railway (`countryside-railway-9b4c57`), Retro Cars (`racing-cars-kit-660d53`), Space Base (`space-base-kit-cf65de`), Spaceship Wars (`spaceship-wars-kit-234642`), Airport (`airport-43b137`).
- **Props, UI & Interiors:** 3D UI kit (`3d-ui-kit-5635f7`), Dungeon & Crypt (`dungeon-crypt-c27d93`), Hospital (`hospital-kit-2ebfcb`), Hotel Casino (`casino-3dd029`), Pirate Cove (`pirate-cove-2ebea4`).

### CLI Commands:
```bash
# 1. Search assets by keyword or filter
python scripts/polyfork.py search "tree" --limit 10
python scripts/polyfork.py search "car" --type vehicle --max-triangles 1500

# 2. Browse themed kits
python scripts/polyfork.py kits --search "train"
python scripts/polyfork.py kit countryside-railway-9b4c57

# 3. Download asset GLB to Remotion public/ folder
python scripts/polyfork.py download steam-locomotive-3b8c21 --out-dir ./public/models

# 4. Generate ready-to-paste Three.js snippet
python scripts/polyfork.py snippet steam-locomotive-3b8c21
```

## Final look values (bridge after 4 verifier rounds; all in `templates/bridge/`)
Start every new short from `templates/bridge/` (copy to `src/videos/<name>/`): the look lives in these values, the
story lives in story.ts / build.ts layout / cast.ts roles.
- **Light presets** (`lights.ts`, sun camera-relative and frozen per shot):
  - day: az 75 / el 48, lit [1.58,1.5,1.33], shade [.30,.29,.36], lift [.05,.06,.11] (cool tint ONLY in shade), sky
    top #3e7fd2 → horizon #b8d0ec, fog = horizon, 25→300 m, uSat 1.08, ~15 % blue haze past 60 m.
  - golden: az 6 / el 7 (backlit low sun), key toward #FFB36B ×1.5, violet-blue shade (facade ≈ #444380), sky
    #ffc47c → #8a6f8a, peach fog only past 50 m, sun disc #ffcf9e + bloom, contact blobs + real card shadows.
- **Albedos** (`paint.ts`/`build.ts`): muted brick / cream / ochre / terracotta houses with plinth, cornice, sills,
  hoods, door step, chimney + pot, heights 7 / 8.4 / 9.8 m; warm grey/beige stone (saturation −35 % from "storybook");
  ochre wood deck C* ~51-58 with near-black seams; iron dark and desaturated. Never lemon, never lavender lit faces.
- **Ink** (`ink.ts`): #030303, 5.1 px near (6 m) → 3.3 px far (90 m) at 1080x1920, creases ×0.8 from 35°, depth
  jumps from 1 %, fog tint 0.3 only far; character cards on layer `NOINK` (they carry their own plum ink).
- **Lens** (`lensblur.ts` + `dofAt` in story.ts): cInf px at 1080: hook/river CU 15-16, close-ups 12-14, MS 10-12,
  park 7, golden sway 5, wides/aerials 0. Focus on the eyes of the front row.
- **Post** (`Bridge.tsx`): ink → lens pre → lens main → bloom (thr 1.0, int .5, 6 levels, radius .6) → NEUTRAL tone
  map → grade; MSAA 4. Film grain exists but is OFF (reference measures no grain; it quadruples the file size).
- **Characters** (`toon.ts`/`cast.ts`/`cardshade.ts`): bean heads h/w .94, plum ink #241726, eyes .26 W apart, no blush,
  14 expressions; adults 3.5 head-heights; walk bob 5 %, lean 1-7°, planted 0.8 m stride; blinks 0.5-2.3 s; tight
  contact shadow ~.5 under the feet + sun-direction tail by day; golden rim inner only (never an offset outer copy).
- **Camera** (`story.ts`): cuts on big jumps, smootherstep glides 18-40 f, every hold creeps (no static hold ≥4 f),
  flip kicks decaying over 7 f on impacts, 4-4.6° rolls, foreground props (`FOREGROUND`) in ~1/3 of shots.

## Look targets (measured from the reference; see references/reports/)
- **Ink:**
  - World lines: about 3 px at 1080 wide, near-black #0b0a0c, nearly constant with distance. Silhouettes, depth jumps and normal creases only. No line on wall/floor joins or the horizon. Character cards are never outlined by the world ink.
  - Character ink: dark plum #201628-#2f1d28, thicker on the bottom/shadow side.
- **Colour:**
  - Day median luma ~.57. Non-ink p5 ~.23 (no crushed blacks). Lit chroma C* p90 ~55. Day sky top ~#5e93d9, horizon 1.28x brighter.
  - Golden: peach horizon #ffd08a, violet-blue shadows (never brown), backlit sun.
- **Depth:**
  - DOF on about 1/3 of screen time (CU, MS, inserts), cInf 10-16 px at 1080, focus on the eyes. Establishing and wide shots stay sharp.
  - Fog = horizon colour, 25→420 m day, 20→360 m golden.
  - Bloom only on HDR emissives: threshold 1.0.
- **Camera:**
  - Hard cuts on big jumps. Everything else is a smootherstep glide of 18-40 f, peak ≤ 25 px/f at 720p.
  - Every hold pushes in 0.15-0.35 %/f, with 0.6 %/f on punch words.
  - Rolls of 4-5°.
  - No hand-held float. Impact shakes flip sign every frame and decay over 7 f.
- **Characters:**
  - About 3.5 head-heights tall, legs 1.4 HH.
  - Stick limbs about 0.055 of head width, ink-dot hands.
  - Bean head (h/w ~0.93, narrower chin, pointier crown).
  - No blush or eye highlights. Faces at brightness ~.93.
  - Walk bob 3-7 %, lean 1-7°, planted feet.
  - Blinks every 0.5-2.3 s, lasting 4 f.

## Look-match loop (Gemini workflow)
1. **Measure the reference first.** `references/reports/*.md` contains exact metrics for motion, depth, textures, characters, lighting, outlines, and color grading. Shared brief: `references/reports/CONTEXT.md`.
2. **Context Window Advantage:** With Gemini's 1M–2M token context, you do not need brittle multi-agent sandbox splits unless desired. Gemini can hold and edit `story.ts`, `world.ts`, `toon.ts`, `paint.ts`, `ink.ts`, and `lights.ts` directly in the project directory.
3. **Verify with Gemini Vision:**
   - Render preview stills: `node scripts/bridge-stills.mjs out/<name>/x_ 100,400 0.5`
   - Generate side-by-side sheets: `python scripts/sbs_sheet.py out.jpg --ours out/<name>/x_100.jpg out/<name>/x_400.jpg --ref references/frames/short01_0060.jpg references/frames/short01_0180.jpg`
   - Gemini Vision inspects `out.jpg` and scores each area out of 10 (colour day / golden, lighting, ink, textures, characters, depth, composition) against the reference reports, providing exact frame fix recommendations.
4. Contracts between components live in exported constants (`NOINK` layer from ink.ts, `dofAt`/`FOREGROUND` from story.ts, `LIGHTS`/`LOOK` from lights.ts).

## GPU Acceleration & Platform Gotchas
- **Always Render with GPU:**
  - **Linux / Arch:** WebGL uses hardware-accelerated `--gl=egl` via Mesa Intel / NVIDIA drivers (`--enable-gpu --use-gl=egl --ignore-gpu-blocklist --enable-gpu-rasterization`).
  - **Windows:** Uses `--gl=angle` (`--use-gl=angle`).
  - **Voice & Alignment:** `generate_voice.py` automatically checks `torch.cuda.is_available()` and executes Chatterbox and `faster-whisper` on GPU with `float16`.
- **Arch Linux & Linux Disk/Tmpfs:** On Linux, `/tmp` is typically a `tmpfs` RAM disk. Every Remotion bundle copies `public/` (~1.3 GB) and can quickly fill `/tmp` with `ENOSPC`. Always keep `REMOTION_TMP` pointed to a physical drive (e.g. `~/.cache/remotion-tmp` or `/var/tmp/remotion-tmp`).
- **Browser Executable:** `bridge-stills.mjs` automatically searches for Google Chrome / Chromium on Linux/Arch (`~/.local/bin/google-chrome`, `/usr/bin/google-chrome-stable`, `/usr/bin/chromium`), or respects `PUPPETEER_EXECUTABLE_PATH`.
- **Sight-lines:** Cameras end up inside houses: the sight-line culler in build.ts/world.ts removes anything blocking any camera ray.
- **Ink & Post-Processing:** Ink in the same merged effect pass as DOF gets overwritten. Ink must be its own pass before the blur.
- Pixel-sized post parameters must scale with resolution: stills are at 0.5, the final at 1.333.
- Remotion writes a silent audio track: mux with `-map 0:v:0 -map 1:a:0`.
- 2K renders run ~4 fps (≈10 min for 67 s on GPU). Stills at 0.5 take 3-8 s each after bundling.
- Film grain at 2.5 % quadruples file size and will turn to mush on YouTube; keep it off.

## Readability traps the verifier caught
- **A swing drawn as one rope that disappears behind the kid reads as a HANGING.** Always two ropes to a wide plank
  with the kid between them (`swingKid` in toon.ts), and a frame whose legs clear the arc (A-frame at each end).
- Props or flotsam closer than ~2 m to a lens become huge cut-off blobs at the frame edge. When a camera moves, re-check
  every prop near its new position.
- A foreground bush cut by the frame edge reads as a "green ball"; a foreground prop must be recognisable or gone.
- Flags: red + yellow star/diamond reads as Vietnam's. Use a period-correct flag (St George's cross for England 1831).
- Painted signs lit by a side sun go grey-blue and unreadable: give the sign face an unlit material.
- Golden rim light done as an offset outer copy turns every hat into a picture frame: inner rim only, head/torso only.
- Balcony/railing rails at chest height through characters: put the lens ~2.5 m up so rails cross legs, not torsos.
- Flat holds read as freezes in QA (frozen span ≥12 f): every hold needs a creeping push-in.
