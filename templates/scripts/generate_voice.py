#!/usr/bin/env python3
"""
Generate narration audio (voice.wav) and word timestamps (words.json)
for Cartoon 3D story shorts.

Default Configuration:
  - Voice Model: Chatterbox TTS (Resemble AI) with precomputed Mark preset ("mark").
  - Acceleration: Automatically enforces GPU execution when available for synthesis and faster-whisper alignment.

Supported Engines:
  - chatterbox (default, supports presets: mark, or any custom .wav / .pt preset)
  - kokoro     (ultra-fast 82M ONNX; voices: bm_george, am_michael, am_adam, etc.)
  - piper      (fast local ONNX neural TTS; voices: en_US-bryce-medium, en_GB-alan-medium, etc.)
  - edge-tts   (Microsoft neural online fallback)

Usage:
  python generate_voice.py --out-dir ~/bridge-short/voice --script SCRIPT.md
  python generate_voice.py --out-dir ~/bridge-short/voice --script SCRIPT.md --preset mark --exaggeration 0.35
"""

import argparse
import json
import os
import re
import sys
import subprocess
import soundfile as sf
import numpy as np


def detect_gpu_device() -> str:
    """Detect if CUDA / GPU is available."""
    try:
        import torch
        if torch.cuda.is_available():
            return "cuda"
    except ImportError:
        pass
    return "cpu"


def find_preset_path(preset_name: str) -> dict:
    """Find preset embeddings (.pt) or reference audio (.wav)."""
    search_dirs = [
        os.path.join(os.path.dirname(__file__), "..", "audio", "voices"),
        os.path.expanduser("~/.agents/skills/cartoon-3d-short/templates/audio/voices"),
        os.path.expanduser("~/.agents/skills/cartoon-3d-short/voice_samples"),
        "/home/exu/.t3/scratch/2026-11-07-https-github-com-mromidev-claude-7a9c895e/templates/audio/voices",
        "/home/exu/.t3/scratch/2026-11-07-https-github-com-mromidev-claude-7a9c895e/voice_samples"
    ]
    name_clean = preset_name.lower().removesuffix(".pt").removesuffix(".wav")

    # Check for precomputed .pt preset first
    for d in search_dirs:
        for fname in [f"{name_clean}_turbo_preset.pt", f"{name_clean}_preset.pt", f"{name_clean}.pt"]:
            p = os.path.join(d, fname)
            if os.path.exists(p):
                return {"type": "pt", "path": os.path.abspath(p)}

    # Check for .wav audio reference
    for d in search_dirs:
        for fname in [f"{name_clean}.wav", f"{name_clean}_ref.wav"]:
            p = os.path.join(d, fname)
            if os.path.exists(p):
                return {"type": "wav", "path": os.path.abspath(p)}

    # Direct path passed
    if os.path.exists(preset_name):
        t = "pt" if preset_name.endswith(".pt") else "wav"
        return {"type": t, "path": os.path.abspath(preset_name)}

    return {"type": "none", "path": None}


def normalize_expression_tags(text: str) -> str:
    """
    Map common expression aliases to Chatterbox's exact token vocabulary:
      [chuckle] / [chuckles] -> [laughter]
      [giggle] / [giggles]   -> [giggle]
      [gasp] / [gasps]       -> [gasp]
      [sigh] / [sighs]       -> [sigh]
      [cough] / [coughs]     -> [cough]
      [groan] / [groans]     -> [groan]
      [sniff] / [sniffs]     -> [sniff]
      [throat]               -> [clear_throat]
    """
    tag_map = {
        r"\[chuckles?\]": "[laughter]",
        r"\[laughs?\]": "[laughter]",
        r"\[giggles?\]": "[giggle]",
        r"\[gasps?\]": "[gasp]",
        r"\[sighs?\]": "[sigh]",
        r"\[coughs?\]": "[cough]",
        r"\[groans?\]": "[groan]",
        r"\[sniffs?\]": "[sniff]",
        r"\[clear_?throat\]": "[clear_throat]",
        r"\[whispers?\]": "[whisper]",
        r"\[sneezes?\]": "[sneeze]",
        r"\[pauses?\]": " ... "
    }
    for pattern, replacement in tag_map.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    return text


