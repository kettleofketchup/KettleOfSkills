# Shaders: Varyings and Common Patterns

## Varyings

Pass data from vertex to fragment shader:

```javascript
const material = new THREE.ShaderMaterial({
  vertexShader: `
    varying vec2 vUv;
    varying vec3 vNormal;
    varying vec3 vPosition;

    void main() {
      vUv = uv;
      vNormal = normalize(normalMatrix * normal);
      vPosition = (modelViewMatrix * vec4(position, 1.0)).xyz;
      gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
    }
  `,
  fragmentShader: `
    varying vec2 vUv;
    varying vec3 vNormal;
    varying vec3 vPosition;

    void main() {
      gl_FragColor = vec4(vNormal * 0.5 + 0.5, 1.0);
    }
  `,
});
```

## Texture Sampling

```javascript
const material = new THREE.ShaderMaterial({
  uniforms: { map: { value: texture } },
  vertexShader: `
    varying vec2 vUv;
    void main() {
      vUv = uv;
      gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
    }
  `,
  fragmentShader: `
    uniform sampler2D map;
    varying vec2 vUv;
    void main() {
      gl_FragColor = texture2D(map, vUv);
    }
  `,
});
```

## Vertex Displacement

```javascript
const material = new THREE.ShaderMaterial({
  uniforms: { time: { value: 0 }, amplitude: { value: 0.5 } },
  vertexShader: `
    uniform float time;
    uniform float amplitude;
    void main() {
      vec3 pos = position;
      pos.z += sin(pos.x * 5.0 + time) * amplitude;
      pos.z += sin(pos.y * 5.0 + time) * amplitude;
      gl_Position = projectionMatrix * modelViewMatrix * vec4(pos, 1.0);
    }
  `,
  fragmentShader: `
    void main() { gl_FragColor = vec4(0.5, 0.8, 1.0, 1.0); }
  `,
});
```

## Fresnel Effect

```javascript
const material = new THREE.ShaderMaterial({
  vertexShader: `
    varying vec3 vNormal;
    varying vec3 vWorldPosition;
    void main() {
      vNormal = normalize(normalMatrix * normal);
      vWorldPosition = (modelMatrix * vec4(position, 1.0)).xyz;
      gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
    }
  `,
  fragmentShader: `
    varying vec3 vNormal;
    varying vec3 vWorldPosition;
    void main() {
      vec3 viewDirection = normalize(cameraPosition - vWorldPosition);
      float fresnel = pow(1.0 - dot(viewDirection, vNormal), 3.0);
      vec3 baseColor = vec3(0.0, 0.0, 0.5);
      vec3 fresnelColor = vec3(0.5, 0.8, 1.0);
      gl_FragColor = vec4(mix(baseColor, fresnelColor, fresnel), 1.0);
    }
  `,
});
```

## Noise-Based Effects

```glsl
float random(vec2 st) {
  return fract(sin(dot(st.xy, vec2(12.9898, 78.233))) * 43758.5453);
}

float noise(vec2 st) {
  vec2 i = floor(st);
  vec2 f = fract(st);
  float a = random(i), b = random(i + vec2(1.0, 0.0));
  float c = random(i + vec2(0.0, 1.0)), d = random(i + vec2(1.0, 1.0));
  vec2 u = f * f * (3.0 - 2.0 * f);
  return mix(a, b, u.x) + (c - a) * u.y * (1.0 - u.x) + (d - b) * u.x * u.y;
}

float n = noise(vUv * 10.0 + time);
```
