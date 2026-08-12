# VR/XR Integration

## Basic WebXR Setup

```javascript
import { VRButton } from 'three/addons/webxr/VRButton.js';

renderer.xr.enabled = true;
document.body.appendChild(VRButton.createButton(renderer));

// Use setAnimationLoop instead of requestAnimationFrame for VR
renderer.setAnimationLoop(() => {
  renderer.render(scene, camera);
});
```

## AR Mode

```javascript
import { ARButton } from 'three/addons/webxr/ARButton.js';

renderer.xr.enabled = true;
document.body.appendChild(ARButton.createButton(renderer));

const session = renderer.xr.getSession();
session.requestHitTestSource({ space: viewerSpace }).then((hitTestSource) => {
  // Use hit testing for placing objects
});
```

## VR Controllers

```javascript
const controller1 = renderer.xr.getController(0);
const controller2 = renderer.xr.getController(1);
scene.add(controller1);
scene.add(controller2);

controller1.addEventListener('selectstart', () => console.log('Trigger pressed'));
controller1.addEventListener('selectend', () => console.log('Trigger released'));

// Add visual controller models
import { XRControllerModelFactory } from 'three/addons/webxr/XRControllerModelFactory.js';
const controllerModelFactory = new XRControllerModelFactory();
const grip1 = renderer.xr.getControllerGrip(0);
grip1.add(controllerModelFactory.createControllerModel(grip1));
scene.add(grip1);
```

## Hand Tracking

```javascript
import { OculusHandModel } from 'three/addons/webxr/OculusHandModel.js';

const hand1 = renderer.xr.getHand(0);
hand1.add(new OculusHandModel(hand1));
scene.add(hand1);
```

## Spatial Audio

```javascript
const listener = new THREE.AudioListener();
camera.add(listener);

const sound = new THREE.PositionalAudio(listener);
const audioLoader = new THREE.AudioLoader();
audioLoader.load('sound.ogg', (buffer) => {
  sound.setBuffer(buffer);
  sound.setRefDistance(1);
  sound.setLoop(true);
  sound.play();
});
object.add(sound); // attach to 3D object
```

## Common VR Patterns

```javascript
// Detect if in VR
if (renderer.xr.isPresenting) { /* VR mode */ }

// Different behavior for VR vs desktop
renderer.setAnimationLoop(() => {
  if (renderer.xr.isPresenting) {
    // VR rendering logic
  } else {
    // Desktop rendering logic
  }
  renderer.render(scene, camera);
});
```

## VR Performance Tips

- Target 90 FPS (11.1ms per frame)
- Use lower polygon counts
- Reduce shadow quality
- Limit post-processing
- Use instancing for repeated objects
- Enable foveated rendering if available

```javascript
// Foveated rendering (Quest 2+)
const gl = renderer.getContext();
const ext = gl.getExtension('WEBGL_foveated_rendering');
if (ext) {
  ext.foveatedRenderingModeWEBGL(gl.FOVEATED_RENDERING_MODE_ENABLE_WEBGL);
}
```
