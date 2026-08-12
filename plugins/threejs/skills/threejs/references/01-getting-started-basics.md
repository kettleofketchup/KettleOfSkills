# Getting Started with Three.js: Core Setup

## Essential Components

Every Three.js app needs 3 core elements:

### 1. Scene
```javascript
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x000000);
scene.fog = new THREE.Fog(0xffffff, 1, 5000);
```

### 2. Camera
**PerspectiveCamera** (most common):
```javascript
const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
camera.position.set(0, 0, 5);
camera.lookAt(0, 0, 0);
```

**OrthographicCamera** (no perspective distortion):
```javascript
const camera = new THREE.OrthographicCamera(left, right, top, bottom, near, far);
```

### 3. Renderer
```javascript
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setPixelRatio(window.devicePixelRatio);
document.body.appendChild(renderer.domElement);
```

## Basic Geometries

```javascript
new THREE.BoxGeometry(width, height, depth);
new THREE.SphereGeometry(radius, widthSegments, heightSegments);
new THREE.PlaneGeometry(width, height);
new THREE.CylinderGeometry(radiusTop, radiusBottom, height, radialSegments);
new THREE.ConeGeometry(radius, height, radialSegments);
new THREE.TorusGeometry(radius, tube, radialSegments, tubularSegments);
```

## Basic Materials

```javascript
// Unlit, flat color
new THREE.MeshBasicMaterial({ color: 0xff0000 });

// PBR, responds to lights
new THREE.MeshStandardMaterial({ color: 0x00ff00, metalness: 0.5, roughness: 0.5 });

// Specular highlights
new THREE.MeshPhongMaterial({ color: 0x0000ff, shininess: 100 });
```

## Creating Meshes

```javascript
const geometry = new THREE.BoxGeometry(1, 1, 1);
const material = new THREE.MeshStandardMaterial({ color: 0x00ff00 });
const cube = new THREE.Mesh(geometry, material);
scene.add(cube);
```

## Basic Lights

Materials (except Basic) need lights:

```javascript
// Global illumination
const ambient = new THREE.AmbientLight(0x404040);
scene.add(ambient);

// Sun-like, infinite distance
const directional = new THREE.DirectionalLight(0xffffff, 1);
directional.position.set(5, 5, 5);
scene.add(directional);

// Lightbulb, radiates all directions
const point = new THREE.PointLight(0xff0000, 1, 100);
point.position.set(0, 10, 0);
scene.add(point);
```

## Animation Loop

```javascript
function animate() {
  requestAnimationFrame(animate);
  cube.rotation.x += 0.01;
  cube.rotation.y += 0.01;
  renderer.render(scene, camera);
}
animate();
```

## Handle Window Resize

```javascript
window.addEventListener('resize', () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});
```
