# Every sound effect + ambience bed for "The Bridge That Danced Itself to Death" (Tacoma Narrows / Galloping Gertie 1940),
# timed to the picture and voice timeline, rendered into one stereo SFX stem.
import math
import numpy as np
from dsp import (SR, ns, tt, rng, dbg, lp, hp, bp, peq, shelf, pan, st, place, fades, widen, make_ir, convolve_st, reson,
                 momentary_max, integrated, colored, smooth_noise, modal)
import sfx_gen as G
import timeline as T

N = ns(T.DUR)
SFX_DB = -6.0


class Cue:
    def __init__(self, t, name, desc, gen, naive, kind="event", p=0.0, extra=0.0, lpf=None, send=0.12, group=None, cut=None):
        self.t, self.name, self.desc, self.gen, self.naive = t, name, desc, gen, naive
        self.kind, self.p, self.extra, self.lpf, self.send, self.cut = kind, p, extra, lpf, send, cut
        self.group = group or name
        self.applied = naive + (SFX_DB if kind == "event" else 0.0) + extra
        self.measured = None


def cues():
    C = []
    R = rng(1940)
    rr = lambda: rng(int(R.integers(1 << 30)))
    add = C.append

    # ------------------------------------------------ Ambience beds
    # 1. Puget Sound coastal daytime air (shots 1-3, 0.0 - 21.0s)
    def amb_puget(dur, seed=101):
        def g():
            r = rng(seed)
            n = ns(dur)
            x = G.breeze(dur, r, 0.85, 0.18, 750)
            waves = bp(colored(n, r, 0.8), 120, 1400, 1) * (0.6 + 0.4 * smooth_noise(n, r, 0.25))
            x += st(waves * 0.45)
            x += pan(G.bird_chirps(dur, r, 0.15, "sparrow") * 0.04, 0.6)
            return fades(x, 0.3, 0.5), 0.0
        return g
    add(Cue(0.0, "amb_puget", "Puget Sound coastal air: breeze, gentle salt water waves, distant gulls",
            amb_puget(21.2, seed=101), -28, "bed", send=0.0))

    # 2. 42 mph Gale wind storm (shots 4-6, 21.0 - 43.5s)
    def amb_gale(dur, seed=102):
        def g():
            r = rng(seed)
            gw = G.gale_wind(dur, r, gust=0.45, f_whistle=440)
            flag = G.flag_flutter(dur, r) * 0.3
            x = st(gw * 1.1) + pan(flag, 0.3)
            return fades(x, 0.5, 0.5), 0.0
        return g
    add(Cue(21.0, "amb_gale", "42 mph howling gale wind through Tacoma Narrows canyon with vortex whistling",
            amb_gale(22.8, seed=102), -23, "bed", send=0.0))

    # 3. Puget Sound churning water & foam after collapse (40.0 - 50.0s)
    def amb_water_aftermath(dur, seed=103):
        def g():
            r = rng(seed)
            wb = G.water_bed(dur, r, close=1.2, slosh_rate=0.7)
            return fades(wb * 0.8, 0.4, 0.6), 0.0
        return g
    add(Cue(40.0, "amb_water_aftermath", "Puget Sound churning water foam & surging waves after 600 ft plunge",
            amb_water_aftermath(10.0, seed=103), -22, "bed", send=0.0))

    # 4. Modern bridge open trusses & clean breeze (58.0 - 67.5s)
    def amb_modern(dur, seed=104):
        def g():
            r = rng(seed)
            n = ns(dur)
            tw = G.truss_wind(dur, r)
            hwy = lp(colored(n, r, 0.9), 180, 2) * 0.25
            x = st(tw) + st(hwy)
            return fades(x, 0.4, 0.3), 0.0
        return g
    add(Cue(58.0, "amb_modern", "modern replacement bridge: laminar breeze whistling cleanly through open trusses",
            amb_modern(9.5, seed=104), -27, "bed", send=0.0))

    # ------------------------------------------------ Hook (0.0 - 4.5s)
    add(Cue(0.05, "cable_hum", "deep low suspension cable tension vibration",
            lambda: (st(reson(rng(1).standard_normal(ns(3.5)), 58, 12) * np.exp(-tt(3.5)/2.0) * 0.8), 0.0),
            -14, send=0.15))
    add(Cue(1.85, "steel_rip", "structural steel plate tearing on tore itself in half",
            lambda: (st(G.timber_tear(rng(2), 0.5) * 0.9), 0.0), -8, p=-0.2, send=0.2))
    add(Cue(3.20, "gentle_breeze", "deceptive soft breeze breath on gentle breeze",
            lambda: (st(G.whoosh(1.2, rng(3), 0.3, 300, 1200, 0.6, 0.1, 0.3) * 0.5), 0.0), -16, p=0.1, send=0.1))

    # ------------------------------------------------ Setting & 1940 Opening (4.5 - 9.5s)
    add(Cue(5.10, "vintage_car_rumble", "1940 flathead roadster engine chug & roll onto span",
            lambda: (st(G.vintage_car(4.2, rng(5), rpm=850)), 0.0), -14, p=-0.3, send=0.15))
    add(Cue(5.85, "vintage_horn_1", "classic 1940 dual-tone car horn on Tacoma Narrows",
            lambda: (st(G.vintage_horn(rng(6), dur=0.4)), 0.0), -7, p=0.2, send=0.2))
    add(Cue(7.20, "crowd_applause", "excited opening crowd cheering on pride of Washington state",
            lambda: (G.applause(2.6, rng(7), people=28) * 0.8, 0.0), -9, send=0.25))
    add(Cue(7.45, "crowd_hurrah", "crowd hurrah on pride of Washington",
            lambda: (st(G.hurrah(rng(8), 240, 1.0)), 0.0), -8, p=0.1, send=0.2))
    add(Cue(8.40, "vintage_horn_2", "second car horn answering in celebration",
            lambda: (st(G.vintage_horn(rng(9), dur=0.35)), 0.0), -10, p=-0.35, send=0.18))

    # ------------------------------------------------ Vertical Bouncing & Trampoline (9.5 - 21.0s)
    # Rhythmic bouncing of road deck & cars as Galloping Gertie undulates
    bounces = [9.95, 11.15, 12.35, 13.55, 14.75, 16.00, 17.20, 18.40]
    for k, tb in enumerate(bounces):
        add(Cue(tb, f"car_bounce_{k+1}", f"road deck vertical bounce & tire suspension squeak {k+1}",
                (lambda r=rr(): (st(G.car_bounce(r)), 0.0)), -9, p=(-0.25 if k % 2 == 0 else 0.25), send=0.12))
        add(Cue(tb + 0.12, f"deck_boing_{k+1}", f"trampoline vertical wave flex on span {k+1}",
                (lambda r=rr(): (st(G.deck_flex(r, 0.75)), 0.0)), -12, p=0.0, send=0.15))

    add(Cue(15.20, "toll_coin_drop", "75-cent toll coin clink into toll hopper on pay the toll",
            lambda: (st(G.toll_coin(rng(15))), 0.0), -6, p=0.3, send=0.1))
    add(Cue(16.10, "rollercoaster_whoosh", "thrilling rollercoaster air whoosh & passenger laughter",
            lambda: (st(G.rollercoaster_whoosh(2.2, rng(16)) * 0.9), 0.0), -7, send=0.2))
    add(Cue(18.75, "seasick_wobble", "queasy seasick wobble pitch dive on people get seasick",
            lambda: (st(G.seasick_wobble(rng(18))), 0.0), -8, p=-0.2, send=0.15))
    add(Cue(20.05, "ominous_creak", "subtle warning creak on nobody thinks its dangerous",
            lambda: (st(G.creak(0.8, rng(20), 70, 130, G.CHAIN, rough=0.15) * 0.7), 0.0), -12, p=0.1, send=0.2))

    # ------------------------------------------------ November 7 Gale & Torsional Twisting (21.0 - 37.0s)
    add(Cue(21.30, "gale_gust_swell", "42 mph gale wind swell on Until November seventh",
            lambda: (st(G.whoosh(2.2, rng(21), 0.9, 180, 1600, 0.9, 0.3, 0.3) * 1.2), 0.0), -6, send=0.18))
    add(Cue(23.10, "vortex_whistle", "howling vortex wind gust on forty mile an hour wind blows in",
            lambda: (st(G.breeze(2.4, rng(23), 1.3, 0.35, 1400)), 0.0), -7, p=-0.2, send=0.15))

    # The violent pivot: bridge abruptly changes from bounce to 45 degree twist
    add(Cue(26.30, "torsion_start", "SUDDEN SHUDDER: bounce stops, massive structural steel twists like a ribbon",
            lambda: (st(G.torsion_groan(2.8, rng(26), intensity=1.2)), 0.0), -4, send=0.2))
    add(Cue(28.20, "torsion_tilt_45", "screaming metal strain as road tilts 45 degrees one way",
            lambda: (st(G.torsion_groan(2.2, rng(28), intensity=1.4)), 0.0), -4, p=-0.35, send=0.22))
    add(Cue(30.25, "violent_snap_reversal", "VIOLENT SNAP: roadway whips 45 degrees the other way",
            lambda: (st(G.torsion_groan(2.4, rng(30), intensity=1.5)), 0.0), -3, p=0.35, send=0.25))
    add(Cue(30.40, "snap_whip_crack", "violent cable whiplash across deck",
            lambda: (st(G.chain_whip(rng(31))), 0.0), -4, p=0.2, send=0.2))

    # Coatsworth car curb slam and escape crawl
    add(Cue(31.10, "car_curb_slam", "Coatsworth car skidding & slamming violently against bridge curb",
            lambda: (st(G.car_curb_slam(rng(311))), 0.0), -3, p=0.25, send=0.2))

    crawls = [33.80, 34.25, 34.70, 35.15, 35.60]
    for k, tc in enumerate(crawls):
        add(Cue(tc, f"crawl_scuff_{k+1}", f"reporter frantic crawling hands and knees on concrete {k+1}",
                (lambda r=rr(): (st(G.crawling_knees(r)), 0.0)), -9, p=(-0.15 if k % 2 == 0 else 0.15), send=0.1))
    add(Cue(36.15, "escape_dive", "reporter leaping to safe anchor footing on escape",
            lambda: (st(G.stroll_step(rng(36), scuff=0.9) * 1.3), 0.0), -8, p=0.2, send=0.15))

    # ------------------------------------------------ The Snap & Plunge (37.0 - 44.0s)
    # Cable snaps like guitar strings
    add(Cue(37.82, "cable_snap_twang_1", "HANGER CABLE SNAPS like a guitar string: loud TWANG & PING",
            lambda: (st(G.cable_twang(rng(378), f0=330)), 0.0), 0, p=-0.3, send=0.25))
    add(Cue(38.20, "cable_snap_twang_2", "second cable snaps: high tension metallic twang",
            lambda: (st(G.cable_twang(rng(382), f0=440)), 0.0), -2, p=0.35, send=0.25))
    add(Cue(38.60, "cable_snap_twang_3", "third cable snaps in cascade whiplash",
            lambda: (st(G.cable_twang(rng(386), f0=260)), 0.0), -3, p=-0.2, send=0.25))

    # 600 ft highway collapse into Puget Sound
    add(Cue(39.10, "highway_tear", "600 feet of steel girder & concrete road tearing loose",
            lambda: (st(G.timber_tear(rng(391), 0.9) * 1.4), 0.0), -2, send=0.25))
    add(Cue(39.35, "concrete_fracture", "massive deck fracture crack",
            lambda: (st(G.wood_crack(rng(392)) * 1.2), 0.0), -3, p=0.1, send=0.2))
    add(Cue(39.80, "massive_puget_splash", "COLOSSAL IMPACT: 600 ft of highway plunges into Puget Sound with thunderous splash",
            lambda: (st(G.splash_big(rng(398)) * 1.8), 0.0), +2, send=0.3))
    add(Cue(39.82, "deep_water_boom", "deep low boom of 600 ft slab slamming water",
            lambda: (st(reson(rng(399).standard_normal(ns(3.5)), 52.0, 6) * np.exp(-tt(3.5)/0.9) * 1.6), 0.0), 0, send=0.3))
    add(Cue(41.20, "water_spray_rain", "massive Puget Sound spray & waves raining down across the sound",
            lambda: (st(G.water_bed(3.2, rng(412), close=1.4) * 0.8), 0.0), -8, send=0.2))

    # ------------------------------------------------ Tubby the Dog & Deadpan (44.0 - 48.0s)
    add(Cue(45.85, "tubby_whimper_1", "Tubby the cocker spaniel terrified cute whimper",
            lambda: (st(G.dog_whimper(rng(458), dur=0.5)), 0.0), -7, p=0.25, send=0.18))
    add(Cue(46.60, "tubby_whimper_2", "Tubby second plaintive little puppy whimper in car",
            lambda: (st(G.dog_whimper(rng(466), dur=0.45)), 0.0), -8, p=0.25, send=0.18))

    # ------------------------------------------------ Explanation: Paper Flutter & Vortexes (48.0 - 58.0s)
    add(Cue(48.60, "solid_wall_thud", "heavy solid steel plate girder metallic thud on solid steel walls",
            lambda: (st(G.modal(0.6, [(110, 1.2, 0.08), (240, 0.8, 0.05), (580, 0.5, 0.03)], rng(486))), 0.0),
            -7, p=-0.2, send=0.15))
    add(Cue(52.20, "paper_flutter_demo", "human air puff + rapid paper strip flutter on make it flutter",
            lambda: (st(G.paper_flutter(1.4, rng(522))), 0.0), -6, p=0.1, send=0.12))

    # Alternating aerodynamic vortex shedding
    add(Cue(53.60, "vortex_shed_1", "spinning vortex whoosh left on spinning vortexes",
            lambda: (st(G.vortex_whoosh(1.0, rng(536), f_center=480)), 0.0), -8, p=-0.4, send=0.15))
    add(Cue(54.60, "vortex_shed_2", "spinning vortex whoosh right pushing bridge back and forth",
            lambda: (st(G.vortex_whoosh(1.0, rng(546), f_center=620)), 0.0), -8, p=0.4, send=0.15))
    add(Cue(55.80, "vortex_shed_3", "resonance vortex feeding energy into each twist",
            lambda: (st(G.vortex_whoosh(1.1, rng(558), f_center=540)), 0.0), -7, p=-0.3, send=0.18))
    add(Cue(57.10, "twist_rip", "structural metal fatigue tear on until it ripped apart",
            lambda: (st(G.timber_tear(rng(571), 0.6) * 0.8), 0.0), -7, p=0.2, send=0.2))

    # ------------------------------------------------ Modern Trusses & Conclusion (58.0 - 67.5s)
    add(Cue(60.25, "girder_reject_thud", "girders banned dull iron thud on never used solid girders again",
            lambda: (st(G.modal(0.5, [(140, 1.0, 0.06), (320, 0.6, 0.03)], rng(602))), 0.0), -9, p=-0.2, send=0.12))
    add(Cue(62.60, "truss_breeze_clean", "clean aerodynamic wind whistling smoothly through open trusses",
            lambda: (st(G.truss_wind(2.8, rng(626)) * 0.9), 0.0), -12, send=0.15))
    add(Cue(64.60, "modern_traffic_hum", "distant modern traffic gliding smoothly across new bridge",
            lambda: (st(lp(colored(ns(2.0), rng(646), 0.8), 240, 2) * 0.35), 0.0), -16, p=0.3, send=0.1))
    add(Cue(65.45, "closed_forever_gate", "heavy iron toll gate & padlock shutting CLANG-CLUNK on closed forever",
            lambda: (st(G.gate_lock(rng(654))), 0.0), -3, p=0.0, send=0.25))

    return C


