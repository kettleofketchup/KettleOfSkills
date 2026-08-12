# WebGPU: Renderer and Core Features

## WebGPU Renderer

Next-generation rendering backend:

```javascript
import WebGPU from 'three/addons/capabilities/WebGPU.js';
import WebGPURenderer from 'three/addons/renderers/webgpu/WebGPURenderer.js';

if (WebGPU.isAvailable()) {
  const renderer = new WebGPURenderer();
  renderer.setSize(window.innerWidth, window.innerHeight);
  document.body.appendChild(renderer.domElement);

  // Use setAnimationLoop (not requestAnimationFrame) for WebGPU
  renderer.setAnimationLoop(() => {
    renderer.render(scene, camera);
  });
} else {
  document.body.appendChild(WebGPU.getErrorMessage());
}
```

## Benefits of WebGPU

- Better performance (lower CPU overhead)
- Compute shaders
- Modern GPU features
- Unified shading language (WGSL)
- Better multi-threading support
- More predictable behavior

## WebGPU Node Materials

```javascript
import { MeshStandardNodeMaterial, texture, normalMap, float } from 'three/nodes';

const material = new MeshStandardNodeMaterial();
material.colorNode = texture(diffuseTexture);
material.normalNode = normalMap(normalTexture);
material.roughnessNode = float(0.5);
material.metalnessNode = float(0.8);
// Works with both WebGL and WebGPU automatically
```

## Multi-Render-Target (MRT)

```javascript
import { WebGPURenderTarget } from 'three/addons/renderers/webgpu/WebGPURenderTarget.js';

const renderTarget = new WebGPURenderTarget(width, height, { count: 3 });
const albedoTexture = renderTarget.textures[0];
const normalTexture = renderTarget.textures[1];
const depthTexture = renderTarget.textures[2];

renderer.setRenderTarget(renderTarget);
renderer.render(scene, camera);
```

## Async Shader Compilation

```javascript
// Compile materials ahead of time to avoid frame drops
await renderer.compileAsync(scene, camera);
renderer.setAnimationLoop(() => renderer.render(scene, camera));
```

## Migration from WebGL

```javascript
// WebGL
const renderer = new THREE.WebGLRenderer();

// WebGPU (drop-in replacement for most cases)
const renderer = new WebGPURenderer();

// Exceptions:
// - Custom shaders: need to use Node materials or WGSL
// - Some extensions not available
// - Compute shaders only in WebGPU
```

## Browser Support (2025)

- Chrome 113+ - supported
- Edge 113+ - supported
- Safari 18+ (macOS/iOS) - supported
- Firefox - in development

Check support: `WebGPU.isAvailable()`
