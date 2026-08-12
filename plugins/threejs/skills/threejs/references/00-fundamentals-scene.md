# Three.js Fundamentals: Scene, Renderer, Object3D

## Quick Start

```javascript
import * as THREE from "three";

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
document.body.appendChild(renderer.domElement);

const geometry = new THREE.BoxGeometry(1, 1, 1);
const material = new THREE.MeshStandardMaterial({ color: 0x00ff00 });
const cube = new THREE.Mesh(geometry, material);
scene.add(cube);
scene.add(new THREE.AmbientLight(0xffffff, 0.5));
const dirLight = new THREE.DirectionalLight(0xffffff, 1);
dirLight.position.set(5, 5, 5);
scene.add(dirLight);
camera.position.z = 5;

function animate() {
  requestAnimationFrame(animate);
  cube.rotation.x += 0.01;
  cube.rotation.y += 0.01;
  renderer.render(scene, camera);
}
animate();

window.addEventListener("resize", () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});
```

## Scene

```javascript
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x000000);
scene.background = texture;        // Skybox texture
scene.background = cubeTexture;    // Cubemap
scene.environment = envMap;        // Environment map for PBR
scene.fog = new THREE.Fog(0xffffff, 1, 100);      // Linear fog
scene.fog = new THREE.FogExp2(0xffffff, 0.02);    // Exponential fog
```

## WebGLRenderer

```javascript
const renderer = new THREE.WebGLRenderer({
  canvas: document.querySelector("#canvas"),
  antialias: true,
  alpha: true,
  powerPreference: "high-performance",
  preserveDrawingBuffer: true,
});
renderer.setSize(width, height);
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.0;
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.setClearColor(0x000000, 1);
renderer.render(scene, camera);
```

## Object3D

Base class for Mesh, Group, Light, Camera.

```javascript
const obj = new THREE.Object3D();
obj.position.set(x, y, z);
obj.rotation.set(x, y, z);      // Euler angles (radians)
obj.quaternion.set(x, y, z, w);
obj.scale.set(x, y, z);
obj.getWorldPosition(targetVector);
obj.getWorldQuaternion(targetQuaternion);
obj.add(child);
obj.remove(child);
obj.visible = false;
obj.layers.set(1);
obj.traverse((child) => {
  if (child.isMesh) child.material.color.set(0xff0000);
});
obj.matrixAutoUpdate = true;
obj.updateMatrix();
obj.updateMatrixWorld(true);
```

## Group and Mesh

```javascript
const group = new THREE.Group();
group.add(mesh1, mesh2);
scene.add(group);
group.position.x = 5;

const mesh = new THREE.Mesh(geometry, material);
mesh.castShadow = true;
mesh.receiveShadow = true;
mesh.frustumCulled = true;
mesh.renderOrder = 10;
```

## Coordinate System

Three.js uses a right-handed system: +X right, +Y up, +Z toward viewer.

```javascript
const axesHelper = new THREE.AxesHelper(5);
scene.add(axesHelper); // Red=X, Green=Y, Blue=Z
```
