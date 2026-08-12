# WebGPU: Compute Shaders and Advanced Features

## Compute Shaders

GPU-accelerated computation:

```javascript
import { storageBuffer, uniform, Fn } from 'three/nodes';
import { StorageBufferAttribute } from 'three/addons/renderers/common/StorageBufferAttribute.js';

const particleCount = 10000;
const positionBuffer = new StorageBufferAttribute(particleCount * 3, 3);

// Fill initial positions
for (let i = 0; i < particleCount; i++) {
  positionBuffer.setXYZ(i, Math.random() * 10 - 5, Math.random() * 10 - 5, Math.random() * 10 - 5);
}

const computeParticles = Fn(() => {
  const position = storageBuffer(positionBuffer);
  const time = uniform('time', 0);
  const index = instanceIndex;

  const pos = position.element(index);
  pos.y.addAssign(sin(time.add(index)).mul(0.01));

  If(pos.y.greaterThan(5), () => {
    pos.y.assign(-5);
  });
})();

const computeNode = computeParticles.compute(particleCount);

renderer.setAnimationLoop(() => {
  renderer.compute(computeNode);
  renderer.render(scene, camera);
});
```

## Storage Buffers

```javascript
import { storage, Fn, vec3, float } from 'three/nodes';

const particleData = storage(
  new THREE.StorageBufferAttribute(count * 7, 7),
  'vec3', 'vec3', 'float'  // position, velocity, life
);

const updateParticle = Fn(() => {
  const data = particleData.element(instanceIndex);
  const position = data.xyz;
  const velocity = data.toVec3(3);
  const life = data.element(6);
  position.addAssign(velocity.mul(deltaTime));
  life.subAssign(deltaTime);
})();
```

## Indirect Drawing

Efficient rendering with compute-generated draw calls:

```javascript
import { IndirectStorageBufferAttribute } from 'three/addons/renderers/common/IndirectStorageBufferAttribute.js';

const indirectBuffer = new IndirectStorageBufferAttribute(count, 5);

const updateIndirect = Fn(() => {
  const indirect = storage(indirectBuffer);
  const visible = computeVisibility();
  If(visible, () => {
    indirect.element(1).addAssign(1); // increment instanceCount
  });
})();

renderer.drawIndirect(mesh, indirectBuffer);
```

## WGSL (WebGPU Shading Language)

Native shader language for WebGPU:

```wgsl
@group(0) @binding(0) var<storage, read_write> positions: array<vec3f>;
@group(0) @binding(1) var<uniform> time: f32;

@compute @workgroup_size(64)
fn main(@builtin(global_invocation_id) global_id: vec3u) {
  let index = global_id.x;
  if (index >= arrayLength(&positions)) { return; }

  var pos = positions[index];
  pos.y += sin(time + f32(index)) * 0.01;
  positions[index] = pos;
}
```

## WebGPU-Specific Features

### Texture Compression (BC7)
```javascript
const texture = new THREE.CompressedTexture(mipmaps, width, height, THREE.RGBA_BPTC_Format);
```

### Storage Textures
```javascript
import { storageTexture } from 'three/nodes';
const writeableTexture = storageTexture(texture);

const computeShader = Fn(() => {
  const coord = vec2(instanceIndex % width, instanceIndex / width);
  writeableTexture.store(coord, vec4(1, 0, 0, 1));
})();
```

## Best Practices

- Use compute shaders for particle systems, physics
- Leverage storage buffers for large datasets
- Async compile before rendering
- Use Node materials instead of custom GLSL
- Test on both WebGL and WebGPU backends
- Provide WebGL fallback for unsupported browsers
