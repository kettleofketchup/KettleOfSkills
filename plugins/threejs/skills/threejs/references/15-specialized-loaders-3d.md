# Specialized Loaders: 3D Formats

## SVG Loader

Load and extrude SVG paths:

```javascript
import { SVGLoader } from 'three/addons/loaders/SVGLoader.js';

const loader = new SVGLoader();
loader.load('image.svg', (data) => {
  const group = new THREE.Group();

  data.paths.forEach((path) => {
    const material = new THREE.MeshBasicMaterial({
      color: path.color, side: THREE.DoubleSide, depthWrite: false
    });
    const shapes = SVGLoader.createShapes(path);
    shapes.forEach((shape) => {
      const geometry = new THREE.ShapeGeometry(shape);
      group.add(new THREE.Mesh(geometry, material));
    });
  });

  // Or extrude SVG
  data.paths.forEach((path) => {
    const shapes = SVGLoader.createShapes(path);
    const geometry = new THREE.ExtrudeGeometry(shapes, { depth: 10, bevelEnabled: false });
    group.add(new THREE.Mesh(geometry, material));
  });

  scene.add(group);
});
```

## STL and 3MF Loaders (3D Printing)

```javascript
import { STLLoader } from 'three/addons/loaders/STLLoader.js';
const loader = new STLLoader();
loader.load('model.stl', (geometry) => {
  const material = new THREE.MeshPhongMaterial({ color: 0xff5533 });
  const mesh = new THREE.Mesh(geometry, material);
  geometry.computeVertexNormals(); // STL doesn't include normals
  scene.add(mesh);
});

// 3MF loader
import { /* 3MFLoader */ } from 'three/addons/loaders/3MFLoader.js';
const loader = new ThreeMFLoader(); // named ThreeMFLoader in Three.js
loader.load('model.3mf', (object) => scene.add(object));
```

## Collada and VRML

```javascript
import { ColladaLoader } from 'three/addons/loaders/ColladaLoader.js';
const loader = new ColladaLoader();
loader.load('model.dae', (collada) => {
  scene.add(collada.scene);
  const mixer = new THREE.AnimationMixer(collada.scene);
  collada.animations.forEach(clip => mixer.clipAction(clip).play());
});

import { VRMLLoader } from 'three/addons/loaders/VRMLLoader.js';
const loader = new VRMLLoader();
loader.load('model.wrl', (object) => scene.add(object));
```

## Scientific and Domain-Specific

```javascript
// PDB (protein data bank - molecular visualization)
import { PDBLoader } from 'three/addons/loaders/PDBLoader.js';
const loader = new PDBLoader();
loader.load('molecule.pdb', (pdb) => {
  const atoms = new THREE.Mesh(pdb.geometryAtoms, new THREE.MeshPhongMaterial({ color: 0xffffff }));
  const bonds = new THREE.Mesh(pdb.geometryBonds, new THREE.MeshPhongMaterial({ color: 0xcccccc }));
  scene.add(atoms, bonds);
});

// VTK (scientific visualization)
import { VTKLoader } from 'three/addons/loaders/VTKLoader.js';
const loader = new VTKLoader();
loader.load('model.vtk', (geometry) => {
  geometry.computeVertexNormals();
  scene.add(new THREE.Mesh(geometry, new THREE.MeshStandardMaterial()));
});

// PLY (point clouds, scanned data)
import { PLYLoader } from 'three/addons/loaders/PLYLoader.js';
const loader = new PLYLoader();
loader.load('model.ply', (geometry) => {
  geometry.computeVertexNormals();
  const material = geometry.attributes.color ?
    new THREE.MeshStandardMaterial({ vertexColors: true }) :
    new THREE.MeshStandardMaterial({ color: 0x888888 });
  scene.add(new THREE.Mesh(geometry, material));
});
```