def clean_script_markdown(text: str) -> str:
    """Extract clean speech text from SCRIPT.md if frontmatter or headings exist."""
    lines = text.strip().splitlines()
    cleaned = []
    in_frontmatter = False
    for line in lines:
        stripped = line.strip()
        if stripped == "---":
            in_frontmatter = not in_frontmatter
            continue
        if in_frontmatter:
            continue
        if stripped.startswith("#") or stripped.startswith("*Fact") or stripped.startswith("Source:"):
            continue
        if stripped:
            cleaned.append(stripped)
    return " ".join(cleaned)


def synthesize_kokoro(text: str, voice: str, speed: float, out_wav: str):
    from kokoro_onnx import Kokoro
    home = os.path.expanduser("~")
    model_dirs = [
        os.path.join(home, ".cache", "kokoro"),
        os.path.join(home, ".t3", "scratch", "2026-11-07-https-github-com-mromidev-claude-7a9c895e", "models", "kokoro"),
        "./models/kokoro"
    ]
    model_path, voices_path = None, None
    for d in model_dirs:
        m = os.path.join(d, "kokoro-v1.0.onnx")
        v = os.path.join(d, "voices-v1.0.bin")
        if os.path.exists(m) and os.path.exists(v):
            model_path, voices_path = m, v
            break

    if not model_path:
        cache_dir = os.path.join(home, ".cache", "kokoro")
        os.makedirs(cache_dir, exist_ok=True)
        model_path = os.path.join(cache_dir, "kokoro-v1.0.onnx")
        voices_path = os.path.join(cache_dir, "voices-v1.0.bin")
        if not os.path.exists(model_path):
            print("Downloading Kokoro ONNX model to ~/.cache/kokoro...")
            subprocess.run([
                "curl", "-L",
                "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx",
                "-o", model_path
            ], check=True)
        if not os.path.exists(voices_path):
            print("Downloading Kokoro voices to ~/.cache/kokoro...")
            subprocess.run([
                "curl", "-L",
                "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin",
                "-o", voices_path
            ], check=True)

    lang = "en-gb" if voice.startswith("b") else "en-us"
    kokoro = Kokoro(model_path, voices_path)
    speech_text = re.sub(r"\[.*?\]", "", text)
    samples, sample_rate = kokoro.create(speech_text, voice=voice, speed=speed, lang=lang)
    sf.write(out_wav, samples, sample_rate)
    return out_wav


def synthesize_piper(text: str, voice: str, speed: float, out_wav: str):
    speech_text = re.sub(r"\[.*?\]", "", text)
    home = os.path.expanduser("~")
    piper_dirs = [
        os.path.join(home, ".cache", "piper"),
        os.path.join(home, ".t3", "scratch", "2026-11-07-https-github-com-mromidev-claude-7a9c895e", "models", "piper"),
        "./models/piper"
    ]
    model_path = None
    if os.path.exists(voice):
        model_path = voice
    else:
        for d in piper_dirs:
            cand = os.path.join(d, f"{voice}.onnx") if not voice.endswith(".onnx") else os.path.join(d, voice)
            if os.path.exists(cand):
                model_path = cand
                break

    if not model_path:
        raise FileNotFoundError(f"Could not locate Piper voice model for '{voice}'.")

    cmd = ["piper", "-m", model_path, "-f", out_wav]
    if speed != 1.0:
        cmd.extend(["--length-scale", str(1.0 / speed)])

    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    proc.communicate(input=speech_text.encode("utf-8"))
    if proc.returncode != 0:
        raise RuntimeError("Piper synthesis failed.")
    return out_wav


