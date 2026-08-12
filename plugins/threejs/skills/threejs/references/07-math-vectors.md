# Math: Vectors, Quaternions, and Matrices

## Vector3

```javascript
const v = new THREE.Vector3(x, y, z);

// Operations
v.add(otherVector); v.sub(otherVector);
v.multiply(otherVector); v.multiplyScalar(scalar);
v.divide(otherVector); v.divideScalar(scalar);

// Analysis
v.length(); v.lengthSq();   // lengthSq is faster
v.normalize();
v.dot(otherVector); v.cross(otherVector);
v.distanceTo(otherVector); v.angleTo(otherVector);

// Interpolation
v.lerp(targetVector, alpha);
v.lerpVectors(v1, v2, alpha);

// Clamping
v.clamp(minVector, maxVector);
v.clampLength(minLength, maxLength);
```

## Vector2 and Vector4

```javascript
const v2 = new THREE.Vector2(x, y);
const v4 = new THREE.Vector4(x, y, z, w);
```

## Quaternion

Rotation representation (avoids gimbal lock):

```javascript
const q = new THREE.Quaternion(x, y, z, w);

q.setFromEuler(new THREE.Euler(x, y, z, 'XYZ'));

const axis = new THREE.Vector3(0, 1, 0);
q.setFromAxisAngle(axis, Math.PI / 2);

q.setFromRotationMatrix(matrix);

q.slerp(targetQuaternion, alpha); // spherical linear interpolation

// Apply to vector
const v = new THREE.Vector3(1, 0, 0);
v.applyQuaternion(q);
```

## Euler

Rotation as XYZ angles:

```javascript
const euler = new THREE.Euler(x, y, z, 'XYZ');
// Order: 'XYZ', 'YXZ', 'ZXY', 'ZYX', 'YZX', 'XZY'

euler.setFromQuaternion(q);
euler.setFromRotationMatrix(matrix);

object.rotation.copy(euler);
```

## Matrix4

```javascript
const m = new THREE.Matrix4();

m.compose(position, quaternion, scale);
const pos = new THREE.Vector3(), quat = new THREE.Quaternion(), scale = new THREE.Vector3();
m.decompose(pos, quat, scale);

m.makeTranslation(x, y, z);
m.makeRotationX(theta); m.makeRotationY(theta); m.makeRotationZ(theta);
m.makeScale(x, y, z);
m.multiply(otherMatrix);
m.premultiply(otherMatrix);
m.invert();

// Apply to vector
const v = new THREE.Vector3(1, 2, 3);
v.applyMatrix4(m);
```
