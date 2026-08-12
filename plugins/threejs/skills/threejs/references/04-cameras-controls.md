# Cameras: Controls and Navigation

## OrbitControls (Most Common)

```javascript
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

const controls = new OrbitControls(camera, renderer.domElement);
controls.target.set(0, 0, 0);
controls.enableDamping = true;
controls.dampingFactor = 0.05;
controls.minDistance = 5;
controls.maxDistance = 50;
controls.maxPolarAngle = Math.PI / 2; // prevent going below ground

// In animation loop
function animate() {
  controls.update(); // required if enableDamping = true
  renderer.render(scene, camera);
}
```

## FirstPersonControls

```javascript
import { FirstPersonControls } from 'three/addons/controls/FirstPersonControls.js';

const controls = new FirstPersonControls(camera, renderer.domElement);
controls.movementSpeed = 10;
controls.lookSpeed = 0.1;

const clock = new THREE.Clock();
function animate() {
  const delta = clock.getDelta();
  controls.update(delta);
  renderer.render(scene, camera);
}
```

## FlyControls

```javascript
import { FlyControls } from 'three/addons/controls/FlyControls.js';

const controls = new FlyControls(camera, renderer.domElement);
controls.movementSpeed = 10;
controls.rollSpeed = Math.PI / 24;
controls.dragToLook = true;
```

## TransformControls

```javascript
import { TransformControls } from 'three/addons/controls/TransformControls.js';

const controls = new TransformControls(camera, renderer.domElement);
controls.attach(mesh);
scene.add(controls);

controls.setMode('translate'); // 'rotate', 'scale'

controls.addEventListener('change', () => renderer.render(scene, camera));
controls.addEventListener('dragging-changed', (event) => {
  orbitControls.enabled = !event.value;
});
```

## PointerLockControls (FPS)

```javascript
import { PointerLockControls } from 'three/addons/controls/PointerLockControls.js';

const controls = new PointerLockControls(camera, renderer.domElement);
renderer.domElement.addEventListener('click', () => controls.lock());

controls.addEventListener('lock', () => console.log('Locked'));
controls.addEventListener('unlock', () => console.log('Unlocked'));

// Movement in animate()
if (controls.isLocked) {
  controls.moveForward(velocity.z);
  controls.moveRight(velocity.x);
}
```
