# Textures: Types and Material Maps

## Texture Types

### Standard 2D Texture
```javascript
const texture = new THREE.Texture(image);
texture.needsUpdate = true; // required after manual creation

// Or use loader (auto-updates)
const texture = new THREE.TextureLoader().load('image.jpg');
```

### Canvas Texture
```javascript
const canvas = document.createElement('canvas');
const ctx = canvas.getContext('2d');
// Draw on canvas...
const texture = new THREE.CanvasTexture(canvas);
```

### Video Texture
```javascript
const video = document.createElement('video');
video.src = 'video.mp4';
video.play();
const texture = new THREE.VideoTexture(video);
```

### Data Texture
```javascript
const size = 512;
const data = new Uint8Array(size * size * 4);
// Fill data with RGBA values...
const texture = new THREE.DataTexture(data, size, size);
texture.needsUpdate = true;
```

### Cube Texture (Environment/Skybox)
```javascript
const loader = new THREE.CubeTextureLoader();
const texture = loader.load(['px.jpg', 'nx.jpg', 'py.jpg', 'ny.jpg', 'pz.jpg', 'nz.jpg']);
```

### Advanced Texture Types
```javascript
// 3D Texture (volumetric)
const texture3d = new THREE.Data3DTexture(data, width, height, depth);

// Depth Texture (for advanced effects)
const depthTexture = new THREE.DepthTexture(width, height);

// Compressed Texture
const compressedTexture = new THREE.CompressedTexture(mipmaps, width, height);
```

## Material Maps

```javascript
const material = new THREE.MeshStandardMaterial({
  map: diffuseTexture,           // base color
  normalMap: normalTexture,       // surface detail
  roughnessMap: roughnessTexture, // surface roughness variation
  metalnessMap: metalnessTexture, // metallic areas
  aoMap: aoTexture,               // ambient occlusion
  emissiveMap: emissiveTexture,   // glow areas
  alphaMap: alphaTexture,         // transparency
  bumpMap: bumpTexture,           // height variation
  displacementMap: dispTexture    // vertex displacement
});

// AO map requires second UV set
geometry.setAttribute('uv2', geometry.attributes.uv);
```

## Color Space

```javascript
// For color data (diffuse, emissive)
texture.colorSpace = THREE.SRGBColorSpace;

// For non-color data (normal, roughness, etc.)
texture.colorSpace = THREE.NoColorSpace; // or LinearSRGBColorSpace
```
