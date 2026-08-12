# Post-Processing: Custom Shaders and Other Effects

## Film/Grain and Glitch

```javascript
import { FilmPass } from 'three/addons/postprocessing/FilmPass.js';
const filmPass = new FilmPass(
  0.35,  // noise intensity
  0.5,   // scanline intensity
  648,   // scanline count
  false  // grayscale
);
composer.addPass(filmPass);

import { GlitchPass } from 'three/addons/postprocessing/GlitchPass.js';
composer.addPass(new GlitchPass());
```

## Custom Shader Pass

```javascript
import { ShaderPass } from 'three/addons/postprocessing/ShaderPass.js';

const customShader = {
  uniforms: {
    tDiffuse: { value: null },
    amount: { value: 1.0 }
  },
  vertexShader: `
    varying vec2 vUv;
    void main() {
      vUv = uv;
      gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
    }
  `,
  fragmentShader: `
    uniform sampler2D tDiffuse;
    uniform float amount;
    varying vec2 vUv;

    void main() {
      vec4 color = texture2D(tDiffuse, vUv);
      color.r *= amount;
      gl_FragColor = color;
    }
  `
};

const customPass = new ShaderPass(customShader);
customPass.material.uniforms.amount.value = 1.5;
composer.addPass(customPass);
```

## Common Pass Patterns

```javascript
// Full chain
composer.addPass(renderPass);
composer.addPass(ssaoPass);
composer.addPass(bloomPass);
composer.addPass(fxaaPass);
composer.addPass(outputPass);

// Selective rendering
bloomPass.renderToScreen = false; // render to texture, not screen

// Clear pass
import { ClearPass } from 'three/addons/postprocessing/ClearPass.js';
composer.addPass(new ClearPass());
```

## Performance Tips

- Post-processing is GPU-intensive
- Use lower resolution for expensive effects (SSAO, SSR)
- Limit number of passes (3-5 for good performance)
- Disable passes when not needed
- Use FXAA instead of MSAA (cheaper)
- Test on target devices

```javascript
// Disable a pass temporarily
ssaoPass.enabled = false;

// Conditional rendering
if (renderer.capabilities.isWebGL2) {
  composer.addPass(ssaoPass);
}
```
