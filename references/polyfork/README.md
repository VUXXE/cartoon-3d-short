# Polyfork 3D Asset Catalog for Cartoon 3D Shorts

**Polyfork** (https://polyfork.dev) is an extensive open library of low-poly 3D models specifically designed for scene layout and procedural worlds.

- **3,086 premade assets** across **47 themed kits**
- Native low triangle counts (typically 300 to 2,000 tris per asset) — perfect for real-time WebGL in Three.js and fast Remotion rendering
- Consistent conventions: Y-up, meter scale, models rest on y=0 ground level, front faces +Z
- Standard GLB format hosted on fast CDN (`https://polyfork.dev/cdn/<asset_id>.glb`)
- Full catalog index: `catalog.json` (1.2 MB) in this directory

---

## 47 Themed Kits Summary

| Kit Name | Kit ID | Parts | Theme / Best For |
| :--- | :--- | :--- | :--- |
| **Medieval Village** | `medieval-village-kit-ca0b43` | 60 | Castles, taverns, timber houses, carts, village props |
| **Medieval Japan** | `medieval-japan-cb01ad` | 60 | Pagodas, torii gates, lanterns, shrines, cherry trees |
| **Little Tokyo** | `japanese-suburban-city-street-baa482` | 57 | Suburban houses, vending machines, utility poles |
| **Frontier Town** | `frontier-town-a0085b` | 61 | Western saloons, hitching posts, barrels, wagons |
| **Nature & Forest** | `nature-forest-kit-f29d6a` | 59 | Oak, pine, birch, rocks, logs, stumps, foliage |
| **Cozy Farm** | `cozy-farm-cc979f` | 60 | Barns, windmills, tractors, fences, crops, apple trees |
| **Campground & Lake** | `campground-lake-ad32b0` | 62 | Cabins, tents, canoes, campfires, docks, pines |
| **Countryside Railway** | `countryside-railway-9b4c57` | 102 | Steam trains, tracks, stations, signals, water towers |
| **New York City** | `nyc-city-kit-fbca88` | 81 | Brownstones, skyscrapers, fire escapes, hot dog stands |
| **Retro Cars** | `racing-cars-kit-660d53` | 29 | Vintage race cars, roadsters, trucks, speedsters |
| **Pirate Cove** | `pirate-cove-2ebea4` | 61 | Galleons, rowboats, palm trees, treasure chests, docks |
| **Space Base** | `space-base-kit-cf65de` | 61 | Moonbases, rovers, airlocks, solar panels, domes |
| **Spaceship Wars** | `spaceship-wars-kit-234642` | 29 | Starfighters, battle cruisers, landing pads, turrets |
| **Hospital** | `hospital-kit-2ebfcb` | 57 | Ambulances, hospital beds, gurneys, medical rooms |
| **Roadside Americana** | `roadside-americana-50d40c` | 60 | Diners, gas stations, motel signs, pickup trucks |
| **Dungeon & Crypt** | `dungeon-crypt-c27d93` | 67 | Sarcophagi, iron cages, stone pillars, torches, chests |
| **Dragons Lair** | `dragons-lair-dark-dragon-782570` | 58 | Obsidian rocks, dragon bones, gold piles, stalagmites |
| **Prehistoric Valley** | `prehistoric-valley-8638dc` | 59 | Volcanos, prehistoric trees, giant bones, caves |
| **Airport** | `airport-43b137` | 31 | Airplanes, hangars, control towers, luggage carts |
| **Construction Site** | `construction-site-9e40b0` | 62 | Cranes, bulldozers, scaffolds, traffic cones, pipes |
| **Hotel Casino** | `casino-3dd029` | 122 | Roulette tables, slot machines, neon signs, velvet ropes |
| **Coral Reef** | `coral-reef-a7128a` | 54 | Anemones, corals, starfish, sunken anchors |
| **3D UI kit** | `3d-ui-kit-5635f7` | 61 | Floating icons, badges, gizmos, dialog panels, dials |

---

## CLI Helper Tool (`scripts/polyfork.py`)

Run queries, list kits, and download models with one command:

### 1. Search Models
```bash
# Search by keyword
python scripts/polyfork.py search "house"

# Filter by kit and max triangles
python scripts/polyfork.py search "tree" --kit nature-forest-kit-f29d6a --max-triangles 1000

# Search by type (building, prop, vehicle, animal, character, terrain)
python scripts/polyfork.py search "car" --type vehicle
```

### 2. List & Inspect Kits
```bash
# List all 47 kits
python scripts/polyfork.py kits

# Filter kits
python scripts/polyfork.py kits --search "japan"

# Inspect all assets inside a kit
python scripts/polyfork.py kit medieval-village-kit-ca0b43
```

### 3. Download Models
```bash
# Download a specific GLB model into your project's public/models folder
python scripts/polyfork.py download a-frame-cabin-6cb550 --out-dir ./public/models

# Download an entire kit (batch download)
python scripts/polyfork.py download-kit frontier-town-a0085b --out-dir ./public/models
```

### 4. Generate Integration Snippets
```bash
python scripts/polyfork.py snippet a-frame-cabin-6cb550
```

---

## Three.js & Remotion Integration

Polyfork models plug directly into `cartoon-3d-short`'s scenery batching system:

```typescript
import { staticFile } from "remotion";
import { GLTFLoader } from "three/examples/jsm/loaders/GLTFLoader.js";
import { Batch, toLambert, V } from "./build";
import { loadPolyforkKit, placePolyforkProp } from "./polyfork";

// In your world asset loader:
const polyforkKit = await loadPolyforkKit([
  "a-frame-cabin-6cb550",
  "apple-tree-ef0ba0",
  "lantern-post-0922a9"
]);

// In buildTown / buildScenery:
// placePolyforkProp handles height scaling, ground alignment, and material conversion to two-tone Lambert
placePolyforkProp(batch, polyforkKit["a-frame-cabin-6cb550"], 20, D0, -45, 6.5, Math.PI / 4);
placePolyforkProp(batch, polyforkKit["apple-tree-ef0ba0"], 12, D0, -38, 4.0);
```
