# Camera Controls: FPS and Advanced Patterns

## FirstPersonControls

FPS-style camera movement:

```javascript
import { FirstPersonControls } from 'three/addons/controls/FirstPersonControls.js';

const controls = new FirstPersonControls(camera, renderer.domElement);
controls.movementSpeed = 10;
controls.lookSpeed = 0.1;
controls.lookVertical = true;
controls.constrainVertical = true;
controls.verticalMin = 1.0;
controls.verticalMax = 2.0;

const clock = new THREE.Clock();
function animate() {
  const delta = clock.getDelta();
  controls.update(delta);
  renderer.render(scene, camera);
  requestAnimationFrame(animate);
}
```

## FlyControls

Free-form flying navigation:

```javascript
import { FlyControls } from 'three/addons/controls/FlyControls.js';

const controls = new FlyControls(camera, renderer.domElement);
controls.movementSpeed = 10;
controls.rollSpeed = Math.PI / 24;
controls.autoForward = false;
controls.dragToLook = false;

const clock = new THREE.Clock();
function animate() {
  const delta = clock.getDelta();
  controls.update(delta);
  renderer.render(scene, camera);
  requestAnimationFrame(animate);
}
```

## PointerLockControls

Locked pointer FPS controls:

```javascript
import { PointerLockControls } from 'three/addons/controls/PointerLockControls.js';

const controls = new PointerLockControls(camera, renderer.domElement);
renderer.domElement.addEventListener('click', () => controls.lock());

let moveForward = false, moveBackward = false, moveLeft = false, moveRight = false;
window.addEventListener('keydown', (event) => {
  switch (event.code) {
    case 'KeyW': moveForward = true; break;
    case 'KeyS': moveBackward = true; break;
    case 'KeyA': moveLeft = true; break;
    case 'KeyD': moveRight = true; break;
  }
});

const direction = new THREE.Vector3();
function animate() {
  if (controls.isLocked) {
    direction.z = Number(moveForward) - Number(moveBackward);
    direction.x = Number(moveRight) - Number(moveLeft);
    direction.normalize();
    controls.moveForward(direction.z * 10);
    controls.moveRight(direction.x * 10);
  }
  renderer.render(scene, camera);
  requestAnimationFrame(animate);
}
```

## Controls Comparison

| Control | Use Case |
|---------|----------|
| OrbitControls | Product viewers, 3D models, general use |
| MapControls | Top-down maps, strategy games |
| FirstPersonControls | Architectural walkthroughs |
| FlyControls | Space navigation, creative tools |
| PointerLockControls | FPS games |
| TrackballControls | CAD applications |
| ArcballControls | Scientific visualization |

## Common Patterns

```javascript
// Animate camera to position (with GSAP)
function moveCameraTo(position, target) {
  gsap.to(camera.position, { duration: 1, ...position, onUpdate: () => controls.update() });
  gsap.to(controls.target, { duration: 1, ...target });
}

// Reset camera
controls.reset();

// Disable during transform gizmo use
transformControls.addEventListener('dragging-changed', (event) => {
  orbitControls.enabled = !event.value;
});
```
