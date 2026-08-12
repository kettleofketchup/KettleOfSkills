# Node Materials (TSL): Basics and Node Types

## What is TSL?

Three Shading Language (TSL) is a node-based system for creating materials and shaders:
- Functional approach to shader composition
- Type-safe node graph
- Unified GLSL/WGSL output (WebGL and WebGPU)
- No manual shader code required

## Basic Node Material

```javascript
import * as THREE from 'three/webgpu';
import { color, texture, normalMap, MeshStandardNodeMaterial } from 'three/nodes';

const material = new MeshStandardNodeMaterial();
material.colorNode = color(0xff0000);
material.colorNode = texture(colorTexture);
material.colorNode = texture(colorTexture).mul(color(0xffffff));
material.normalNode = normalMap(normalTexture);
```

## Input Nodes

```javascript
import { attribute, uniform, texture, cubeTexture, instancedArray, storage } from 'three/nodes';

const positionNode = attribute('position');
const normalNode = attribute('normal');
const uvNode = attribute('uv');
const timeNode = uniform(0);
const colorNode = texture(diffuseTexture);
const envNode = cubeTexture(cubeMapTexture);
const instanceColorNode = instancedArray('instanceColor');
const storageNode = storage(buffer, 'vec4', count);
```

## Math Nodes

```javascript
import { add, sub, mul, div, pow, sin, cos, length, normalize, mix } from 'three/nodes';

const result = add(a, b);     // a + b
const result = sub(a, b);     // a - b
const result = mul(a, b);     // a * b
const result = div(a, b);     // a / b
const result = sin(angle);
const result = cos(angle);
const result = length(vector);
const result = normalize(vector);
const result = mul(texture(tex), color(0xff0000)); // chaining
```

## Procedural Nodes

```javascript
import { checker, dots, noise, voronoi } from 'three/nodes';

material.colorNode = checker(uvNode.mul(10));
material.colorNode = noise(uvNode.mul(5));
material.colorNode = voronoi(uvNode.mul(3));
```

## Custom Shader Function

```javascript
import { Fn, vec3, float } from 'three/nodes';

const customColor = Fn(([uv, time]) => {
  const r = sin(uv.x.mul(10).add(time));
  const g = cos(uv.y.mul(10).add(time));
  const b = float(0.5);
  return vec3(r, g, b);
});

material.colorNode = customColor(uvNode, timeNode);
```

## Node Material Types

```javascript
import {
  MeshStandardNodeMaterial, MeshPhysicalNodeMaterial,
  MeshBasicNodeMaterial, PointsNodeMaterial,
  LineBasicNodeMaterial, SpriteNodeMaterial
} from 'three/nodes';

const material = new MeshStandardNodeMaterial();
material.colorNode = colorNode;
material.roughnessNode = roughnessNode;
material.metalnessNode = metalnessNode;

const physical = new MeshPhysicalNodeMaterial();
physical.clearcoatNode = clearcoatNode;
physical.transmissionNode = transmissionNode;
```
