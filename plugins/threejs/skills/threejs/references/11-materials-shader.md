# Materials: ShaderMaterial, RawShaderMaterial, Env Maps

## ShaderMaterial

Custom GLSL shaders with Three.js uniforms:

```javascript
const material = new THREE.ShaderMaterial({
  uniforms: {
    time: { value: 0 },
    color: { value: new THREE.Color(0xff0000) },
    texture1: { value: texture },
  },
  vertexShader: `
    varying vec2 vUv;
    uniform float time;
    void main() {
      vUv = uv;
      vec3 pos = position;
      pos.z += sin(pos.x * 10.0 + time) * 0.1;
      gl_Position = projectionMatrix * modelViewMatrix * vec4(pos, 1.0);
    }
  `,
  fragmentShader: `
    varying vec2 vUv;
    uniform vec3 color;
    uniform sampler2D texture1;
    void main() {
      vec4 texColor = texture2D(texture1, vUv);
      gl_FragColor = vec4(color * texColor.rgb, 1.0);
    }
  `,
  transparent: true,
  side: THREE.DoubleSide,
});

material.uniforms.time.value = clock.getElapsedTime();
```

### Built-in Uniforms (auto-provided)

```glsl
uniform mat4 modelMatrix;
uniform mat4 modelViewMatrix;
uniform mat4 projectionMatrix;
uniform mat4 viewMatrix;
uniform mat3 normalMatrix;
uniform vec3 cameraPosition;
// Attributes: position, normal, uv
```

## RawShaderMaterial

Full control - no built-in uniforms/attributes:

```javascript
const material = new THREE.RawShaderMaterial({
  uniforms: {
    projectionMatrix: { value: camera.projectionMatrix },
    modelViewMatrix: { value: new THREE.Matrix4() },
  },
  vertexShader: `
    precision highp float;
    attribute vec3 position;
    uniform mat4 projectionMatrix;
    uniform mat4 modelViewMatrix;
    void main() {
      gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
    }
  `,
  fragmentShader: `
    precision highp float;
    void main() { gl_FragColor = vec4(1.0, 0.0, 0.0, 1.0); }
  `,
});
```

## Environment Maps and Material Management

```javascript
// Load cube texture env map
const cubeLoader = new THREE.CubeTextureLoader();
const envMap = cubeLoader.load(['px.jpg','nx.jpg','py.jpg','ny.jpg','pz.jpg','nz.jpg']);
material.envMap = envMap;
material.envMapIntensity = 1;
scene.environment = envMap; // affects all PBR materials

// Clone and modify
const clone = material.clone();
clone.color.set(0x00ff00);

// Modify at runtime
material.color.set(0xff0000);
material.needsUpdate = true; // only needed for some changes

// Dispose when done
material.dispose();
texture.dispose();
```

## Performance Tips

1. Reuse materials: Same material = batched draw calls
2. Avoid transparent when possible
3. Use alphaTest instead of transparency for cutouts
4. Choose simpler materials: Basic > Lambert > Phong > Standard > Physical
5. Limit active lights: Each adds shader complexity

```javascript
// Material pooling
const materialCache = new Map();
function getMaterial(color) {
  const key = color.toString(16);
  if (!materialCache.has(key)) {
    materialCache.set(key, new THREE.MeshStandardMaterial({ color }));
  }
  return materialCache.get(key);
}
```
