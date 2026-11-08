#!/usr/bin/env python3
"""
Generate topic-adaptive sound effects (sfx.py) and mastered soundtrack mix (mix.wav)
for any 3D cartoon short project, timed precisely to SCRIPT.md and voice/words.json.

Usage:
  python scripts/generate_sfx.py --project-dir /path/to/project
  python scripts/generate_sfx.py --script SCRIPT.md --words voice/words.json --render
"""

import argparse
import json
import math
import os
import re
import sys
import subprocess
import numpy as np

# Keywords mapped to procedural DSP generators in sfx_gen.py
KEYWORD_RULES = [
    # Environment & Weather
    (r"\b(breeze|wind|gust|draft)\b", "breeze", -12, "soft wind breath", "breeze"),
    (r"\b(gale|storm|hurricane|howl|howling)\b", "gale_wind", -7, "howling gale wind", "wind"),
    (r"\b(puget|ocean|sea|river|water|waves|lake)\b", "water_bed", -14, "water flow and ripples", "water"),
    (r"\b(splash|plunge|plunges|dropped|fell|dive)\b", "splash_big", 0, "heavy water splash and impact", "impact"),
    (r"\b(sparrow|birds|chirp|chirping|forest)\b", "bird_chirps", -15, "bird chirps", "nature"),
    (r"\b(crickets|night|dusk|evening)\b", "crickets", -18, "evening crickets", "nature"),

    # Vehicles & Engines
    (r"\b(car|cars|roadster|vehicle|truck|drive|driving)\b", "vintage_car", -12, "car engine roll", "vehicle"),
    (r"\b(horn|honk|toot)\b", "vintage_horn", -7, "vintage car horn", "vehicle"),
    (r"\b(toll|coin|pay|cents|dollar|money)\b", "toll_coin", -6, "toll coin clink into register", "foley"),
    (r"\b(rollercoaster|roller coaster|trampoline|bounce|bounces|bouncing)\b", "car_bounce", -8, "trampoline road bounce & leaf-spring squeak", "motion"),
    (r"\b(rollercoaster|ride|thrill|rush)\b", "rollercoaster_whoosh", -7, "rollercoaster air whoosh & track clatter", "motion"),
    (r"\b(seasick|dizzy|queasy|wobble|sway)\b", "seasick_wobble", -8, "queasy wobble pitch dive", "comedy"),

    # Structural Stress, Metal & Failure
    (r"\b(twist|twisting|ribbon|torsion|tilt|tilts)\b", "torsion_groan", -4, "massive structural steel twisting groan", "creak"),
    (r"\b(groan|groaning|creak|creaking|strain)\b", "chain_groan", -6, "suspension metal groaning under stress", "creak"),
    (r"\b(snap|snaps|guitar|strings|cable|cables)\b", "cable_twang", -2, "high-tension cable snap like guitar string", "impact"),
    (r"\b(tear|tore|tearing|ripped|rip|peel)\b", "timber_tear", -4, "heavy structural material tearing apart", "impact"),
    (r"\b(crack|fracture|break|breaks|slam|hit)\b", "wood_crack", -3, "violent structural fracture crack", "impact"),
    (r"\b(skid|curb|slide|sliding|crash)\b", "car_curb_slam", -4, "car skidding and slamming concrete curb", "impact"),

    # Movement, Characters & Foley
    (r"\b(crawl|crawls|crawling|knees|hands)\b", "crawling_knees", -9, "hands and knees pavement crawling scuffs", "foley"),
    (r"\b(escape|run|leap|jump|step|footsteps)\b", "stroll_step", -8, "footstep landing on solid ground", "foley"),
    (r"\b(dog|tubby|puppy|bark|whimper)\b", "dog_whimper", -7, "terrified cute puppy whimper", "vocal"),
    (r"\b(crowd|locals|people|cheer|cheers|applause)\b", "applause", -8, "crowd applause & cheers", "crowd"),
    (r"\b(hurrah|pride|hooray)\b", "hurrah", -8, "crowd cheer hurrah", "crowd"),

    # Explanations & Physics
    (r"\b(solid|wall|walls|girder|girders)\b", "modal", -7, "solid steel girder resonant metallic thud", "physics"),
    (r"\b(paper|flutter|strip|blow|blown|puff)\b", "paper_flutter", -6, "human breath puff + paper strip flutter", "physics"),
    (r"\b(vortex|vortexes|spinning|eddies|swirl)\b", "vortex_whoosh", -7, "aerodynamic vortex shedding whoosh", "physics"),
    (r"\b(truss|trusses|open|through|clean)\b", "truss_wind", -11, "clean laminar breeze whistling through open trusses", "physics"),
    (r"\b(closed|forever|lock|locked|gate|shut)\b", "gate_lock", -3, "heavy iron toll gate & padlock shutting CLANG", "foley"),
]


