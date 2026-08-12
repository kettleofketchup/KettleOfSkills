# Animations: Keyframes and Manual Animation

## Creating Custom Animations

Using KeyframeTracks:

```javascript
// Position animation
const times = [0, 1, 2]; // keyframe times in seconds
const values = [0, 0, 0,  10, 0, 0,  0, 0, 0]; // x,y,z per keyframe

const positionKF = new THREE.VectorKeyframeTrack('.position', times, values);

// Rotation animation (quaternions)
const q1 = new THREE.Quaternion();
const q2 = new THREE.Quaternion().setFromEuler(new THREE.Euler(0, Math.PI, 0));
const rotationKF = new THREE.QuaternionKeyframeTrack(
  '.quaternion', [0, 1],
  [q1.x, q1.y, q1.z, q1.w, q2.x, q2.y, q2.z, q2.w]
);

// Create clip from tracks
const clip = new THREE.AnimationClip('custom', 2, [positionKF, rotationKF]);
const mixer = new THREE.AnimationMixer(object);
mixer.clipAction(clip).play();
```

## Keyframe Track Types

```javascript
new THREE.VectorKeyframeTrack('.position', times, values);
new THREE.VectorKeyframeTrack('.scale', times, values);
new THREE.QuaternionKeyframeTrack('.quaternion', times, values);
new THREE.ColorKeyframeTrack('.material.color', times, values);
new THREE.NumberKeyframeTrack('.material.opacity', times, values);
new THREE.BooleanKeyframeTrack('.visible', times, values);
```

## Manual Animation

Simple transform animations using Clock:

```javascript
const clock = new THREE.Clock();

function animate() {
  const elapsed = clock.getElapsedTime();

  // Rotate
  object.rotation.y = elapsed;

  // Oscillate position
  object.position.y = Math.sin(elapsed * 2) * 5;

  // Pulse scale
  const scale = 1 + Math.sin(elapsed * 3) * 0.1;
  object.scale.set(scale, scale, scale);

  renderer.render(scene, camera);
  requestAnimationFrame(animate);
}
```

## Tween Libraries

For complex easing, use GSAP:

```javascript
import gsap from 'gsap';

// Position tween
gsap.to(object.position, { duration: 1, x: 10, ease: "power2.inOut" });

// Camera animation
gsap.to(camera.position, {
  duration: 2,
  x: 5, y: 3, z: 10,
  onUpdate: () => camera.lookAt(0, 0, 0)
});

// Multiple properties
gsap.to(mesh.rotation, {
  duration: 1,
  y: Math.PI * 2,
  repeat: -1,  // infinite
  ease: "none"
});
```

## State Machine Pattern

```javascript
class CharacterAnimator {
  constructor(mixer, animations) {
    this.mixer = mixer;
    this.actions = {};
    animations.forEach(clip => {
      this.actions[clip.name] = mixer.clipAction(clip);
    });
    this.current = null;
  }

  play(name, crossFadeDuration = 0.3) {
    const next = this.actions[name];
    if (!next || next === this.current) return;
    if (this.current) this.current.crossFadeTo(next, crossFadeDuration, true);
    next.reset().play();
    this.current = next;
  }
}
```
