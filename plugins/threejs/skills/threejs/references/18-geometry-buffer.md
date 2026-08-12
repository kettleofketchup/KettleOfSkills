# Geometry: BufferGeometry and Custom Attributes

## Custom BufferGeometry

```javascript
const geometry = new THREE.BufferGeometry();

// Vertices (3 floats per vertex: x, y, z)
const vertices = new Float32Array([
  -1, -1, 0,   // vertex 0
   1, -1, 0,   // vertex 1
   1,  1, 0,   // vertex 2
  -1,  1, 0,   // vertex 3
]);
geometry.setAttribute("position", new THREE.BufferAttribute(vertices, 3));

// Indices (for indexed geometry - reuse vertices)
const indices = new Uint16Array([0, 1, 2,  0, 2, 3]);
geometry.setIndex(new THREE.BufferAttribute(indices, 1));

// Normals (required for lighting)
const normals = new Float32Array([0, 0, 1,  0, 0, 1,  0, 0, 1,  0, 0, 1]);
geometry.setAttribute("normal", new THREE.BufferAttribute(normals, 3));

// UVs (for texturing)
const uvs = new Float32Array([0, 0,  1, 0,  1, 1,  0, 1]);
geometry.setAttribute("uv", new THREE.BufferAttribute(uvs, 2));

// Per-vertex colors
const colors = new Float32Array([1, 0, 0,  0, 1, 0,  0, 0, 1,  1, 1, 0]);
geometry.setAttribute("color", new THREE.BufferAttribute(colors, 3));
// Use with: material.vertexColors = true
```

## BufferAttribute Types

```javascript
new Float32Array(count * itemSize); // Positions, normals, UVs
new Uint16Array(count);             // Indices (up to 65535 vertices)
new Uint32Array(count);             // Indices (larger meshes)
new Uint8Array(count * itemSize);   // Colors (0-255 range)
// Item sizes: position=3, normal=3, uv=2, color=3/4, index=1
```

## Modifying BufferGeometry

```javascript
const positions = geometry.attributes.position;

positions.setXYZ(index, x, y, z);   // set vertex
const x = positions.getX(index);    // get vertex component

positions.needsUpdate = true;        // flag for GPU update

geometry.computeVertexNormals();     // recompute after position changes
geometry.computeBoundingBox();
geometry.computeBoundingSphere();
```

## Interleaved Buffers (Advanced)

```javascript
const interleavedBuffer = new THREE.InterleavedBuffer(
  new Float32Array([
    // pos.x, pos.y, pos.z, uv.u, uv.v (per vertex)
    -1, -1, 0, 0, 0,   1, -1, 0, 1, 0,
     1,  1, 0, 1, 1,  -1,  1, 0, 0, 1,
  ]),
  5, // stride (floats per vertex)
);

geometry.setAttribute("position", new THREE.InterleavedBufferAttribute(interleavedBuffer, 3, 0));
geometry.setAttribute("uv", new THREE.InterleavedBufferAttribute(interleavedBuffer, 2, 3));
```

## Edges and Wireframe

```javascript
// Edge lines (only hard edges)
const edges = new THREE.EdgesGeometry(boxGeometry, 15); // 15 = threshold angle
const edgeMesh = new THREE.LineSegments(edges, new THREE.LineBasicMaterial({ color: 0xffffff }));

// Wireframe (all triangles)
const wireframe = new THREE.WireframeGeometry(boxGeometry);
const wireMesh = new THREE.LineSegments(wireframe, new THREE.LineBasicMaterial({ color: 0xffffff }));
```
