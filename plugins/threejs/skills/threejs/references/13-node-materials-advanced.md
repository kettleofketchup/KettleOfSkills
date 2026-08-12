# Node Materials (TSL): Advanced Effects and Compute

## Animation with Nodes

```javascript
import { uniform, oscSine, timerLocal } from 'three/nodes';

// Oscillating value
const oscillator = oscSine(timerLocal(0.5)); // frequency = 0.5

// Pulsing color
material.colorNode = color(0xff0000).mul(oscillator.add(0.5));

// Rotating UV
const rotatedUV = uvNode.rotateUV(timerLocal());
material.colorNode = texture(tex, rotatedUV);
```

## Advanced Effects

### Fresnel Effect

```javascript
import { normalView, positionView, dot, pow, mix } from 'three/nodes';

const fresnel = pow(
  float(1).sub(dot(normalView, positionView.normalize())), 3
);
material.colorNode = mix(baseColor, edgeColor, fresnel);
```

### Vertex Displacement

```javascript
import { positionLocal, normalLocal, timerLocal, sin } from 'three/nodes';

const displacement = sin(positionLocal.y.add(timerLocal())).mul(0.5);
material.positionNode = positionLocal.add(normalLocal.mul(displacement));
```

## Compute Shaders (WebGPU)

```javascript
import { compute, uniform, storage, Fn } from 'three/nodes';

const computeShader = Fn(() => {
  const storageBuffer = storage(buffer, 'vec4', count);
  const index = instanceIndex;
  const value = storageBuffer.element(index);
  storageBuffer.element(index).assign(value.mul(2));
})();

const computeNode = compute(computeShader, 256); // workgroup size
renderer.compute(computeNode);
```

## Animated Material Example

```javascript
import * as THREE from 'three/webgpu';
import { MeshStandardNodeMaterial, texture, uniform, timerLocal, sin, cos, vec2 } from 'three/nodes';

const material = new MeshStandardNodeMaterial();

const time = timerLocal();
const scrollSpeed = uniform(0.1);
const uvOffset = vec2(
  time.mul(scrollSpeed),
  sin(time).mul(0.1)
);
const scrolledUV = uv().add(uvOffset);
material.colorNode = texture(diffuseTexture, scrolledUV);

const pulseSpeed = uniform(2);
const emission = sin(time.mul(pulseSpeed)).mul(0.5).add(0.5);
material.emissiveNode = color(1, 0.5, 0).mul(emission);
```

## Migration from ShaderMaterial

```javascript
// Old way (ShaderMaterial)
const material = new THREE.ShaderMaterial({
  uniforms: { time: { value: 0 } },
  vertexShader: `...`,
  fragmentShader: `...`
});

// New way (Node Material) - cleaner, type-safe, reusable
const material = new MeshStandardNodeMaterial();
material.colorNode = customFunction(timerLocal());
```

## When to Use Node Materials

- Creating complex procedural materials
- Need both WebGL and WebGPU support
- Want visual/functional shader composition
- Reusable shader components
- Compute shader integration (WebGPU only)

**Note**: Node materials require WebGPU renderer for full features. Some features work with WebGL backend but compute shaders require WebGPU.