def synthesize_chatterbox(text: str, preset_name: str, exaggeration: float, out_wav: str):
    """Synthesize speech with Resemble AI Chatterbox-Turbo with native expressive paralinguistic audio tags."""
    try:
        from chatterbox.tts_turbo import ChatterboxTurboTTS
        import torch
    except ImportError:
        raise ImportError("Please install chatterbox-tts: pip install chatterbox-tts")

    device = detect_gpu_device()
    print(f"Synthesizing with Chatterbox-Turbo on {device.upper()} (preset={preset_name})...")
    model = ChatterboxTurboTTS.from_pretrained(device=device)

    preset_info = find_preset_path(preset_name)
    kwargs = {}

    if preset_info["type"] == "pt":
        print(f"Loading precomputed voice preset embeddings: {preset_info['path']}")
        conds = torch.load(preset_info["path"], map_location=device, weights_only=False)
        model.conds = conds
    elif preset_info["type"] == "wav":
        print(f"Loading reference audio preset: {preset_info['path']}")
        kwargs["audio_prompt_path"] = preset_info["path"]
    else:
        print("Note: No preset found, using Chatterbox default voice.")

    formatted_text = normalize_expression_tags(text)
    print(f"Generating audio with expressive tags: {formatted_text}")

    audio = model.generate(formatted_text, **kwargs)
    audio_np = audio.squeeze().cpu().numpy()
    sf.write(out_wav, audio_np, model.sr)
    return out_wav


