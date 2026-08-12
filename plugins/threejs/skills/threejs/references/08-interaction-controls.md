# Interaction: Drag Controls, Transform, and Selection

## DragControls

Drag objects with mouse:

```javascript
import { DragControls } from 'three/addons/controls/DragControls.js';

const controls = new DragControls(objectsArray, camera, renderer.domElement);

controls.addEventListener('dragstart', (event) => {
  orbitControls.enabled = false;
  event.object.material.emissive.set(0xaaaaaa);
});

controls.addEventListener('drag', (event) => {
  console.log(event.object.position);
});

controls.addEventListener('dragend', (event) => {
  orbitControls.enabled = true;
  event.object.material.emissive.set(0x000000);
});
```

## TransformControls

Interactive 3D gizmo for translate/rotate/scale:

```javascript
import { TransformControls } from 'three/addons/controls/TransformControls.js';

const transformControls = new TransformControls(camera, renderer.domElement);
scene.add(transformControls);
transformControls.attach(mesh);

transformControls.setMode('translate'); // 'rotate', 'scale'
transformControls.setSpace('world');    // 'local'

transformControls.addEventListener('change', () => renderer.render(scene, camera));
transformControls.addEventListener('dragging-changed', (event) => {
  orbitControls.enabled = !event.value;
});

// Keyboard shortcuts
window.addEventListener('keydown', (event) => {
  switch (event.key) {
    case 'g': transformControls.setMode('translate'); break;
    case 'r': transformControls.setMode('rotate'); break;
    case 's': transformControls.setMode('scale'); break;
    case 'Escape': transformControls.detach(); break;
  }
});
```

## Pointer Lock (First Person)

```javascript
import { PointerLockControls } from 'three/addons/controls/PointerLockControls.js';

const controls = new PointerLockControls(camera, renderer.domElement);
renderer.domElement.addEventListener('click', () => controls.lock());

controls.addEventListener('lock', () => console.log('Pointer locked'));
controls.addEventListener('unlock', () => console.log('Pointer unlocked'));

const velocity = new THREE.Vector3();
function animate() {
  if (controls.isLocked) {
    controls.moveForward(velocity.z);
    controls.moveRight(velocity.x);
  }
  renderer.render(scene, camera);
  requestAnimationFrame(animate);
}
```

## Selection Box (Box Select Multiple Objects)

```javascript
import { SelectionBox } from 'three/addons/interactive/SelectionBox.js';
import { SelectionHelper } from 'three/addons/interactive/SelectionHelper.js';

const selectionBox = new SelectionBox(camera, scene);
const helper = new SelectionHelper(renderer, 'selectBox');
let isSelecting = false;

renderer.domElement.addEventListener('pointerdown', (event) => {
  isSelecting = true;
  selectionBox.startPoint.set(
    (event.clientX / window.innerWidth) * 2 - 1,
    -(event.clientY / window.innerHeight) * 2 + 1,
    0.5
  );
});

renderer.domElement.addEventListener('pointermove', (event) => {
  if (isSelecting) {
    selectionBox.endPoint.set(
      (event.clientX / window.innerWidth) * 2 - 1,
      -(event.clientY / window.innerHeight) * 2 + 1,
      0.5
    );
    const allSelected = selectionBox.select();
    console.log('Selected:', allSelected.length);
  }
});

renderer.domElement.addEventListener('pointerup', () => { isSelecting = false; });
```
