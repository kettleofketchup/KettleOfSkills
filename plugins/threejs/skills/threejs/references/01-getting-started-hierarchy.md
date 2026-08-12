# Getting Started: Object Hierarchy and Transforms

## Object3D Hierarchy

Transform and group objects:

```javascript
const group = new THREE.Group();
group.add(cube1);
group.add(cube2);
scene.add(group);

// Transform
object.position.set(x, y, z);
object.rotation.set(x, y, z); // Euler angles
object.scale.set(x, y, z);

// Hierarchy transforms are relative to parent
```

## Transform Properties

```javascript
// Position
mesh.position.x = 5;
mesh.position.set(1, 2, 3);

// Rotation (Euler angles in radians)
mesh.rotation.y = Math.PI / 4;  // 45 degrees
mesh.rotation.set(0, Math.PI, 0);

// Scale
mesh.scale.set(2, 1, 1);  // double width

// Quaternion (avoids gimbal lock)
mesh.quaternion.setFromAxisAngle(new THREE.Vector3(0, 1, 0), Math.PI / 4);
```

## World vs Local Transforms

```javascript
// Get world position (accounts for parent hierarchy)
const worldPos = new THREE.Vector3();
mesh.getWorldPosition(worldPos);

const worldQuat = new THREE.Quaternion();
mesh.getWorldQuaternion(worldQuat);

const worldDir = new THREE.Vector3();
mesh.getWorldDirection(worldDir);
```

## Traversal

```javascript
// Apply operation to all children
scene.traverse((object) => {
  if (object.isMesh) {
    object.castShadow = true;
    object.receiveShadow = true;
  }
});

// Find by name
const found = scene.getObjectByName('myMesh');

// Find all matching
const lights = [];
scene.traverse((obj) => {
  if (obj.isLight) lights.push(obj);
});
```

## Visibility and Layers

```javascript
// Toggle visibility
mesh.visible = false;

// Layers for selective rendering
mesh.layers.set(1);
camera.layers.enable(1);  // camera renders layer 1

// Objects on disabled layers won't be rendered or raycasted
```

## Shadows

```javascript
// Enable shadows on renderer
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;

// Enable on objects
mesh.castShadow = true;
mesh.receiveShadow = true;

// Enable on light
dirLight.castShadow = true;
dirLight.shadow.mapSize.width = 2048;
dirLight.shadow.mapSize.height = 2048;
```

## Helpers for Debugging

```javascript
// Show axes
const axes = new THREE.AxesHelper(5);
scene.add(axes);

// Show bounding box
const box = new THREE.BoxHelper(mesh, 0xffff00);
scene.add(box);

// Show grid
const grid = new THREE.GridHelper(10, 10);
scene.add(grid);
```
