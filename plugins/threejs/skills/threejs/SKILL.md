---
name: threejs
description: Build 3D web apps with Three.js (WebGL/WebGPU). Use for 3D scenes, animations, custom shaders, PBR materials, VR/XR experiences, games, data visualizations, product configurators.
license: MIT
version: 2.0.0
---

# Three.js Development

Build high-performance 3D web applications using Three.js - a cross-browser WebGL/WebGPU library.

## When to Use This Skill

Use when working with:
- 3D scenes, models, animations, or visualizations
- WebGL/WebGPU rendering and graphics programming
- Interactive 3D experiences (games, configurators, data viz)
- Camera controls, lighting, materials, or shaders
- Loading 3D assets (GLTF, FBX, OBJ) or textures
- Post-processing effects (bloom, depth of field, SSAO)
- Physics simulations, VR/XR experiences, or spatial audio
- Performance optimization (instancing, LOD, frustum culling)

## Quick Start Pattern

```javascript
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, window.innerWidth/window.innerHeight, 0.1, 1000);
const renderer = new THREE.WebGLRenderer();
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);

const geometry = new THREE.BoxGeometry();
const material = new THREE.MeshStandardMaterial({ color: 0x00ff00 });
const cube = new THREE.Mesh(geometry, material);
scene.add(cube);

const light = new THREE.DirectionalLight(0xffffff, 1);
light.position.set(5, 5, 5);
scene.add(light);
scene.add(new THREE.AmbientLight(0x404040));

function animate() {
  requestAnimationFrame(animate);
  cube.rotation.x += 0.01;
  cube.rotation.y += 0.01;
  renderer.render(scene, camera);
}
animate();
```

## References

### Level 1: Fundamentals
- `references/00-fundamentals-scene.md` - Scene, Renderer, Object3D, Group, Mesh
- `references/00-fundamentals-math.md` - Vector3, Matrix4, Quaternion, Color, MathUtils
- `references/00-fundamentals-patterns.md` - Camera types, Clock, cleanup, curves, LOD

### Level 2: Getting Started
- `references/01-getting-started-basics.md` - Scene/Camera/Renderer setup, basic geometries, materials, lights
- `references/01-getting-started-hierarchy.md` - Object hierarchy, transforms, traversal, helpers

### Level 3: Common Topics
- **Asset Loading**: `references/02-loaders-standard.md`, `references/02-loaders-compressed.md`
- **Textures**: `references/03-textures-types.md`, `references/03-textures-config.md`
- **Cameras**: `references/04-cameras-types.md`, `references/04-cameras-controls.md`
- **Lights**: `references/05-lights-types.md`, `references/05-lights-helpers.md`
- **Animations**: `references/06-animations-system.md`, `references/06-animations-keyframes.md`
- **Math**: `references/07-math-vectors.md`, `references/07-math-color-raycaster.md`
- **Geometry**: `references/18-geometry-builtin.md`, `references/18-geometry-buffer.md`, `references/18-geometry-instanced.md`, `references/18-geometry-utils.md`
- **Materials**: `references/11-materials-standard.md`, `references/11-materials-physical.md`, `references/11-materials-shader.md`, `references/11-materials-advanced-pbr.md`

### Level 4: Interactive and Effects
- **Interaction**: `references/08-interaction-raycasting.md`, `references/08-interaction-controls.md`
- **Post-Processing**: `references/09-postprocessing-passes.md`, `references/09-postprocessing-custom.md`
- **Controls (Addons)**: `references/10-controls-orbit.md`, `references/10-controls-fps.md`

### Level 5: Advanced Rendering
- **Performance**: `references/12-performance-instancing.md`, `references/12-performance-textures.md`
- **Node Materials (TSL)**: `references/13-node-materials-basics.md`, `references/13-node-materials-advanced.md`

### Level 6: Specialized
- **Physics**: `references/14-physics-engines.md`
- **VR/XR**: `references/14-vr-xr.md`
- **Advanced Loaders**: `references/15-specialized-loaders-3d.md`, `references/15-specialized-loaders-media.md`
- **WebGPU**: `references/16-webgpu-renderer.md`, `references/16-webgpu-compute.md`
- **Shaders**: `references/17-shader-basics.md`, `references/17-shader-patterns.md`, `references/17-shader-extending.md`, `references/17-shader-effects.md`

## External Resources

- Official Docs: https://threejs.org/docs/
- Examples: https://threejs.org/examples/
- Editor: https://threejs.org/editor/
- Discord: https://discord.gg/56GBJwAnUS
