# Animations: System and Playback

## Animation System

Three.js uses AnimationMixer for playback:

```javascript
const mixer = new THREE.AnimationMixer(object);
const action = mixer.clipAction(animationClip);
action.play();

const clock = new THREE.Clock();
function animate() {
  const delta = clock.getDelta();
  mixer.update(delta);
  renderer.render(scene, camera);
  requestAnimationFrame(animate);
}
```

## Loading Animations (GLTF/FBX)

```javascript
const loader = new GLTFLoader();
loader.load('model.gltf', (gltf) => {
  scene.add(gltf.scene);
  const mixer = new THREE.AnimationMixer(gltf.scene);

  // Play all animations
  gltf.animations.forEach((clip) => mixer.clipAction(clip).play());

  // Play specific animation
  const clip = THREE.AnimationClip.findByName(gltf.animations, 'Walk');
  const action = mixer.clipAction(clip);
  action.play();
});
```

## Animation Actions

```javascript
const action = mixer.clipAction(clip);

action.play(); action.stop(); action.pause(); action.reset();

// Loop modes
action.setLoop(THREE.LoopRepeat, Infinity);   // loop forever
action.setLoop(THREE.LoopOnce, 1);            // play once
action.setLoop(THREE.LoopPingPong, Infinity); // reverse on each loop

action.timeScale = 1.5;  // 1.5x speed
action.timeScale = -1;   // reverse

action.setEffectiveWeight(0.5); // 50% influence
action.enabled = true;
```

## Animation Blending

```javascript
currentAction.crossFadeTo(nextAction, 0.5, true); // 0.5 second transition

// Or manually
currentAction.fadeOut(0.5);
nextAction.reset().fadeIn(0.5).play();
```

## Skeletal and Morph Target Animation

```javascript
// Skeletal (rigged characters)
const mesh = gltf.scene.children.find(child => child.isSkinnedMesh);
const skeleton = mesh.skeleton;
skeleton.bones[0].rotation.x = Math.PI / 4; // Manual bone control
const helper = new THREE.SkeletonHelper(mesh);
scene.add(helper);

// Morph targets (blend shapes)
mesh.morphTargetInfluences[0] = 0.5; // 50% of first morph target
const track = new THREE.NumberKeyframeTrack(
  '.morphTargetInfluences[0]', [0, 1, 2], [0, 1, 0]
);
const clip = new THREE.AnimationClip('morph', 2, [track]);
```
