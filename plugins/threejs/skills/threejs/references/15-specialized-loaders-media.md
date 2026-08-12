# Specialized Loaders: Fonts, LEGO, and Export

## LDraw Loader (LEGO)

```javascript
import { LDrawLoader } from 'three/addons/loaders/LDrawLoader.js';

const loader = new LDrawLoader();
loader.setPath('ldraw/');
loader.load('model.mpd', (group) => {
  scene.add(group);
  group.traverse((child) => {
    if (child.isMesh) child.material.flatShading = false;
  });
});
```

## 3DS Max Format

```javascript
import { TDSLoader } from 'three/addons/loaders/TDSLoader.js';
const loader = new TDSLoader();
loader.load('model.3ds', (object) => scene.add(object));
```

## Font Loader (3D Text)

```javascript
import { FontLoader } from 'three/addons/loaders/FontLoader.js';
import { TextGeometry } from 'three/addons/geometries/TextGeometry.js';

const fontLoader = new FontLoader();
fontLoader.load('fonts/helvetiker_regular.typeface.json', (font) => {
  const geometry = new TextGeometry('Hello World', {
    font: font,
    size: 80,
    depth: 5,
    curveSegments: 12,
    bevelEnabled: true,
    bevelThickness: 10,
    bevelSize: 8,
    bevelSegments: 5
  });
  const material = new THREE.MeshPhongMaterial({ color: 0x00ff00 });
  scene.add(new THREE.Mesh(geometry, material));
});
```

## EXR and HDR Loaders

```javascript
import { EXRLoader } from 'three/addons/loaders/EXRLoader.js';
const loader = new EXRLoader();
loader.load('env.exr', (texture) => {
  texture.mapping = THREE.EquirectangularReflectionMapping;
  scene.background = texture;
  scene.environment = texture;
});

import { RGBELoader } from 'three/addons/loaders/RGBELoader.js';
const loader = new RGBELoader();
loader.load('env.hdr', (texture) => {
  texture.mapping = THREE.EquirectangularReflectionMapping;
  scene.background = texture;
  scene.environment = texture;

  // Use PMREMGenerator for better quality
  const pmremGenerator = new THREE.PMREMGenerator(renderer);
  const envMap = pmremGenerator.fromEquirectangular(texture).texture;
  scene.environment = envMap;
  texture.dispose();
  pmremGenerator.dispose();
});
```

## USDZ Exporter (Apple AR)

```javascript
import { USDZExporter } from 'three/addons/exporters/USDZExporter.js';

const exporter = new USDZExporter();
const arraybuffer = await exporter.parse(scene);
const blob = new Blob([arraybuffer], { type: 'application/octet-stream' });

const link = document.createElement('a');
link.href = URL.createObjectURL(blob);
link.download = 'model.usdz';
link.click();
```

## Basis/KTX2 Texture Loader

```javascript
import { KTX2Loader } from 'three/addons/loaders/KTX2Loader.js';

const loader = new KTX2Loader();
loader.setTranscoderPath('basis/');
loader.detectSupport(renderer);
loader.load('texture.ktx2', (texture) => {
  material.map = texture;
  material.needsUpdate = true;
});
```
