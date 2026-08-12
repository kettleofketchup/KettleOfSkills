# Geometry: InstancedMesh and Points

## InstancedMesh

Efficiently render many copies of the same geometry:

```javascript
const geometry = new THREE.BoxGeometry(1, 1, 1);
const material = new THREE.MeshStandardMaterial({ color: 0x00ff00 });
const count = 1000;

const instancedMesh = new THREE.InstancedMesh(geometry, material, count);

const dummy = new THREE.Object3D();
for (let i = 0; i < count; i++) {
  dummy.position.set(
    (Math.random() - 0.5) * 20,
    (Math.random() - 0.5) * 20,
    (Math.random() - 0.5) * 20
  );
  dummy.rotation.set(Math.random() * Math.PI, Math.random() * Math.PI, 0);
  dummy.scale.setScalar(0.5 + Math.random());
  dummy.updateMatrix();
  instancedMesh.setMatrixAt(i, dummy.matrix);
}
instancedMesh.instanceMatrix.needsUpdate = true;

// Per-instance colors
for (let i = 0; i < count; i++) {
  instancedMesh.setColorAt(i, new THREE.Color(Math.random(), Math.random(), Math.random()));
}
instancedMesh.instanceColor.needsUpdate = true;
scene.add(instancedMesh);
```

## Update Instance at Runtime

```javascript
const matrix = new THREE.Matrix4();
instancedMesh.getMatrixAt(index, matrix);
// Modify matrix...
instancedMesh.setMatrixAt(index, matrix);
instancedMesh.instanceMatrix.needsUpdate = true;

// Raycasting with instanced mesh
const intersects = raycaster.intersectObject(instancedMesh);
if (intersects.length > 0) {
  const instanceId = intersects[0].instanceId;
}
```

## InstancedBufferGeometry (Advanced)

```javascript
const geometry = new THREE.InstancedBufferGeometry();
geometry.copy(new THREE.BoxGeometry(1, 1, 1));

const offsets = new Float32Array(count * 3);
for (let i = 0; i < count; i++) {
  offsets[i * 3] = Math.random() * 10;
  offsets[i * 3 + 1] = Math.random() * 10;
  offsets[i * 3 + 2] = Math.random() * 10;
}
geometry.setAttribute("offset", new THREE.InstancedBufferAttribute(offsets, 3));
// Use in shader: attribute vec3 offset; vec3 transformed = position + offset;
```

## Points

```javascript
const geometry = new THREE.BufferGeometry();
const positions = new Float32Array(1000 * 3);
for (let i = 0; i < 1000; i++) {
  positions[i * 3] = (Math.random() - 0.5) * 10;
  positions[i * 3 + 1] = (Math.random() - 0.5) * 10;
  positions[i * 3 + 2] = (Math.random() - 0.5) * 10;
}
geometry.setAttribute("position", new THREE.BufferAttribute(positions, 3));

const material = new THREE.PointsMaterial({ size: 0.1, sizeAttenuation: true, color: 0xffffff });
scene.add(new THREE.Points(geometry, material));
```

## Lines

```javascript
// Connected line
const points = [new THREE.Vector3(-1, 0, 0), new THREE.Vector3(0, 1, 0), new THREE.Vector3(1, 0, 0)];
const geometry = new THREE.BufferGeometry().setFromPoints(points);
const line = new THREE.Line(geometry, new THREE.LineBasicMaterial({ color: 0xff0000 }));

// LineLoop (closed)
const loop = new THREE.LineLoop(geometry, material);

// LineSegments (pairs of points)
const segmentsGeometry = new THREE.BufferGeometry();
segmentsGeometry.setAttribute("position", new THREE.BufferAttribute(
  new Float32Array([-1,0,0, 0,1,0, 0,1,0, 1,0,0]), 3
));
const segments = new THREE.LineSegments(segmentsGeometry, material);
```
