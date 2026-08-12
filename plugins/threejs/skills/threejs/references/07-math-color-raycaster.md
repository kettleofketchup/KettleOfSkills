# Math: Color, Raycaster, and Geometry Bounds

## Color

```javascript
const color = new THREE.Color(0xff0000);
const color = new THREE.Color('red');
const color = new THREE.Color(1, 0, 0); // RGB 0-1

// Conversions
color.getHex();       // 0xff0000
color.getHexString(); // "ff0000"
color.getStyle();     // "rgb(255,0,0)"

// Color spaces
color.setHSL(h, s, l);
const hsl = {};
color.getHSL(hsl);

// Operations
color.add(otherColor);
color.multiply(otherColor);
color.lerp(targetColor, alpha);
```

## MathUtils

```javascript
THREE.MathUtils.clamp(value, min, max);
THREE.MathUtils.lerp(start, end, alpha);
THREE.MathUtils.mapLinear(value, inMin, inMax, outMin, outMax);
THREE.MathUtils.degToRad(degrees);
THREE.MathUtils.radToDeg(radians);
THREE.MathUtils.randFloat(min, max);
THREE.MathUtils.randInt(min, max);
THREE.MathUtils.smoothstep(x, min, max);
```

## Raycaster

Ray intersection testing:

```javascript
const raycaster = new THREE.Raycaster();
const mouse = new THREE.Vector2();

mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;

raycaster.setFromCamera(mouse, camera);
const intersects = raycaster.intersectObjects(scene.children, true);

if (intersects.length > 0) {
  const hit = intersects[0];
  console.log(hit.object);   // intersected object
  console.log(hit.point);    // intersection point (Vector3)
  console.log(hit.distance); // distance from camera
  console.log(hit.face);     // intersected face
}
```

## Box3

Axis-aligned bounding box:

```javascript
const box = new THREE.Box3();
box.setFromObject(mesh);
box.setFromPoints(arrayOfVector3);

box.min; box.max;            // Vector3
box.getCenter(target);       // fills target Vector3
box.getSize(target);         // fills target Vector3
box.containsPoint(point);
box.intersectsBox(otherBox);
```

## Sphere and Plane

```javascript
// Bounding sphere
const sphere = new THREE.Sphere(center, radius);
const box = new THREE.Box3().setFromObject(mesh);
box.getBoundingSphere(sphere);
sphere.containsPoint(point);
sphere.intersectsSphere(otherSphere);

// Infinite plane
const plane = new THREE.Plane(normal, constant);
plane.setFromCoplanarPoints(p1, p2, p3);
plane.distanceToPoint(point);
const projected = new THREE.Vector3();
plane.projectPoint(point, projected);
```
