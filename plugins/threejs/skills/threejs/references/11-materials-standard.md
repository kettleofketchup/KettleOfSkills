# Materials: Overview, Basic, Lambert, Phong, and Standard

## Material Types Overview

| Material | Use Case | Lighting |
|---|---|---|
| MeshBasicMaterial | Unlit, flat colors, wireframes | No |
| MeshLambertMaterial | Matte surfaces, performance | Yes (diffuse only) |
| MeshPhongMaterial | Shiny surfaces, specular highlights | Yes |
| MeshStandardMaterial | PBR, realistic materials | Yes (PBR) |
| MeshPhysicalMaterial | Advanced PBR, clearcoat, transmission | Yes (PBR+) |
| MeshToonMaterial | Cel-shaded, cartoon look | Yes (toon) |
| MeshNormalMaterial | Debug normals | No |
| MeshDepthMaterial | Depth visualization | No |
| ShaderMaterial | Custom GLSL shaders | Custom |
| RawShaderMaterial | Full shader control | Custom |

## MeshBasicMaterial

```javascript
const material = new THREE.MeshBasicMaterial({
  color: 0xff0000,
  transparent: true,
  opacity: 0.5,
  side: THREE.DoubleSide,
  wireframe: false,
  map: texture,
  alphaMap: alphaTexture,
  envMap: envTexture,
  fog: true,
});
```

## MeshLambertMaterial

```javascript
const material = new THREE.MeshLambertMaterial({
  color: 0x00ff00,
  emissive: 0x111111,
  emissiveIntensity: 1,
  map: texture,
  emissiveMap: emissiveTexture,
  envMap: envTexture,
});
```

## MeshPhongMaterial

```javascript
const material = new THREE.MeshPhongMaterial({
  color: 0x0000ff,
  specular: 0xffffff,
  shininess: 100,
  emissive: 0x000000,
  flatShading: false,
  map: texture,
  specularMap: specTexture,
  normalMap: normalTexture,
  normalScale: new THREE.Vector2(1, 1),
  bumpMap: bumpTexture,
  bumpScale: 1,
  displacementMap: dispTexture,
  displacementScale: 1,
});
```

## MeshStandardMaterial (PBR)

```javascript
const material = new THREE.MeshStandardMaterial({
  color: 0xffffff,
  roughness: 0.5,  // 0=mirror, 1=diffuse
  metalness: 0.0,  // 0=dielectric, 1=metal
  map: colorTexture,
  roughnessMap: roughTexture,
  metalnessMap: metalTexture,
  normalMap: normalTexture,
  normalScale: new THREE.Vector2(1, 1),
  aoMap: aoTexture,        // requires uv2!
  aoMapIntensity: 1,
  displacementMap: dispTexture,
  displacementScale: 0.1,
  emissive: 0x000000,
  emissiveIntensity: 1,
  emissiveMap: emissiveTexture,
  envMap: envTexture,
  envMapIntensity: 1,
  flatShading: false,
  wireframe: false,
});

// aoMap requires second UV channel
geometry.setAttribute("uv2", geometry.attributes.uv);
```
