# Geometry: Utilities, Morph Targets, and Performance

## Geometry Utilities

```javascript
import * as BufferGeometryUtils from "three/examples/jsm/utils/BufferGeometryUtils.js";

// Merge geometries (must have same attributes)
const merged = BufferGeometryUtils.mergeGeometries([geo1, geo2, geo3]);

// Merge with groups (for multi-material)
const merged = BufferGeometryUtils.mergeGeometries([geo1, geo2], true);

// Compute tangents (required for normal maps)
BufferGeometryUtils.computeTangents(geometry);

// Interleave attributes for better performance
const interleaved = BufferGeometryUtils.interleaveAttributes([
  geometry.attributes.position,
  geometry.attributes.normal,
  geometry.attributes.uv,
]);
```

## Common Patterns

```javascript
// Center geometry
geometry.computeBoundingBox();
geometry.center(); // move vertices so center is at origin

// Scale to fit
geometry.computeBoundingBox();
const size = new THREE.Vector3();
geometry.boundingBox.getSize(size);
const maxDim = Math.max(size.x, size.y, size.z);
geometry.scale(1 / maxDim, 1 / maxDim, 1 / maxDim);

// Clone and transform
const clone = geometry.clone();
clone.rotateX(Math.PI / 2);
clone.translate(0, 1, 0);
clone.scale(2, 2, 2);
```

## Morph Targets

```javascript
const geometry = new THREE.BoxGeometry(1, 1, 1, 4, 4, 4);

const morphPositions = geometry.attributes.position.array.slice();
for (let i = 0; i < morphPositions.length; i += 3) {
  morphPositions[i] *= 2;      // Scale X
  morphPositions[i + 1] *= 0.5; // Squash Y
}

geometry.morphAttributes.position = [
  new THREE.BufferAttribute(new Float32Array(morphPositions), 3),
];

const mesh = new THREE.Mesh(geometry, material);
mesh.morphTargetInfluences[0] = 0.5; // 50% blend
```

## Multiple Materials and Groups

```javascript
// Assign different materials to geometry groups
const geometry = new THREE.BoxGeometry(1, 1, 1);
const materials = [
  new THREE.MeshBasicMaterial({ color: 0xff0000 }), // right
  new THREE.MeshBasicMaterial({ color: 0x00ff00 }), // left
  new THREE.MeshBasicMaterial({ color: 0x0000ff }), // top
  new THREE.MeshBasicMaterial({ color: 0xffff00 }), // bottom
  new THREE.MeshBasicMaterial({ color: 0xff00ff }), // front
  new THREE.MeshBasicMaterial({ color: 0x00ffff }), // back
];
const mesh = new THREE.Mesh(geometry, materials);

// Custom groups
geometry.clearGroups();
geometry.addGroup(0, 6, 0); // start, count, materialIndex
geometry.addGroup(6, 6, 1);
```

## Performance Tips

1. Use indexed geometry: Reuse vertices with indices
2. Merge static meshes: Reduce draw calls with `mergeGeometries`
3. Use InstancedMesh: For many identical objects
4. Choose appropriate segment counts: More segments = smoother but slower
5. Dispose unused geometry: `geometry.dispose()`

```javascript
// Good segment counts
new THREE.SphereGeometry(1, 32, 32); // Good quality
new THREE.SphereGeometry(1, 64, 64); // High quality
new THREE.SphereGeometry(1, 16, 16); // Performance mode

geometry.dispose(); // free GPU memory
```
