# Advanced Materials: PBR, Blending, and Depth

## MeshStandardMaterial (PBR) - Full Reference

```javascript
const material = new THREE.MeshStandardMaterial({
  color: 0xffffff,
  metalness: 0.5,      // 0 = dielectric, 1 = metal
  roughness: 0.5,      // 0 = smooth/shiny, 1 = rough/matte
  map: colorTexture,
  normalMap: normalTexture,
  roughnessMap: roughnessTexture,
  metalnessMap: metalnessTexture,
  aoMap: aoTexture,    // ambient occlusion
  emissive: 0xff0000,
  emissiveMap: emissiveTexture,
  emissiveIntensity: 1.0,
  envMap: environmentMap,
  envMapIntensity: 1.0,
  alphaMap: alphaTexture,
  transparent: true,
  opacity: 1.0,
  side: THREE.DoubleSide,
  flatShading: false
});
```

## MeshPhysicalMaterial - Common Presets

```javascript
// Glass
const glass = new THREE.MeshPhysicalMaterial({
  transmission: 1.0, thickness: 0.5, ior: 1.5,
  roughness: 0, metalness: 0, envMapIntensity: 1,
});

// Car paint
const carPaint = new THREE.MeshPhysicalMaterial({
  color: 0xff0000, metalness: 0.9, roughness: 0.5,
  clearcoat: 1, clearcoatRoughness: 0.1,
});

// Fabric
const fabric = new THREE.MeshPhysicalMaterial({
  color: 0x663399, roughness: 0.8,
  sheen: 1.0, sheenRoughness: 0.5,
  sheenColor: new THREE.Color(0x9966cc),
});
```

## Material Blending

```javascript
material.blending = THREE.AdditiveBlending;
// Options:
// THREE.NoBlending
// THREE.NormalBlending (default)
// THREE.AdditiveBlending (glow/light effects)
// THREE.SubtractiveBlending
// THREE.MultiplyBlending

// Custom blending
material.blending = THREE.CustomBlending;
material.blendEquation = THREE.AddEquation;
material.blendSrc = THREE.SrcAlphaFactor;
material.blendDst = THREE.OneMinusSrcAlphaFactor;
```

## Depth and Stencil

```javascript
material.depthTest = true;
material.depthWrite = true;
material.depthFunc = THREE.LessEqualDepth;
material.alphaTest = 0.5;  // discard transparent pixels

mesh.renderOrder = 1;  // higher renders later

// Prevent z-fighting
material.polygonOffset = true;
material.polygonOffsetFactor = 1;
material.polygonOffsetUnits = 1;
```

## Shader Patterns

### Fresnel Effect
```glsl
float fresnel = pow(1.0 - dot(vNormal, vViewDirection), 3.0);
gl_FragColor = vec4(mix(baseColor, edgeColor, fresnel), 1.0);
```

### Noise/Distortion
```glsl
float noise(vec2 p) {
  return fract(sin(dot(p, vec2(12.9898, 78.233))) * 43758.5453);
}
vec2 distortedUV = vUv + vec2(noise(vUv + time) * 0.1, noise(vUv.yx + time) * 0.1);
```

### Scrolling Texture
```glsl
uniform float time;
varying vec2 vUv;
vec2 scrollUV = vUv + vec2(time * 0.1, 0.0);
vec4 color = texture2D(map, scrollUV);
```
