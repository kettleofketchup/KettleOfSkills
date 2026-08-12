# Physics Integration

Three.js doesn't include physics - use external libraries.

## Rapier Physics (Recommended)

Rust-based, high-performance:

```javascript
import { RapierPhysics } from 'three/addons/physics/RapierPhysics.js';

const physics = await RapierPhysics();

const box = new THREE.Mesh(new THREE.BoxGeometry(), new THREE.MeshStandardMaterial());
scene.add(box);
physics.addMesh(box, 1); // mass = 1 (dynamic)

const ground = new THREE.Mesh(
  new THREE.BoxGeometry(10, 0.5, 10), new THREE.MeshStandardMaterial()
);
ground.position.y = -2;
scene.add(ground);
physics.addMesh(ground); // no mass = static

function animate() {
  physics.step();
  renderer.render(scene, camera);
  requestAnimationFrame(animate);
}
```

## Ammo Physics

Port of Bullet physics engine:

```javascript
import { AmmoPhysics } from 'three/addons/physics/AmmoPhysics.js';

const physics = await AmmoPhysics();
physics.addMesh(mesh, mass);

function animate() {
  physics.step();
  renderer.render(scene, camera);
  requestAnimationFrame(animate);
}
```

## Jolt Physics

High-performance alternative:

```javascript
import { JoltPhysics } from 'three/addons/physics/JoltPhysics.js';

const physics = await JoltPhysics();
physics.addMesh(mesh, mass);
```

## Physics Constraints

```javascript
const physics = await RapierPhysics();

physics.addConstraint(meshA, meshB, 'fixed');
physics.addConstraint(meshA, meshB, 'spring', { stiffness: 100 });
physics.removeConstraint(constraint);
```

## Physics Best Practices

- Use simplified collision shapes (boxes/spheres vs mesh)
- Rapier: best for most games and simulations
- Ammo/Bullet: more mature, Blender/Godot export support
- Jolt: excellent for large-scale simulations
- Update physics step independently from render loop when possible
- Use `physics.step(delta)` with clock delta for framerate independence

```javascript
const clock = new THREE.Clock();
function animate() {
  const delta = clock.getDelta();
  physics.step(Math.min(delta, 0.05)); // cap at 50ms
  renderer.render(scene, camera);
  requestAnimationFrame(animate);
}
```
