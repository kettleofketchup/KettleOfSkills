# Shaders: ShaderMaterial and Uniforms

## Quick Start

```javascript
import * as THREE from "three";

const material = new THREE.ShaderMaterial({
  uniforms: {
    time: { value: 0 },
    color: { value: new THREE.Color(0xff0000) },
  },
  vertexShader: `
    void main() {
      gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
    }
  `,
  fragmentShader: `
    uniform vec3 color;
    void main() {
      gl_FragColor = vec4(color, 1.0);
    }
  `,
});

material.uniforms.time.value = clock.getElapsedTime();
```

## ShaderMaterial vs RawShaderMaterial

**ShaderMaterial** - Three.js provides built-in uniforms and attributes:
```javascript
const material = new THREE.ShaderMaterial({
  vertexShader: `
    // Built-ins available: modelMatrix, modelViewMatrix, projectionMatrix,
    // viewMatrix, normalMatrix, cameraPosition
    // Attributes: position, normal, uv
    void main() {
      gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
    }
  `,
  fragmentShader: `
    void main() { gl_FragColor = vec4(1.0, 0.0, 0.0, 1.0); }
  `,
});
```

**RawShaderMaterial** - full control, you define everything:
```javascript
const material = new THREE.RawShaderMaterial({
  uniforms: { projectionMatrix: { value: camera.projectionMatrix }, modelViewMatrix: { value: new THREE.Matrix4() } },
  vertexShader: `
    precision highp float;
    attribute vec3 position;
    uniform mat4 projectionMatrix;
    uniform mat4 modelViewMatrix;
    void main() {
      gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
    }
  `,
  fragmentShader: `
    precision highp float;
    void main() { gl_FragColor = vec4(1.0, 0.0, 0.0, 1.0); }
  `,
});
```

## Uniform Types

```javascript
const material = new THREE.ShaderMaterial({
  uniforms: {
    floatValue: { value: 1.5 },
    intValue: { value: 1 },
    vec2Value: { value: new THREE.Vector2(1, 2) },
    vec3Value: { value: new THREE.Vector3(1, 2, 3) },
    colorValue: { value: new THREE.Color(0xff0000) },  // becomes vec3
    mat4Value: { value: new THREE.Matrix4() },
    textureValue: { value: texture },
    cubeTextureValue: { value: cubeTexture },
    floatArray: { value: [1.0, 2.0, 3.0] },
    vec3Array: { value: [new THREE.Vector3(1, 0, 0), new THREE.Vector3(0, 1, 0)] },
  },
});
```

```glsl
uniform float floatValue;
uniform int intValue;
uniform vec2 vec2Value;
uniform vec3 vec3Value;
uniform vec3 colorValue;
uniform mat4 mat4Value;
uniform sampler2D textureValue;
uniform samplerCube cubeTextureValue;
uniform float floatArray[3];
uniform vec3 vec3Array[2];
```

## Updating Uniforms

```javascript
material.uniforms.time.value = clock.getElapsedTime();
material.uniforms.position.value.set(x, y, z);
material.uniforms.color.value.setHSL(hue, 1, 0.5);
material.uniforms.matrix.value.copy(mesh.matrixWorld);
```
