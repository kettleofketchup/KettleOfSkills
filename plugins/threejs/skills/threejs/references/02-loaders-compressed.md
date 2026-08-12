# Asset Loading: Compressed Formats and Best Practices

## DRACO Compressed Models

Smaller file sizes for GLTF:

```javascript
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { DRACOLoader } from 'three/addons/loaders/DRACOLoader.js';

const dracoLoader = new DRACOLoader();
dracoLoader.setDecoderPath('path/to/draco/');

const loader = new GLTFLoader();
loader.setDRACOLoader(dracoLoader);
loader.load('compressed.gltf', (gltf) => scene.add(gltf.scene));
```

## KTX2 Compressed Textures

GPU-optimized texture compression:

```javascript
import { KTX2Loader } from 'three/addons/loaders/KTX2Loader.js';

const ktx2Loader = new KTX2Loader();
ktx2Loader.setTranscoderPath('path/to/basis/');
ktx2Loader.detectSupport(renderer);
ktx2Loader.load('texture.ktx2', (texture) => {
  material.map = texture;
  material.needsUpdate = true;
});
```

## HDR Environment Maps

```javascript
import { RGBELoader } from 'three/addons/loaders/RGBELoader.js';

const loader = new RGBELoader();
loader.load('env.hdr', (texture) => {
  texture.mapping = THREE.EquirectangularReflectionMapping;
  scene.environment = texture;
  scene.background = texture;
});
```

## Common Other Loaders

```javascript
import { STLLoader } from 'three/addons/loaders/STLLoader.js';     // 3D printing
import { ColladaLoader } from 'three/addons/loaders/ColladaLoader.js'; // .dae
import { TDSLoader } from 'three/addons/loaders/TDSLoader.js';     // 3DS Max
```

## Common Patterns

```javascript
// Load with progress
loader.load(
  'file.ext',
  (result) => { /* success */ },
  (xhr) => console.log((xhr.loaded / xhr.total * 100) + '% loaded'),
  (error) => console.error(error)
);

// Center imported model
const box = new THREE.Box3().setFromObject(model);
const center = box.getCenter(new THREE.Vector3());
model.position.sub(center);

// Scale to fit
const size = box.getSize(new THREE.Vector3());
const maxDim = Math.max(size.x, size.y, size.z);
model.scale.setScalar(10 / maxDim);
```

## Best Practices

- Use GLTF/GLB for web (best compression, features)
- Compress with DRACO for large models
- Use KTX2 for textures (GPU-friendly)
- Enable caching: `THREE.Cache.enabled = true`
- Show loading progress to users
- Handle errors gracefully
