# Materials: Physical, Toon, Points, and Lines

## MeshPhysicalMaterial (Advanced PBR)

Extends MeshStandardMaterial:

```javascript
const material = new THREE.MeshPhysicalMaterial({
  // Clearcoat (car paint, lacquer)
  clearcoat: 1.0,
  clearcoatRoughness: 0.1,
  clearcoatMap: ccTexture,
  clearcoatNormalMap: ccnTexture,

  // Transmission (glass, water)
  transmission: 1.0,
  transmissionMap: transTexture,
  thickness: 0.5,
  ior: 1.5,  // Index of refraction (1-2.333)
  attenuationDistance: 1,
  attenuationColor: new THREE.Color(0xffffff),

  // Sheen (fabric, velvet)
  sheen: 1.0,
  sheenRoughness: 0.5,
  sheenColor: new THREE.Color(0xffffff),

  // Iridescence (soap bubbles)
  iridescence: 1.0,
  iridescenceIOR: 1.3,
  iridescenceThicknessRange: [100, 400],

  // Anisotropy (brushed metal)
  anisotropy: 1.0,
  anisotropyRotation: 0,

  // Specular
  specularIntensity: 1,
  specularColor: new THREE.Color(0xffffff),
});

// Glass example
const glass = new THREE.MeshPhysicalMaterial({
  color: 0xffffff, metalness: 0, roughness: 0, transmission: 1, thickness: 0.5, ior: 1.5
});

// Car paint example
const carPaint = new THREE.MeshPhysicalMaterial({
  color: 0xff0000, metalness: 0.9, roughness: 0.5, clearcoat: 1, clearcoatRoughness: 0.1
});
```

## MeshToonMaterial

```javascript
const material = new THREE.MeshToonMaterial({
  color: 0x00ff00,
  gradientMap: gradientTexture,
});

// Create step gradient texture
const colors = new Uint8Array([0, 128, 255]);
const gradientMap = new THREE.DataTexture(colors, 3, 1, THREE.RedFormat);
gradientMap.minFilter = THREE.NearestFilter;
gradientMap.magFilter = THREE.NearestFilter;
gradientMap.needsUpdate = true;
```

## PointsMaterial and LineBasicMaterial

```javascript
// Point clouds
const material = new THREE.PointsMaterial({
  color: 0xffffff, size: 0.1, sizeAttenuation: true,
  map: pointTexture, alphaMap: alphaTexture, transparent: true,
  alphaTest: 0.5, vertexColors: true,
});
const points = new THREE.Points(geometry, material);

// Lines
const lineMaterial = new THREE.LineBasicMaterial({ color: 0xffffff, linewidth: 1 });

// Dashed lines
const dashedMaterial = new THREE.LineDashedMaterial({
  color: 0xffffff, dashSize: 0.5, gapSize: 0.25, scale: 1
});
const line = new THREE.Line(geometry, dashedMaterial);
line.computeLineDistances(); // required for dashed lines
```

## Common Material Properties

```javascript
material.visible = true;
material.transparent = false;
material.opacity = 1.0;
material.alphaTest = 0;
material.side = THREE.FrontSide;
material.depthTest = true;
material.depthWrite = true;
material.blending = THREE.NormalBlending;
// NormalBlending, AdditiveBlending, SubtractiveBlending, MultiplyBlending

// Polygon offset (z-fighting fix)
material.polygonOffset = false;
material.polygonOffsetFactor = 0;
material.polygonOffsetUnits = 0;
material.dithering = false;
material.toneMapped = true;
```