def load_words(words_path):
    if not os.path.exists(words_path):
        return []
    with open(words_path, "r", encoding="utf-8") as f:
        return json.load(f)


def analyze_script_and_words(script_text, words):
    """Scan words.json against keyword rules and map exact timestamps."""
    cues = []
    seen_times = set()

    for item in words:
        w = item.get("w", "").strip().lower()
        t = item.get("s", 0.0)
        # Clean punctuation
        clean_w = re.sub(r"[^\w\s]", "", w)

        for pattern, gen_func, naive_lvl, desc, category in KEYWORD_RULES:
            if re.search(pattern, clean_w):
                # Avoid stacking identical cues within 0.25 seconds
                time_key = (gen_func, round(t * 3) / 3)
                if time_key in seen_times:
                    continue
                seen_times.add(time_key)

                cues.append({
                    "t": round(t, 2),
                    "word": w,
                    "gen": gen_func,
                    "naive": naive_lvl,
                    "desc": desc,
                    "cat": category
                })
                break

    return cues


def generate_sfx_code(project_dir, cues, dur=67.5):
    """Generate modern, modular Python sfx.py for the project."""
    lines = [
        '# Topic-Adaptive procedural sound effects stem generator',
        '# Auto-generated by generate_sfx.py from SCRIPT.md and words.json',
        'import math',
        'import numpy as np',
        'from dsp import (SR, ns, tt, rng, dbg, lp, hp, bp, peq, shelf, pan, st, place, fades, widen, make_ir, convolve_st,',
        '                 momentary_max, integrated, colored, smooth_noise, modal, reson)',
        'import sfx_gen as G',
        'import timeline as T',
        '',
        'N = ns(T.DUR)',
        'SFX_DB = -6.0',
        '',
        '',
        'class Cue:',
        '    def __init__(self, t, name, desc, gen, naive, kind="event", p=0.0, extra=0.0, lpf=None, send=0.12, group=None, cut=None):',
        '        self.t, self.name, self.desc, self.gen, self.naive = t, name, desc, gen, naive',
        '        self.kind, self.p, self.extra, self.lpf, self.send, self.cut = kind, p, extra, lpf, send, cut',
        '        self.group = group or name',
        '        self.applied = naive + (SFX_DB if kind == "event" else 0.0) + extra',
        '        self.measured = None',
        '',
        '',
        'def cues():',
        '    C = []',
        '    R = rng(1940)',
        '    rr = lambda: rng(int(R.integers(1 << 30)))',
        '    add = C.append',
        '',
        '    # ---------------- Ambience Beds (layered scene progression)',
        '    # Act 1 Bed (0.0s to 21.0s)',
        '    def amb_act1(dur):',
        '        def g():',
        '            r = rng(101)',
        '            x = G.breeze(dur, r, 0.85, 0.18, 750)',
        '            waves = bp(colored(ns(dur), r, 0.8), 120, 1400, 1) * 0.45',
        '            return fades(x + st(waves), 0.3, 0.5), 0.0',
        '        return g',
        '    add(Cue(0.0, "amb_act1", "Act 1 daytime environment bed", amb_act1(min(21.5, T.DUR)), -27, "bed", send=0.0))',
        '',
        '    # Act 2 Bed (Storm / Tension / Twist: 21.0s to 43.5s)',
        '    if T.DUR > 21.0:',
        '        def amb_act2(dur):',
        '            def g():',
        '                r = rng(102)',
        '                gw = G.gale_wind(dur, r, gust=0.45, f_whistle=440)',
        '                return fades(st(gw * 1.1), 0.5, 0.5), 0.0',
        '            return g',
        '        add(Cue(21.0, "amb_act2", "Act 2 gale / tension bed", amb_act2(min(22.5, T.DUR - 21.0)), -23, "bed", send=0.0))',
        '',
        '    # Act 3 Bed (Climax / Aftermath / Modern: 42.0s to End)',
        '    if T.DUR > 42.0:',
        '        def amb_act3(dur):',
        '            def g():',
        '                r = rng(103)',
        '                tw = G.truss_wind(dur, r)',
        '                return fades(st(tw * 0.9), 0.4, 0.3), 0.0',
        '            return g',
        '        add(Cue(42.0, "amb_act3", "Act 3 calm aftermath / modern bed", amb_act3(T.DUR - 42.0), -26, "bed", send=0.0))',
        '',
        '    # ---------------- Synchronized Narrative Event Cues',
    ]

    for i, c in enumerate(cues):
        t = c["t"]
        func = c["gen"]
        naive = c["naive"]
        desc = c["desc"]
        word = c["word"]
        pan_val = round(-0.35 if (i % 2 == 0) else 0.35, 2)

        # Handle specific sound generator invocations
        if func == "breeze":
            gen_expr = "lambda: (st(G.whoosh(1.2, rr(), 0.3, 300, 1200, 0.6, 0.1, 0.3) * 0.5), 0.0)"
        elif func == "gale_wind":
            gen_expr = "lambda: (st(G.whoosh(2.0, rr(), 0.8, 180, 1600, 0.9, 0.3, 0.3) * 1.1), 0.0)"
        elif func == "water_bed":
            gen_expr = "lambda: (st(G.water_bed(2.5, rr(), close=1.2) * 0.7), 0.0)"
        elif func == "splash_big":
            gen_expr = "lambda: (st(G.splash_big(rr()) * 1.8), 0.0)"
        elif func == "bird_chirps":
            gen_expr = "lambda: (pan(G.bird_chirps(1.5, rr(), 0.4) * 0.1, 0.5), 0.0)"
        elif func == "vintage_car":
            gen_expr = "lambda: (st(G.vintage_car(3.8, rr(), rpm=850)), 0.0)"
        elif func == "vintage_horn":
            gen_expr = "lambda: (st(G.vintage_horn(rr(), dur=0.4)), 0.0)"
        elif func == "toll_coin":
            gen_expr = "lambda: (st(G.toll_coin(rr())), 0.0)"
        elif func == "car_bounce":
            gen_expr = "lambda: (st(G.car_bounce(rr())), 0.0)"
        elif func == "rollercoaster_whoosh":
            gen_expr = "lambda: (st(G.rollercoaster_whoosh(2.2, rr()) * 0.9), 0.0)"
        elif func == "seasick_wobble":
            gen_expr = "lambda: (st(G.seasick_wobble(rr())), 0.0)"
        elif func == "torsion_groan":
            gen_expr = "lambda: (st(G.torsion_groan(2.4, rr(), intensity=1.4)), 0.0)"
        elif func == "chain_groan":
            gen_expr = "lambda: (st(G.chain_groan(1.8, rr(), 0.5, 0.9, 24, 38), 0.0))"
        elif func == "cable_twang":
            gen_expr = "lambda: (st(G.cable_twang(rr(), f0=320)), 0.0)"
        elif func == "timber_tear":
            gen_expr = "lambda: (st(G.timber_tear(rr(), 0.8) * 1.2), 0.0)"
        elif func == "wood_crack":
            gen_expr = "lambda: (st(G.wood_crack(rr()) * 1.2), 0.0)"
        elif func == "car_curb_slam":
            gen_expr = "lambda: (st(G.car_curb_slam(rr())), 0.0)"
        elif func == "crawling_knees":
            gen_expr = "lambda: (st(G.crawling_knees(rr())), 0.0)"
        elif func == "dog_whimper":
            gen_expr = "lambda: (st(G.dog_whimper(rr(), dur=0.5)), 0.0)"
        elif func == "applause":
            gen_expr = "lambda: (G.applause(2.4, rr(), people=24) * 0.8, 0.0)"
        elif func == "hurrah":
            gen_expr = "lambda: (st(G.hurrah(rr(), 240, 1.0)), 0.0)"
        elif func == "paper_flutter":
            gen_expr = "lambda: (st(G.paper_flutter(1.4, rr())), 0.0)"
        elif func == "vortex_whoosh":
            gen_expr = "lambda: (st(G.vortex_whoosh(1.1, rr(), f_center=550)), 0.0)"
        elif func == "truss_wind":
            gen_expr = "lambda: (st(G.truss_wind(2.6, rr()) * 0.9), 0.0)"
        elif func == "gate_lock":
            gen_expr = "lambda: (st(G.gate_lock(rr())), 0.0)"
        elif func == "modal":
            gen_expr = "lambda: (st(G.modal(0.6, [(110, 1.2, 0.08), (240, 0.8, 0.05), (580, 0.5, 0.03)], rr())), 0.0)"
        else:
            gen_expr = f"lambda: (st(G.whoosh(0.5, rr(), 0.1, 400, 2000, 0.8, 0.1, 0.2)), 0.0)"

        cue_name = f"cue_{i+1}_{func}"
        clean_desc = f"{desc} ('{word}')"
        lines.append(f'    add(Cue({t:.2f}, "{cue_name}", "{clean_desc}", {gen_expr}, {naive}, p={pan_val}, send=0.15))')

    lines.extend([
        '',
        '    return C',
        '',
        '',
        '# ================================================================ Render',
        'def render(v_ref, on_event=None):',
        '    """v_ref = integrated loudness of voice stem. Returns (stereo stem, cue list with measured levels)."""',
        '    C = cues()',
        '    out = np.zeros((2, N))',
        '    send = np.zeros(N)',
        '    for c in C:',
        '        x, anchor = c.gen()',
        '        x = np.asarray(x, float)',
        '        x = pan(x, c.p) if x.ndim == 1 else x',
        '        if c.cut is not None:',
        '            k = ns(c.cut - (c.t - anchor))',
        '            if 0 < k < x.shape[1]:',
        '                x = fades(x[:, :k], 0.0, 0.02)',
        '        tgt = v_ref + c.applied',
        '        cur = momentary_max(x) if c.kind == "event" else integrated(x)',
        '        if np.isfinite(cur):',
        '            x = x * dbg(tgt - cur)',
        '        if c.lpf:',
        '            x = lp(x, c.lpf, 1)',
        '        c.measured = momentary_max(x) - v_ref if c.kind == "event" else integrated(x) - v_ref',
        '        t0 = c.t - anchor',
        '        place(out, x, t0)',
        '        if on_event:',
        '            on_event(c, x, t0)',
        '        if c.send > 0:',
        '            G._place_mono(send, c.send * x.mean(0), t0)',
        '    valley = make_ir(1.1, 77, pre=0.01, hf=1.6, early=[(0.09, 0.45, -0.5), (0.14, 0.3, 0.6), (0.23, 0.2, -0.2)])',
        '    out += 0.55 * convolve_st(send, valley)',
        '    out = hp(out, 25, 2)',
        '    end = ns(T.DUR - 0.12)',
        '    out[:, end:] *= np.linspace(1, 0, N - end)[None, :] ** 2',
        '    return out, C',
    ])

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Generate topic-adaptive SFX for any 3D cartoon short.")
    parser.add_argument("--project-dir", default=".", help="Project root directory")
    parser.add_argument("--script", default="SCRIPT.md", help="Script markdown file")
    parser.add_argument("--words", default="voice/words.json", help="Word timestamps JSON")
    parser.add_argument("--render", action="store_true", help="Immediately render mix.wav via audio/mix.py")
    args = parser.parse_args()

    project_dir = os.path.abspath(args.project_dir)
    script_path = os.path.join(project_dir, args.script) if not os.path.isabs(args.script) else args.script
    words_path = os.path.join(project_dir, args.words) if not os.path.isabs(args.words) else args.words

    if not os.path.exists(script_path):
        print(f"Error: Script file not found: {script_path}")
        sys.exit(1)

    if not os.path.exists(words_path):
        print(f"Error: Words timestamp file not found: {words_path}")
        print("Tip: Run scripts/generate_voice.py first to create voice.wav and words.json")
        sys.exit(1)

    with open(script_path, "r", encoding="utf-8") as f:
        script_text = f.read()

    words = load_words(words_path)
    if not words:
        print("Error: words.json is empty or invalid.")
        sys.exit(1)

    dur = words[-1].get("e", 60.0) + 1.6
    print(f"Analyzing narrative beats from {os.path.basename(script_path)} ({len(words)} words, ~{dur:.1f}s)...")

    cues = analyze_script_and_words(script_text, words)
    print(f"Identified {len(cues)} narrative sound cues tailored to topic.")

    sfx_code = generate_sfx_code(project_dir, cues, dur=dur)
    sfx_target = os.path.join(project_dir, "audio", "sfx.py")
    os.makedirs(os.path.dirname(sfx_target), exist_ok=True)

    with open(sfx_target, "w", encoding="utf-8") as f:
        f.write(sfx_code)
    print(f"Generated topic-adaptive SFX file: {sfx_target}")

    if args.render:
        print("\nTriggering audio mix via audio/mix.py...")
        # Clear cached sfx stem
        cache_file = os.path.join(project_dir, "audio", "_cache", "sfx.npy")
        if os.path.exists(cache_file):
            os.remove(cache_file)

        # Run mix.py using the project's venv or python3
        venv_py = os.path.join(project_dir, ".venv", "bin", "python")
        py_bin = venv_py if os.path.exists(venv_py) else sys.executable
        mix_script = os.path.join(project_dir, "audio", "mix.py")

        if os.path.exists(mix_script):
            res = subprocess.run([py_bin, mix_script], cwd=os.path.join(project_dir, "audio"), capture_output=True, text=True)
            print(res.stdout)
            if res.returncode != 0:
                print(f"Mix error: {res.stderr}")
                sys.exit(res.returncode)
            print(f"Full soundtrack mix complete! Output: {os.path.join(project_dir, 'audio', 'mix.wav')}")
        else:
            print(f"Notice: mix.py not found at {mix_script}; sfx.py was generated and ready for mix.")


if __name__ == "__main__":
    main()
