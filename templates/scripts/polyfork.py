#!/usr/bin/env python3
"""
Polyfork 3D Asset Tool for Cartoon 3D Short Skill.
Browse, search, inspect, and download low-poly 3D models from Polyfork (3,086+ premade assets across 47 themed kits).

Features:
  - Search models by keyword, kit, or type
  - List and inspect themed kits (Medieval, Little Tokyo, NYC, Nature, Space, Sci-Fi, etc.)
  - Download optimized GLB models directly to your Remotion public/ directory
  - Generate Three.js / Remotion integration code snippets with two-tone shading and ink outline support

Usage:
  python polyfork.py search "tree"
  python polyfork.py search "house" --kit medieval-village-kit-ca0b43
  python polyfork.py kits
  python polyfork.py kit frontier-town-a0085b
  python polyfork.py info a-frame-cabin-6cb550
  python polyfork.py download a-frame-cabin-6cb550 --out-dir ./public/models
  python polyfork.py snippet a-frame-cabin-6cb550
"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.error

# Resolve catalog path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
POSSIBLE_CATALOG_PATHS = [
    os.path.join(SCRIPT_DIR, "..", "references", "polyfork", "catalog.json"),
    os.path.join(SCRIPT_DIR, "references", "polyfork", "catalog.json"),
    os.path.expanduser("~/.agents/skills/cartoon-3d-short/references/polyfork/catalog.json"),
    "/home/exu/.t3/scratch/2026-11-07-https-github-com-mromidev-claude-7a9c895e/references/polyfork/catalog.json",
]

def load_catalog():
    for p in POSSIBLE_CATALOG_PATHS:
        if os.path.exists(p):
            with open(p, "r", encoding="utf-8") as f:
                return json.load(f)
    print("Error: Could not locate catalog.json. Searched locations:", file=sys.stderr)
    for p in POSSIBLE_CATALOG_PATHS:
        print(f"  - {p}", file=sys.stderr)
    sys.exit(1)

USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"

def download_file(url: str, dest_path: str):
    os.makedirs(os.path.dirname(os.path.abspath(dest_path)), exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req) as resp, open(dest_path, "wb") as out_file:
            total_size = int(resp.headers.get("Content-Length", 0))
            chunk_size = 16384
            downloaded = 0
            while True:
                chunk = resp.read(chunk_size)
                if not chunk:
                    break
                out_file.write(chunk)
                downloaded += len(chunk)
        return True
    except urllib.error.HTTPError as e:
        print(f"HTTP Error {e.code}: {e.reason} for {url}", file=sys.stderr)
        return False
    except Exception as e:
        print(f"Error downloading {url}: {e}", file=sys.stderr)
        return False

def cmd_search(args, catalog):
    query = args.query.lower().strip()
    kit_filter = args.kit.lower().strip() if args.kit else None
    type_filter = args.type.lower().strip() if args.type else None
    max_tri = args.max_triangles

    results = []
    for asset in catalog.get("assets", []):
        a_id = (asset.get("id") or "").lower()
        title = (asset.get("title") or "").lower()
        a_type = (asset.get("type") or "").lower()
        a_kit = (asset.get("kit") or "").lower()
        tri = asset.get("triangles", 0)

        if query and (query not in a_id and query not in title):
            continue
        if kit_filter and kit_filter not in a_kit:
            continue
        if type_filter and type_filter != a_type:
            continue
        if max_tri and tri > max_tri:
            continue

        results.append(asset)

    print(f"Found {len(results)} matching assets:")
    for a in results[:args.limit]:
        print(f"  [{a['id']}] {a['title']} | Type: {a.get('type')} | Kit: {a.get('kit')} | Tris: {a.get('triangles')}")
        print(f"     GLB: {a.get('glb')}")

    if len(results) > args.limit:
        print(f"\n... and {len(results) - args.limit} more. Use --limit to see more results.")

def cmd_kits(args, catalog):
    search = args.search.lower().strip() if args.search else None
    kits = catalog.get("kits", [])
    if search:
        kits = [k for k in kits if search in (k.get("title") or "").lower() or search in (k.get("id") or "").lower()]

    print(f"Available Kits ({len(kits)} kits):")
    for k in sorted(kits, key=lambda x: x.get("title", "")):
        print(f"  - {k['title']} (id: {k['id']}) — {k.get('parts', '?')} parts")
        print(f"    Page: {k.get('page')}")

def cmd_kit(args, catalog):
    kit_id = args.kit_id.lower().strip()
    matching_kit = None
    for k in catalog.get("kits", []):
        if kit_id in (k.get("id") or "").lower() or kit_id in (k.get("title") or "").lower():
            matching_kit = k
            break

    if not matching_kit:
        print(f"Error: Kit '{kit_id}' not found.", file=sys.stderr)
        return

    full_id = matching_kit["id"]
    print(f"Kit: {matching_kit['title']} (ID: {full_id})")
    print(f"Total parts: {matching_kit.get('parts')}")
    print(f"URL: {matching_kit.get('page')}")
    print("\nAssets in this kit:")

    kit_assets = [a for a in catalog.get("assets", []) if (a.get("kit") or "").lower() == full_id.lower()]
    for a in kit_assets:
        print(f"  - [{a['id']}] {a['title']} ({a.get('type')}) — {a.get('triangles')} tris")
        print(f"    GLB: {a.get('glb')}")

def cmd_info(args, catalog):
    asset_id = args.asset_id.strip()
    for a in catalog.get("assets", []):
        if a["id"].lower() == asset_id.lower():
            print(f"Asset: {a['title']} (ID: {a['id']})")
            print(f"  Type:       {a.get('type')}")
            print(f"  Kit:        {a.get('kit')}")
            print(f"  Triangles:  {a.get('triangles')}")
            print(f"  GLB:        {a.get('glb')}")
            print(f"  Module:     {a.get('module')}")
            print(f"  Page:       {a.get('page')}")
            print(f"  Thumbnail:  {a.get('thumbnail')}")
            return
    print(f"Asset '{asset_id}' not found.", file=sys.stderr)

def cmd_download(args, catalog):
    asset_id = args.asset_id.strip()
    target_asset = None
    for a in catalog.get("assets", []):
        if a["id"].lower() == asset_id.lower():
            target_asset = a
            break

    if not target_asset:
        print(f"Asset '{asset_id}' not found in catalog.", file=sys.stderr)
        return

    out_dir = args.out_dir
    os.makedirs(out_dir, exist_ok=True)
    dest_path = os.path.join(out_dir, f"{target_asset['id']}.glb")
    print(f"Downloading {target_asset['title']} [{target_asset['id']}] to {dest_path}...")
    if download_file(target_asset["glb"], dest_path):
        size = os.path.getsize(dest_path)
        print(f"Success! Saved {dest_path} ({size/1024:.1f} KB)")
    else:
        print("Download failed.", file=sys.stderr)

def cmd_download_kit(args, catalog):
    kit_id = args.kit_id.lower().strip()
    matching_kit = None
    for k in catalog.get("kits", []):
        if kit_id in (k.get("id") or "").lower() or kit_id in (k.get("title") or "").lower():
            matching_kit = k
            break

    if not matching_kit:
        print(f"Kit '{kit_id}' not found.", file=sys.stderr)
        return

    full_id = matching_kit["id"]
    kit_assets = [a for a in catalog.get("assets", []) if (a.get("kit") or "").lower() == full_id.lower()]
    out_dir = os.path.join(args.out_dir, full_id)
    os.makedirs(out_dir, exist_ok=True)

    print(f"Downloading {len(kit_assets)} assets from kit '{matching_kit['title']}' into {out_dir}...")
    success = 0
    for idx, a in enumerate(kit_assets, 1):
        dest_path = os.path.join(out_dir, f"{a['id']}.glb")
        if os.path.exists(dest_path):
            print(f"  [{idx}/{len(kit_assets)}] Skipping {a['id']} (already exists)")
            success += 1
            continue
        print(f"  [{idx}/{len(kit_assets)}] Downloading {a['title']} [{a['id']}]...")
        if download_file(a["glb"], dest_path):
            success += 1
        else:
            print(f"    Failed: {a['id']}")
    print(f"\nFinished kit download: {success}/{len(kit_assets)} models downloaded.")

def cmd_snippet(args, catalog):
    asset_id = args.asset_id.strip()
    target_asset = None
    for a in catalog.get("assets", []):
        if a["id"].lower() == asset_id.lower():
            target_asset = a
            break

    if not target_asset:
        print(f"Asset '{asset_id}' not found in catalog.", file=sys.stderr)
        return

    a_id = target_asset["id"]
    title = target_asset["title"]
    tris = target_asset.get("triangles", 0)

    snippet = f"""// --- Polyfork Premade Asset: {title} ({a_id}, {tris} tris) ---
