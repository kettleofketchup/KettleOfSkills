# Camera Controls: OrbitControls and Map-Style

## OrbitControls (Most Common)

Orbit camera around a target:

```javascript
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

const controls = new OrbitControls(camera, renderer.domElement);
controls.target.set(0, 0, 0);

// Damping (smooth motion)
controls.enableDamping = true;
controls.dampingFactor = 0.05;

// Zoom limits
controls.minDistance = 5;
controls.maxDistance = 50;

// Rotation limits
controls.minPolarAngle = 0;
controls.maxPolarAngle = Math.PI / 2;  // prevent going below ground
controls.minAzimuthAngle = -Math.PI / 4;
controls.maxAzimuthAngle = Math.PI / 4;

// Behavior
controls.enablePan = true;
controls.enableZoom = true;
controls.autoRotate = true;
controls.autoRotateSpeed = 2.0;

// Mouse buttons
controls.mouseButtons = {
  LEFT: THREE.MOUSE.ROTATE,
  MIDDLE: THREE.MOUSE.DOLLY,
  RIGHT: THREE.MOUSE.PAN
};

// In animation loop
function animate() {
  controls.update(); // required if damping enabled
  renderer.render(scene, camera);
  requestAnimationFrame(animate);
}

controls.addEventListener('change', () => renderer.render(scene, camera));
```

## MapControls

Bird's-eye map navigation:

```javascript
import { MapControls } from 'three/addons/controls/MapControls.js';

const controls = new MapControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.screenSpacePanning = false;
controls.maxPolarAngle = Math.PI / 2;

controls.mouseButtons = {
  LEFT: THREE.MOUSE.PAN,
  MIDDLE: THREE.MOUSE.DOLLY,
  RIGHT: THREE.MOUSE.ROTATE
};
```

## TrackballControls

Intuitive rotation (no gimbal lock):

```javascript
import { TrackballControls } from 'three/addons/controls/TrackballControls.js';

const controls = new TrackballControls(camera, renderer.domElement);
controls.rotateSpeed = 1.0;
controls.zoomSpeed = 1.2;
controls.panSpeed = 0.8;
controls.staticMoving = true;

function animate() {
  controls.update();
  renderer.render(scene, camera);
  requestAnimationFrame(animate);
}
```

## ArcballControls

3D rotation with virtual ball:

```javascript
import { ArcballControls } from 'three/addons/controls/ArcballControls.js';

const controls = new ArcballControls(camera, renderer.domElement, scene);
controls.enablePan = true;
controls.enableZoom = true;
controls.enableRotate = true;
```