# ================================================================ Render
def render(v_ref, on_event=None):
    """v_ref = integrated loudness of the voice stem (stereo). Returns (stereo stem, cue list with measured levels)."""
    C = cues()
    out = np.zeros((2, N))
    send = np.zeros(N)
    for c in C:
        x, anchor = c.gen()
        x = np.asarray(x, float)
        x = pan(x, c.p) if x.ndim == 1 else x
        if c.cut is not None:
            k = ns(c.cut - (c.t - anchor))
            if 0 < k < x.shape[1]:
                x = fades(x[:, :k], 0.0, 0.02)
        tgt = v_ref + c.applied
        cur = momentary_max(x) if c.kind == "event" else integrated(x)
        if np.isfinite(cur):
            x = x * dbg(tgt - cur)
        if c.lpf:
            x = lp(x, c.lpf, 1)
        c.measured = momentary_max(x) - v_ref if c.kind == "event" else integrated(x) - v_ref
        t0 = c.t - anchor
        place(out, x, t0)
        if on_event:
            on_event(c, x, t0)
        if c.send > 0:
            G._place_mono(send, c.send * x.mean(0), t0)
    valley = make_ir(1.1, 77, pre=0.01, hf=1.6, early=[(0.09, 0.45, -0.5), (0.14, 0.3, 0.6), (0.23, 0.2, -0.2)])
    out += 0.55 * convolve_st(send, valley)
    out = hp(out, 25, 2)
    end = ns(T.DUR - 0.12)
    out[:, end:] *= np.linspace(1, 0, N - end)[None, :] ** 2
    return out, C