// 1. Download model:
//    python scripts/polyfork.py download {a_id} --out-dir public/models/

// 2. In your Remotion build.ts / world.ts loader:
import {{ staticFile }} from "remotion";
import {{ GLTFLoader }} from "three/examples/jsm/loaders/GLTFLoader.js";

// Add to your asset loader:
const loadAsset = async () => {{
  const loader = new GLTFLoader();
  const gltf = await loader.loadAsync(staticFile("models/{a_id}.glb"));
  return gltf.scene;
}};

// 3. In buildTown / buildScenery, convert materials to two-tone Lambert and place in scene:
export const place{title.replace(' ', '').replace('-', '')} = (batch: Batch, model: THREE.Object3D, x: number, y: number, z: number, scale = 1, yaw = 0) => {{
  const m = new THREE.Matrix4().compose(
    new THREE.Vector3(x, y, z),
    new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(0, 1, 0), yaw),
    new THREE.Vector3(scale, scale, scale)
  );
  batch.addObject(model, m); // Automatically converts materials with toLambert()
}};
"""
    print(snippet)

def main():
    parser = argparse.ArgumentParser(description="Polyfork 3D Asset Tool for Cartoon 3D Short Skill")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # search
    p_search = subparsers.add_parser("search", help="Search Polyfork assets")
    p_search.add_argument("query", nargs="?", default="", help="Search query (name or keyword)")
    p_search.add_argument("--kit", help="Filter by kit ID or name")
    p_search.add_argument("--type", help="Filter by type (building, prop, vehicle, animal, character, terrain)")
    p_search.add_argument("--max-triangles", type=int, help="Maximum triangle count")
    p_search.add_argument("--limit", type=int, default=20, help="Max results to display")

    # kits
    p_kits = subparsers.add_parser("kits", help="List all 47 Polyfork kits")
    p_kits.add_argument("--search", help="Filter kits by keyword")

    # kit
    p_kit = subparsers.add_parser("kit", help="Inspect a specific kit")
    p_kit.add_argument("kit_id", help="Kit ID or title")

    # info
    p_info = subparsers.add_parser("info", help="Get full metadata for an asset")
    p_info.add_argument("asset_id", help="Asset ID (e.g. a-frame-cabin-6cb550)")

    # download
    p_dl = subparsers.add_parser("download", help="Download asset GLB")
    p_dl.add_argument("asset_id", help="Asset ID")
    p_dl.add_argument("--out-dir", default="./public/models", help="Output directory (default: ./public/models)")

    # download-kit
    p_dlk = subparsers.add_parser("download-kit", help="Download all GLBs in a kit")
    p_dlk.add_argument("kit_id", help="Kit ID")
    p_dlk.add_argument("--out-dir", default="./public/models", help="Output directory")

    # snippet
    p_snip = subparsers.add_parser("snippet", help="Generate Three.js / Remotion code snippet")
    p_snip.add_argument("asset_id", help="Asset ID")

    args = parser.parse_args()
    catalog = load_catalog()

    if args.command == "search":
        cmd_search(args, catalog)
    elif args.command == "kits":
        cmd_kits(args, catalog)
    elif args.command == "kit":
        cmd_kit(args, catalog)
    elif args.command == "info":
        cmd_info(args, catalog)
    elif args.command == "download":
        cmd_download(args, catalog)
    elif args.command == "download-kit":
        cmd_download_kit(args, catalog)
    elif args.command == "snippet":
        cmd_snippet(args, catalog)

if __name__ == "__main__":
    main()
