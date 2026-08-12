# Lights: Helpers, Intensity, and Performance

## Light Helpers

Visualize light positions and directions:

```javascript
// Directional light
const helper = new THREE.DirectionalLightHelper(light, 5);
scene.add(helper);

// Point light
const helper = new THREE.PointLightHelper(light, 1);
scene.add(helper);

// Spot light
const helper = new THREE.SpotLightHelper(light);
scene.add(helper);

// Hemisphere light
const helper = new THREE.HemisphereLightHelper(light, 5);
scene.add(helper);

// RectArea light
import { RectAreaLightHelper } from 'three/addons/helpers/RectAreaLightHelper.js';
const helper = new RectAreaLightHelper(light);
light.add(helper);
```

## Light Intensity and Units

```javascript
// Intensity values for typical use:
// - Lower values (0.1-1) for ambient/hemisphere
// - Higher values (1-10) for directional/point/spot
// - Very high (10-100+) for small area lights

// Physical light units (optional)
renderer.physicallyCorrectLights = true; // deprecated in newer versions
// Use intensity in candelas (cd) for point/spot lights
```

## Environment Maps for Lighting

HDR environment maps provide realistic image-based lighting:

```javascript
import { RGBELoader } from 'three/addons/loaders/RGBELoader.js';

const rgbeLoader = new RGBELoader();
rgbeLoader.load('environment.hdr', (texture) => {
  texture.mapping = THREE.EquirectangularReflectionMapping;
  scene.environment = texture; // affects all PBR materials
  scene.background = texture;  // also use as background
});

// PMREMGenerator for better quality
const pmremGenerator = new THREE.PMREMGenerator(renderer);
const envMap = pmremGenerator.fromEquirectangular(texture).texture;
scene.environment = envMap;
```

## Performance Tips

- Limit number of lights (3-5 for good performance)
- Use ambient + 1-2 directional lights for outdoor scenes
- Bake lighting into textures for static scenes
- Use lightmaps for complex static lighting
- Shadows are expensive - use selectively
- Lower shadow map resolution for better performance

```javascript
// Reduce shadow quality for performance
light.shadow.mapSize.width = 512;  // instead of 2048
light.shadow.mapSize.height = 512;

// Limit shadow camera frustum
light.shadow.camera.far = 50;      // only cast shadows nearby
```
