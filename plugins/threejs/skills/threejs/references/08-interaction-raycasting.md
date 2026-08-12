# Interaction: Raycasting and Picking

## Mouse/Touch Raycasting

Detect which object user clicked:

```javascript
const raycaster = new THREE.Raycaster();
const mouse = new THREE.Vector2();
const clickableObjects = [];

function onPointerMove(event) {
  mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
  mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;

  raycaster.setFromCamera(mouse, camera);
  const intersects = raycaster.intersectObjects(clickableObjects);

  if (intersects.length > 0) {
    intersects[0].object.material.emissive.setHex(0xff0000);
  }
}

function onClick(event) {
  mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
  mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;

  raycaster.setFromCamera(mouse, camera);
  const intersects = raycaster.intersectObjects(clickableObjects);

  if (intersects.length > 0) {
    const object = intersects[0].object;
    console.log('Clicked:', object.name, 'Point:', intersects[0].point);
  }
}

renderer.domElement.addEventListener('pointermove', onPointerMove);
renderer.domElement.addEventListener('click', onClick);
```

## Object Highlighting

Visual feedback on hover/selection:

```javascript
let hoveredObject = null;
const originalEmissive = new THREE.Color();

function onPointerMove(event) {
  mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
  mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;

  raycaster.setFromCamera(mouse, camera);
  const intersects = raycaster.intersectObjects(scene.children, true);

  if (hoveredObject) {
    hoveredObject.material.emissive.copy(originalEmissive);
    hoveredObject = null;
  }

  if (intersects.length > 0) {
    hoveredObject = intersects[0].object;
    originalEmissive.copy(hoveredObject.material.emissive);
    hoveredObject.material.emissive.setHex(0x555555);
  }

  renderer.domElement.style.cursor = hoveredObject ? 'pointer' : 'default';
}
```

## HTML Tooltip at 3D Position

```javascript
function updateTooltip(object3D, text) {
  const vector = object3D.position.clone();
  vector.project(camera);

  const x = (vector.x * 0.5 + 0.5) * window.innerWidth;
  const y = (-vector.y * 0.5 + 0.5) * window.innerHeight;

  tooltip.style.left = x + 'px';
  tooltip.style.top = y + 'px';
  tooltip.textContent = text;
}
```

## Keyboard Input

```javascript
const keysPressed = {};

window.addEventListener('keydown', (event) => { keysPressed[event.key] = true; });
window.addEventListener('keyup', (event) => { keysPressed[event.key] = false; });

function animate() {
  const speed = 0.1;
  if (keysPressed['w']) object.position.z -= speed;
  if (keysPressed['s']) object.position.z += speed;
  if (keysPressed['a']) object.position.x -= speed;
  if (keysPressed['d']) object.position.x += speed;
  renderer.render(scene, camera);
  requestAnimationFrame(animate);
}
```
