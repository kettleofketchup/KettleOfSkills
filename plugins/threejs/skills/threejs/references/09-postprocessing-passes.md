# Post-Processing: Composer and Effect Passes

## EffectComposer Setup

```javascript
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';

const composer = new EffectComposer(renderer);
composer.addPass(new RenderPass(scene, camera));
// Add effect passes...
composer.addPass(new OutputPass()); // required last

function animate() {
  requestAnimationFrame(animate);
  composer.render(); // instead of renderer.render()
}

window.addEventListener('resize', () => {
  composer.setSize(window.innerWidth, window.innerHeight);
});
```

## Bloom Effect

```javascript
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';

const bloomPass = new UnrealBloomPass(
  new THREE.Vector2(window.innerWidth, window.innerHeight),
  1.5,  // strength
  0.4,  // radius
  0.85  // threshold
);
composer.addPass(bloomPass);
```

## SSAO and SSR

```javascript
import { SSAOPass } from 'three/addons/postprocessing/SSAOPass.js';
const ssaoPass = new SSAOPass(scene, camera, width, height);
ssaoPass.kernelRadius = 16;
ssaoPass.minDistance = 0.005;
ssaoPass.maxDistance = 0.1;
composer.addPass(ssaoPass);

import { SSRPass } from 'three/addons/postprocessing/SSRPass.js';
const ssrPass = new SSRPass({ renderer, scene, camera, width, height });
ssrPass.opacity = 0.5;
composer.addPass(ssrPass);
```

## Depth of Field (Bokeh)

```javascript
import { BokehPass } from 'three/addons/postprocessing/BokehPass.js';
const bokehPass = new BokehPass(scene, camera, {
  focus: 10.0, aperture: 0.025, maxblur: 0.01
});
composer.addPass(bokehPass);
```

## FXAA Anti-Aliasing

```javascript
import { ShaderPass } from 'three/addons/postprocessing/ShaderPass.js';
import { FXAAShader } from 'three/addons/shaders/FXAAShader.js';

const fxaaPass = new ShaderPass(FXAAShader);
fxaaPass.material.uniforms['resolution'].value.x = 1 / window.innerWidth;
fxaaPass.material.uniforms['resolution'].value.y = 1 / window.innerHeight;
composer.addPass(fxaaPass);
```

## Outline Pass

```javascript
import { OutlinePass } from 'three/addons/postprocessing/OutlinePass.js';
const outlinePass = new OutlinePass(
  new THREE.Vector2(window.innerWidth, window.innerHeight), scene, camera
);
outlinePass.edgeStrength = 3;
outlinePass.edgeGlow = 0.5;
outlinePass.edgeThickness = 1;
outlinePass.visibleEdgeColor.set('#ffffff');
outlinePass.selectedObjects = [mesh1, mesh2];
composer.addPass(outlinePass);
```
