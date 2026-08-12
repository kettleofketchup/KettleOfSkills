# Shaders: Advanced Effects and Debugging

## Rim Lighting

```javascript
const material = new THREE.ShaderMaterial({
  vertexShader: `
    varying vec3 vNormal;
    varying vec3 vViewPosition;
    void main() {
      vNormal = normalize(normalMatrix * normal);
      vec4 mvPosition = modelViewMatrix * vec4(position, 1.0);
      vViewPosition = mvPosition.xyz;
      gl_Position = projectionMatrix * mvPosition;
    }
  `,
  fragmentShader: `
    varying vec3 vNormal;
    varying vec3 vViewPosition;
    void main() {
      vec3 viewDir = normalize(-vViewPosition);
      float rim = 1.0 - max(0.0, dot(viewDir, vNormal));
      rim = pow(rim, 4.0);
      vec3 baseColor = vec3(0.2, 0.2, 0.8);
      vec3 rimColor = vec3(1.0, 0.5, 0.0);
      gl_FragColor = vec4(baseColor + rimColor * rim, 1.0);
    }
  `,
});
```

## Dissolve Effect

```glsl
uniform float progress;
uniform sampler2D noiseMap;

void main() {
  float noise = texture2D(noiseMap, vUv).r;
  if (noise < progress) { discard; }

  float edge = smoothstep(progress, progress + 0.1, noise);
  vec3 edgeColor = vec3(1.0, 0.5, 0.0);
  vec3 baseColor = vec3(0.5);

  gl_FragColor = vec4(mix(edgeColor, baseColor, edge), 1.0);
}
```

## Instanced Shaders

```javascript
const offsets = new Float32Array(instanceCount * 3);
// Fill offsets...
geometry.setAttribute("offset", new THREE.InstancedBufferAttribute(offsets, 3));

const material = new THREE.ShaderMaterial({
  vertexShader: `
    attribute vec3 offset;
    void main() {
      vec3 pos = position + offset;
      gl_Position = projectionMatrix * modelViewMatrix * vec4(pos, 1.0);
    }
  `,
  fragmentShader: `
    void main() { gl_FragColor = vec4(1.0, 0.0, 0.0, 1.0); }
  `,
});
```

## External Shader Files

```javascript
// With Vite/Webpack
import vertexShader from "./shaders/vertex.glsl";
import fragmentShader from "./shaders/fragment.glsl";

const material = new THREE.ShaderMaterial({ vertexShader, fragmentShader });
```

## Debugging Shaders

```javascript
// Check for compile errors
material.onBeforeCompile = (shader) => {
  console.log("Vertex Shader:", shader.vertexShader);
  console.log("Fragment Shader:", shader.fragmentShader);
};

// Visual debugging in fragment shader
void main() {
  // Debug UV
  gl_FragColor = vec4(vUv, 0.0, 1.0);
  
  // Debug normals
  // gl_FragColor = vec4(vNormal * 0.5 + 0.5, 1.0);
  
  // Debug position
  // gl_FragColor = vec4(vPosition * 0.1 + 0.5, 1.0);
}
```

```javascript
renderer.debug.checkShaderErrors = true;
```

## Performance Tips

1. **Minimize uniforms**: Group related values into vectors
2. **Avoid conditionals**: Use mix/step instead of if/else
3. **Precalculate**: Move calculations to JS when possible
4. **Use textures**: For complex functions, use lookup tables

```glsl
// Instead of if/else:
color = mix(colorB, colorA, step(0.5, value));
```
