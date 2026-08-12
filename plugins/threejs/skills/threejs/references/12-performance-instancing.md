# Performance: Instancing, LOD, and Culling

## Instancing

Render many copies of same geometry efficiently:

```javascript
const geometry = new THREE.BoxGeometry(1, 1, 1);
const material = new THREE.MeshStandardMaterial({ color: 0x00ff00 });
const mesh = new THREE.InstancedMesh(geometry, material, 10000);

const matrix = new THREE.Matrix4();
const position = new THREE.Vector3();
const quaternion = new THREE.Quaternion();
const scale = new THREE.Vector3(1, 1, 1);

for (let i = 0; i < 10000; i++) {
  position.set(
    Math.random() * 100 - 50,
    Math.random() * 100 - 50,
    Math.random() * 100 - 50
  );
  quaternion.setFromEuler(new THREE.Euler(
    Math.random() * Math.PI, Math.random() * Math.PI, 0
  ));
  matrix.compose(position, quaternion, scale);
  mesh.setMatrixAt(i, matrix);
}

mesh.instanceMatrix.needsUpdate = true;
scene.add(mesh);

// Per-instance colors
for (let i = 0; i < 10000; i++) {
  mesh.setColorAt(i, new THREE.Color(Math.random(), Math.random(), Math.random()));
}
```

## Level of Detail (LOD)

```javascript
const lod = new THREE.LOD();
lod.addLevel(new THREE.Mesh(new THREE.IcosahedronGeometry(10, 4), material), 0);
lod.addLevel(new THREE.Mesh(new THREE.IcosahedronGeometry(10, 2), material), 50);
lod.addLevel(new THREE.Mesh(new THREE.IcosahedronGeometry(10, 0), material), 100);
scene.add(lod);

function animate() {
  lod.update(camera);
  renderer.render(scene, camera);
  requestAnimationFrame(animate);
}
```

## Frustum Culling

```javascript
// Automatic - objects outside view aren't rendered
object.frustumCulled = false; // force disable for specific object

// Manually test if in view
const frustum = new THREE.Frustum();
const cameraViewProjectionMatrix = new THREE.Matrix4();
cameraViewProjectionMatrix.multiplyMatrices(
  camera.projectionMatrix, camera.matrixWorldInverse
);
frustum.setFromProjectionMatrix(cameraViewProjectionMatrix);

if (frustum.intersectsObject(object)) {
  // Object is visible
}
```

## Geometry Optimization

```javascript
// Merge geometries (reduce draw calls)
import { mergeGeometries } from 'three/addons/utils/BufferGeometryUtils.js';
const mergedGeometry = mergeGeometries([geom1, geom2, geom3]);
geomArray.forEach(g => g.dispose());

// Simplify geometry
import { SimplifyModifier } from 'three/addons/modifiers/SimplifyModifier.js';
const modifier = new SimplifyModifier();
const count = Math.floor(geometry.attributes.position.count * 0.5);
const simplified = modifier.modify(geometry, count);
```

## Object Pooling

```javascript
class ObjectPool {
  constructor(factory, initialSize) {
    this.factory = factory;
    this.pool = Array.from({ length: initialSize }, factory);
  }
  get() { return this.pool.length > 0 ? this.pool.pop() : this.factory(); }
  release(obj) { this.pool.push(obj); }
}

const bulletPool = new ObjectPool(
  () => new THREE.Mesh(bulletGeometry, bulletMaterial), 100
);

const bullet = bulletPool.get();
scene.add(bullet);
scene.remove(bullet);
bulletPool.release(bullet);
```
