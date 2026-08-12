# Lights: Types and Shadows

## Ambient Light

Global illumination affecting all objects equally:

```javascript
const light = new THREE.AmbientLight(0x404040);
scene.add(light);
// Often used as base illumination with other lights
```

## Directional Light

Infinite distance light with parallel rays (sun-like):

```javascript
const light = new THREE.DirectionalLight(0xffffff, 1);
light.position.set(10, 10, 5);
light.target.position.set(0, 0, 0);
scene.add(light);
scene.add(light.target); // target must be in scene

// With shadows
light.castShadow = true;
light.shadow.mapSize.width = 2048;
light.shadow.mapSize.height = 2048;
light.shadow.camera.near = 0.5;
light.shadow.camera.far = 500;
light.shadow.camera.left = -10;
light.shadow.camera.right = 10;
light.shadow.camera.top = 10;
light.shadow.camera.bottom = -10;

const helper = new THREE.CameraHelper(light.shadow.camera);
scene.add(helper);
```

## Point Light

Omnidirectional light from a point (lightbulb-like):

```javascript
const light = new THREE.PointLight(0xff0000, 1, 100, 2);
// params: color, intensity, distance (0=infinite), decay
light.position.set(0, 10, 0);
scene.add(light);
light.castShadow = true;
```

## Spot Light

Cone-shaped light:

```javascript
const light = new THREE.SpotLight(0xffffff, 1);
light.position.set(0, 10, 0);
light.target.position.set(0, 0, 0);
scene.add(light);
scene.add(light.target);
light.angle = Math.PI / 6;
light.penumbra = 0.1;   // edge softness (0-1)
light.decay = 2;
light.distance = 100;
light.castShadow = true;
```

## Hemisphere Light

Sky/ground two-color lighting:

```javascript
const light = new THREE.HemisphereLight(0x0000ff, 0x00ff00, 0.6);
scene.add(light);
// Good for outdoor scenes
```

## RectArea Light

```javascript
import { RectAreaLight } from 'three/addons/lights/RectAreaLight.js';
const light = new RectAreaLight(0xffffff, 5, 10, 10);
light.position.set(0, 5, 0);
light.lookAt(0, 0, 0);
scene.add(light);
```

## Shadow Configuration

```javascript
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
// BasicShadowMap, PCFShadowMap, PCFSoftShadowMap, VSMShadowMap

mesh.castShadow = true;
mesh.receiveShadow = true;
```
