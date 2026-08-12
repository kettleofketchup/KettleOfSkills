# Geometry: Built-in Shapes

## Basic Shapes

```javascript
// Box - width, height, depth, widthSegments, heightSegments, depthSegments
new THREE.BoxGeometry(1, 1, 1, 1, 1, 1);

// Sphere - radius, widthSegments, heightSegments, phiStart, phiLength, thetaStart, thetaLength
new THREE.SphereGeometry(1, 32, 32);
new THREE.SphereGeometry(1, 32, 32, 0, Math.PI); // Hemisphere

// Plane
new THREE.PlaneGeometry(10, 10, 1, 1);

// Circle - radius, segments, thetaStart, thetaLength
new THREE.CircleGeometry(1, 32);
new THREE.CircleGeometry(1, 32, 0, Math.PI); // Semicircle

// Cylinder - radiusTop, radiusBottom, height, radialSegments, heightSegments, openEnded
new THREE.CylinderGeometry(1, 1, 2, 32, 1, false);
new THREE.CylinderGeometry(0, 1, 2, 32);  // Cone
new THREE.CylinderGeometry(1, 1, 2, 6);   // Hexagonal prism

// Cone
new THREE.ConeGeometry(1, 2, 32, 1, false);

// Torus
new THREE.TorusGeometry(1, 0.4, 16, 100);

// TorusKnot
new THREE.TorusKnotGeometry(1, 0.4, 100, 16, 2, 3);

// Ring - innerRadius, outerRadius, thetaSegments, phiSegments
new THREE.RingGeometry(0.5, 1, 32, 1);
```

## Advanced Shapes

```javascript
new THREE.CapsuleGeometry(0.5, 1, 4, 8);
new THREE.DodecahedronGeometry(1, 0);
new THREE.IcosahedronGeometry(1, 0); // 0=20 faces, higher=smoother
new THREE.OctahedronGeometry(1, 0);
new THREE.TetrahedronGeometry(1, 0);

// Custom polyhedron
const vertices = [1, 1, 1, -1, -1, 1, -1, 1, -1, 1, -1, -1];
const indices = [2, 1, 0, 0, 3, 2, 1, 3, 0, 2, 3, 1];
new THREE.PolyhedronGeometry(vertices, indices, 1, 0);
```

## Path-Based Shapes

```javascript
// Lathe - revolve profile around Y axis
const points = [
  new THREE.Vector2(0, 0), new THREE.Vector2(0.5, 0),
  new THREE.Vector2(0.5, 1), new THREE.Vector2(0, 1),
];
new THREE.LatheGeometry(points, 32);

// Extrude - extend 2D shape
const shape = new THREE.Shape();
shape.moveTo(0, 0); shape.lineTo(1, 0);
shape.lineTo(1, 1); shape.lineTo(0, 1); shape.lineTo(0, 0);
new THREE.ExtrudeGeometry(shape, { steps: 2, depth: 1, bevelEnabled: true, bevelThickness: 0.1, bevelSize: 0.1, bevelSegments: 3 });

// Tube - extrude along curve
const curve = new THREE.CatmullRomCurve3([
  new THREE.Vector3(-1, 0, 0), new THREE.Vector3(0, 1, 0), new THREE.Vector3(1, 0, 0)
]);
new THREE.TubeGeometry(curve, 64, 0.2, 8, false);
```

## Text Geometry

```javascript
import { FontLoader } from "three/examples/jsm/loaders/FontLoader.js";
import { TextGeometry } from "three/examples/jsm/geometries/TextGeometry.js";

const loader = new FontLoader();
loader.load("fonts/helvetiker_regular.typeface.json", (font) => {
  const geometry = new TextGeometry("Hello", {
    font: font, size: 1, depth: 0.2, curveSegments: 12,
    bevelEnabled: true, bevelThickness: 0.03, bevelSize: 0.02, bevelSegments: 5,
  });
  geometry.computeBoundingBox();
  geometry.center();
  scene.add(new THREE.Mesh(geometry, material));
});
```
