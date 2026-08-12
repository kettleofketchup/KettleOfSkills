# Three.js Fundamentals: Common Patterns

## Cameras

**PerspectiveCamera** (most common):
```javascript
const camera = new THREE.PerspectiveCamera(75, w/h, 0.1, 1000);
camera.position.set(0, 5, 10);
camera.lookAt(0, 0, 0);
camera.updateProjectionMatrix(); // Call after changing fov/aspect/near/far
```

**OrthographicCamera** (no perspective distortion):
```javascript
const aspect = window.innerWidth / window.innerHeight;
const frustumSize = 10;
const camera = new THREE.OrthographicCamera(
  (frustumSize * aspect) / -2, (frustumSize * aspect) / 2,
  frustumSize / 2, frustumSize / -2, 0.1, 1000
);
```

**ArrayCamera** (multiple viewports):
```javascript
const cameras = [];
for (let i = 0; i < 4; i++) {
  const sub = new THREE.PerspectiveCamera(40, 1, 0.1, 100);
  sub.viewport = new THREE.Vector4(Math.floor(i % 2) * 0.5, Math.floor(i / 2) * 0.5, 0.5, 0.5);
  cameras.push(sub);
}
const arrayCamera = new THREE.ArrayCamera(cameras);
```

**CubeCamera** (environment maps for reflections):
```javascript
const cubeRenderTarget = new THREE.WebGLCubeRenderTarget(256);
const cubeCamera = new THREE.CubeCamera(0.1, 1000, cubeRenderTarget);
scene.add(cubeCamera);
material.envMap = cubeRenderTarget.texture;
cubeCamera.position.copy(reflectiveMesh.position);
cubeCamera.update(renderer, scene); // Expensive - call selectively
```

## Proper Cleanup

```javascript
function dispose() {
  mesh.geometry.dispose();
  if (Array.isArray(mesh.material)) {
    mesh.material.forEach((m) => m.dispose());
  } else {
    mesh.material.dispose();
  }
  texture.dispose();
  scene.remove(mesh);
  renderer.dispose();
}
```

## Clock for Animation

```javascript
const clock = new THREE.Clock();

function animate() {
  const delta = clock.getDelta();    // Time since last frame (seconds)
  const elapsed = clock.getElapsedTime();

  mesh.rotation.y += delta * 0.5;   // Consistent speed regardless of framerate
  object.position.y = Math.sin(elapsed * 2) * 5;

  requestAnimationFrame(animate);
  renderer.render(scene, camera);
}
```

## Responsive Canvas

```javascript
function onWindowResize() {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
}
window.addEventListener("resize", onWindowResize);
```

## Loading Manager

```javascript
const manager = new THREE.LoadingManager();
manager.onStart = (url, loaded, total) => console.log("Started loading");
manager.onLoad = () => console.log("All loaded");
manager.onProgress = (url, loaded, total) => console.log(`${loaded}/${total}`);
manager.onError = (url) => console.error(`Error loading ${url}`);

const textureLoader = new THREE.TextureLoader(manager);
const gltfLoader = new GLTFLoader(manager);
```

## Curves

```javascript
const curve = new THREE.CubicBezierCurve3(
  new THREE.Vector3(-10, 0, 0),
  new THREE.Vector3(-5, 15, 0),
  new THREE.Vector3(20, 15, 0),
  new THREE.Vector3(10, 0, 0)
);
const points = curve.getPoints(50);
const geometry = new THREE.BufferGeometry().setFromPoints(points);
const line = new THREE.Line(geometry, material);
const point = curve.getPoint(0.5); // Get point at t (0-1)
```

## Performance Tips

1. **Limit draw calls**: Merge geometries, use instancing, atlas textures
2. **Frustum culling**: Enabled by default, ensure bounding boxes are correct
3. **LOD (Level of Detail)**: Use `THREE.LOD` for distance-based mesh switching
4. **Object pooling**: Reuse objects instead of creating/destroying
5. **Avoid `getWorldPosition` in loops**: Cache results

```javascript
const lod = new THREE.LOD();
lod.addLevel(highDetailMesh, 0);
lod.addLevel(medDetailMesh, 50);
lod.addLevel(lowDetailMesh, 100);
scene.add(lod);
```