def synthesize_edge_tts(text: str, voice: str, speed: float, out_wav: str):
    import asyncio
    import edge_tts
    speech_text = re.sub(r"\[.*?\]", "", text)
    rate_str = f"{int((speed - 1.0) * 100):+d}%"
    tmp_mp3 = out_wav + ".tmp.mp3"

    async def _run():
        comm = edge_tts.Communicate(speech_text, voice, rate=rate_str)
        await comm.save(tmp_mp3)

    asyncio.run(_run())
    subprocess.run(["ffmpeg", "-y", "-i", tmp_mp3, "-ar", "48000", "-ac", "1", out_wav],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if os.path.exists(tmp_mp3):
        os.remove(tmp_mp3)
    return out_wav


def align_word_timestamps(wav_path: str, out_json: str):
    """Run faster-whisper with GPU auto-detection to extract word-level timestamps."""
    device = detect_gpu_device()
    compute_type = "float16" if device == "cuda" else "int8"
    print(f"Aligning word timestamps with faster-whisper (target={device.upper()})...")
    try:
        from faster_whisper import WhisperModel
        import librosa
        audio_16k, _ = librosa.load(wav_path, sr=16000)
        try:
            model = WhisperModel("base.en", device=device, compute_type=compute_type)
            segments, _ = model.transcribe(audio_16k.astype(np.float32), word_timestamps=True)
            words = []
            for segment in segments:
                for word in segment.words:
                    words.append({
                        "w": word.word.strip(),
                        "s": float(round(word.start, 3)),
                        "e": float(round(word.end, 3))
                    })
        except Exception as e:
            print(f"Whisper GPU alignment fallback to CPU ({e})...")
            model = WhisperModel("base.en", device="cpu", compute_type="int8")
            segments, _ = model.transcribe(audio_16k.astype(np.float32), word_timestamps=True)
            words = []
            for segment in segments:
                for word in segment.words:
                    words.append({
                        "w": word.word.strip(),
                        "s": float(round(word.start, 3)),
                        "e": float(round(word.end, 3))
                    })
    except ImportError:
        print("faster-whisper not installed; falling back to openai-whisper CLI...")
        device_flag = ["--device", "cuda"] if device == "cuda" else ["--device", "cpu"]
        cmd = ["whisper", wav_path, "--model", "base.en", "--word_timestamps", "True",
               "--output_format", "json", "--output_dir", os.path.dirname(out_json)] + device_flag
        res = subprocess.run(cmd, capture_output=True, text=True)
        gen_json = os.path.splitext(wav_path)[0] + ".json"
        if os.path.exists(gen_json):
            with open(gen_json) as f:
                data = json.load(f)
            words = []
            for seg in data.get("segments", []):
                for w in seg.get("words", []):
                    words.append({"w": w["word"].strip(), "s": round(w["start"], 3), "e": round(w["end"], 3)})
            if gen_json != out_json and os.path.exists(gen_json):
                os.remove(gen_json)
        else:
            raise RuntimeError(f"Whisper alignment failed: {res.stderr}")

    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(words, f, indent=2)
    print(f"Saved {len(words)} aligned words to {out_json}")
    return words


def main():
    parser = argparse.ArgumentParser(description="Generate voice.wav and words.json for 3D Cartoon shorts (Mark preset by default, GPU-accelerated).")
    parser.add_argument("--out-dir", required=True, help="Destination directory (e.g. ~/bridge-short/voice)")
    parser.add_argument("--script", help="Path to SCRIPT.md or text file")
    parser.add_argument("--text", help="Raw script text string")
    parser.add_argument("--engine", default="chatterbox", choices=["chatterbox", "kokoro", "piper", "edge-tts"], help="TTS engine (default: chatterbox)")
    parser.add_argument("--preset", default="mark", help="Voice preset name or file (default: mark)")
    parser.add_argument("--voice", help="Voice name when using Kokoro/Piper/Edge-TTS (e.g. bm_george)")
    parser.add_argument("--exaggeration", type=float, default=0.35, help="Chatterbox exaggeration (0.25=deadpan, 0.5=natural, 0.8=theatrical)")
    parser.add_argument("--speed", type=float, default=1.0, help="Speech speed multiplier (default 1.0)")
    parser.add_argument("--no-align", action="store_true", help="Skip word timestamp alignment")

    args = parser.parse_args()

    if args.script:
        with open(args.script, "r", encoding="utf-8") as f:
            raw_text = f.read()
        speech_text = clean_script_markdown(raw_text)
    elif args.text:
        speech_text = args.text
    else:
        print("Error: Specify either --script <path> or --text '<string>'", file=sys.stderr)
        sys.exit(1)

    os.makedirs(args.out_dir, exist_ok=True)
    out_wav = os.path.join(args.out_dir, "voice.wav")
    out_json = os.path.join(args.out_dir, "words.json")

    device = detect_gpu_device()
    print(f"Hardware execution device: {device.upper()}")
    print(f"Generating speech ({args.engine}, preset: {args.preset})...")
    if args.engine == "chatterbox":
        synthesize_chatterbox(speech_text, args.preset, args.exaggeration, out_wav)
    elif args.engine == "kokoro":
        voice = args.voice or "bm_george"
        synthesize_kokoro(speech_text, voice, args.speed, out_wav)
    elif args.engine == "piper":
        voice = args.voice or "en_US-bryce-medium"
        synthesize_piper(speech_text, voice, args.speed, out_wav)
    elif args.engine == "edge-tts":
        voice = args.voice if args.voice and args.voice.startswith("en-") else "en-GB-RyanNeural"
        synthesize_edge_tts(speech_text, voice, args.speed, out_wav)

    # Standardize output to 48 kHz mono for Remotion / mix.py
    norm_wav = os.path.join(args.out_dir, "voice_48k.wav")
    subprocess.run([
        "ffmpeg", "-y", "-i", out_wav, "-ar", "48000", "-ac", "1", norm_wav
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    os.replace(norm_wav, out_wav)
    print(f"Standardized voice.wav (48 kHz mono) -> {out_wav}")

    if not args.no_align:
        align_word_timestamps(out_wav, out_json)

    print("\nVoice assets ready for story.ts and mix.py!")


if __name__ == "__main__":
    main()
