# Asset Loading: Standard Loaders

## Loading Manager

Coordinate multiple loads, track progress:

```javascript
const manager = new THREE.LoadingManager();
manager.onStart = (url, loaded, total) => console.log('Loading:', url);
manager.onProgress = (url, loaded, total) => console.log(`${loaded}/${total}`);
manager.onLoad = () => console.log('Complete');
manager.onError = (url) => console.error('Error:', url);

const loader = new THREE.TextureLoader(manager);
```

## GLTF Loader (Recommended Format)

Industry standard, supports PBR materials, animations, bones:

```javascript
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';

const loader = new GLTFLoader();
loader.load(
  'model.gltf',
  (gltf) => {
    scene.add(gltf.scene);
    const mixer = new THREE.AnimationMixer(gltf.scene);
    gltf.animations.forEach((clip) => mixer.clipAction(clip).play());
  },
  (xhr) => console.log((xhr.loaded / xhr.total * 100) + '% loaded'),
  (error) => console.error(error)
);
```

## FBX and OBJ Loaders

```javascript
import { FBXLoader } from 'three/addons/loaders/FBXLoader.js';
const loader = new FBXLoader();
loader.load('model.fbx', (object) => scene.add(object));

// OBJ with material library
import { OBJLoader } from 'three/addons/loaders/OBJLoader.js';
import { MTLLoader } from 'three/addons/loaders/MTLLoader.js';
const mtlLoader = new MTLLoader();
mtlLoader.load('model.mtl', (materials) => {
  materials.preload();
  const objLoader = new OBJLoader();
  objLoader.setMaterials(materials);
  objLoader.load('model.obj', (object) => scene.add(object));
});
```

## Texture Loader

```javascript
const textureLoader = new THREE.TextureLoader();
const texture = textureLoader.load('texture.jpg');
const material = new THREE.MeshStandardMaterial({ map: texture });

textureLoader.load(
  'texture.jpg',
  (texture) => { material.map = texture; material.needsUpdate = true; },
  (xhr) => console.log((xhr.loaded / xhr.total * 100) + '% loaded'),
  (error) => console.error(error)
);
```

## Cube Texture Loader

```javascript
const cubeLoader = new THREE.CubeTextureLoader();
const envMap = cubeLoader.load([
  'px.jpg', 'nx.jpg',
  'py.jpg', 'ny.jpg',
  'pz.jpg', 'nz.jpg'
]);
scene.background = envMap;
material.envMap = envMap;
```
