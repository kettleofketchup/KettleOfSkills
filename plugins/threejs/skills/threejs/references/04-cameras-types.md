# Cameras: Types and Methods

## Perspective Camera

Realistic camera with field of view (most common):

```javascript
const camera = new THREE.PerspectiveCamera(fov, aspect, near, far);
// fov: typically 45-75 degrees
// aspect: width / height
// near: typically 0.1
// far: typically 1000

camera.position.set(0, 5, 10);
camera.lookAt(0, 0, 0);

// Update after changing parameters
camera.fov = 60;
camera.updateProjectionMatrix();
```

## Orthographic Camera

No perspective distortion (parallel projection):

```javascript
const frustumSize = 10;
const aspect = window.innerWidth / window.innerHeight;
const camera = new THREE.OrthographicCamera(
  frustumSize * aspect / -2, // left
  frustumSize * aspect / 2,  // right
  frustumSize / 2,           // top
  frustumSize / -2,          // bottom
  0.1, 1000
);
// Useful for: 2D games, CAD, isometric views
```

## Camera Methods

```javascript
// Position and orientation
camera.position.set(x, y, z);
camera.lookAt(x, y, z); // or lookAt(vector3) or lookAt(object.position)
camera.up.set(0, 1, 0);

// Get world direction
const direction = new THREE.Vector3();
camera.getWorldDirection(direction);

// Screen to world (raycasting)
const mouse = new THREE.Vector2(x, y); // normalized device coords (-1 to 1)
const raycaster = new THREE.Raycaster();
raycaster.setFromCamera(mouse, camera);

// World to screen
const vector = new THREE.Vector3(x, y, z);
vector.project(camera); // now in normalized device coords
```

## Layers

Selective rendering with layers:

```javascript
mesh.layers.set(1);          // object on layer 1
camera.layers.enable(0);     // render layer 0
camera.layers.enable(1);     // render layer 1
camera.layers.disable(2);    // don't render layer 2
```

## Frustum Culling

```javascript
const frustum = new THREE.Frustum();
const matrix = new THREE.Matrix4().multiplyMatrices(
  camera.projectionMatrix,
  camera.matrixWorldInverse
);
frustum.setFromProjectionMatrix(matrix);

if (frustum.containsPoint(object.position)) {
  // Object is visible
}
```

## Multiple Cameras and Resize Handling

```javascript
// Multiple cameras with different viewports
renderer.setViewport(0, 0, width, height);
renderer.render(scene, mainCamera);
renderer.setViewport(width - 200, height - 200, 200, 200);
renderer.render(scene, minimapCamera);

// Resize handling
window.addEventListener('resize', () => {
  // Perspective
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();

  // Orthographic
  const aspect = window.innerWidth / window.innerHeight;
  camera.left = -frustumSize * aspect / 2;
  camera.right = frustumSize * aspect / 2;
  camera.updateProjectionMatrix();

  renderer.setSize(window.innerWidth, window.innerHeight);
});
```
