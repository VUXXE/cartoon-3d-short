// Polyfork Premade Asset Integration for Cartoon 3D Short
// Loads low-poly models from Polyfork (https://polyfork.dev), converts materials to two-tone Lambert,
// and integrates with the scene batching and ink outline post-processing.
import * as THREE from "three";
import { staticFile } from "remotion";
import { GLTFLoader } from "three/examples/jsm/loaders/GLTFLoader.js";
import { Batch, toLambert, V, Kit } from "./build";

const loader = new GLTFLoader();
const modelCache = new Map<string, THREE.Object3D>();
const boxCache = new Map<THREE.Object3D, THREE.Box3>();

/**
 * Load one or more Polyfork GLB models from the project's public/ folder.
 * Models should be downloaded beforehand using:
 *   python scripts/polyfork.py download <asset_id> --out-dir ./public/models
 *
 * @param assetIds Array of Polyfork asset IDs (e.g. ["apple-tree-ef0ba0", "a-frame-cabin-6cb550"])
 * @param subDir Subdirectory inside public/ (default: "models")
 */
export const loadPolyforkKit = async (
  assetIds: string[],
  subDir = "models"
): Promise<Kit> => {
  const kit: Kit = {};
  await Promise.all(
    assetIds.map(async (id) => {
      if (modelCache.has(id)) {
        kit[id] = modelCache.get(id)!;
        return;
      }
      try {
        const filePath = staticFile(`${subDir}/${id}.glb`);
        const gltf = await loader.loadAsync(filePath);
        modelCache.set(id, gltf.scene);
        kit[id] = gltf.scene;
      } catch (err) {
        console.warn(`[Polyfork] Could not load ${id}.glb from public/${subDir}/:`, err);
      }
    })
  );
  return kit;
};

/**
 * Place a Polyfork model into the static scenery Batch.
 * Automatically aligns the model's base to y, scales to desired height, converts materials
 * to two-tone Lambert, and merges into the static draw batch.
 *
 * @param b Static Batch instance
 * @param model THREE.Object3D loaded from Polyfork
 * @param x World X coordinate
 * @param y World Y coordinate (ground level)
 * @param z World Z coordinate
 * @param height Optional target height in meters (if omitted, keeps Polyfork native meter scale)
 * @param yaw Rotation around Y axis in radians
 */
export const placePolyforkProp = (
  b: Batch,
  model: THREE.Object3D,
  x: number,
  y: number,
  z: number,
  height?: number,
  yaw = 0
) => {
  if (!model) return;
  let box = boxCache.get(model);
  if (!box) {
    box = new THREE.Box3().setFromObject(model);
    boxCache.set(model, box);
  }

  const modelHeight = Math.max(0.01, box.max.y - box.min.y);
  const scale = height ? height / modelHeight : 1.0;
  const yOffset = box.min.y * scale;

  const mat = new THREE.Matrix4().compose(
    V(x, y - yOffset, z),
    new THREE.Quaternion().setFromAxisAngle(V(0, 1, 0), yaw),
    V(scale, scale, scale)
  );

  b.addObject(model, mat);
};

/**
 * Clone a Polyfork model as an independent object for foreground framing (FOREGROUND) or moving elements.
 */
export const clonePolyforkModel = (
  model: THREE.Object3D,
  height?: number
): THREE.Object3D | null => {
  if (!model) return null;
  let box = boxCache.get(model);
  if (!box) {
    box = new THREE.Box3().setFromObject(model);
    boxCache.set(model, box);
  }

  const c = model.clone(true);
  const modelHeight = Math.max(0.01, box.max.y - box.min.y);
  const scale = height ? height / modelHeight : 1.0;

  c.traverse((child) => {
    const mesh = child as THREE.Mesh;
    if (mesh.isMesh) {
      mesh.material = toLambert(
        Array.isArray(mesh.material) ? mesh.material[0] : mesh.material
      );
      mesh.castShadow = false;
      mesh.receiveShadow = true;
    }
  });

  c.scale.set(scale, scale, scale);
  return c;
};
