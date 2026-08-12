# Shaders: Extending Built-in Materials and GLSL Reference

## onBeforeCompile - Modify Existing Shaders

```javascript
const material = new THREE.MeshStandardMaterial({ color: 0x00ff00 });

material.onBeforeCompile = (shader) => {
  shader.uniforms.time = { value: 0 };
  material.userData.shader = shader;

  // Modify vertex shader
  shader.vertexShader = "uniform float time;\n" + shader.vertexShader;
  shader.vertexShader = shader.vertexShader.replace(
    "#include <begin_vertex>",
    `
    #include <begin_vertex>
    transformed.y += sin(position.x * 10.0 + time) * 0.1;
    `
  );
};

// Update in animation loop
if (material.userData.shader) {
  material.userData.shader.uniforms.time.value = clock.getElapsedTime();
}
```

## Common Injection Points

```javascript
// Vertex shader chunks
"#include <begin_vertex>";      // After position is calculated
"#include <project_vertex>";    // After gl_Position
"#include <beginnormal_vertex>"; // Normal calculation start

// Fragment shader chunks
"#include <color_fragment>";    // After diffuse color
"#include <output_fragment>";   // Final output
"#include <fog_fragment>";      // After fog applied
```

## GLSL Built-in Functions

```glsl
// Math
abs(x), sign(x), floor(x), ceil(x), fract(x)
mod(x, y), min(x, y), max(x, y), clamp(x, min, max)
mix(a, b, t), step(edge, x), smoothstep(edge0, edge1, x)

// Trigonometry
sin(x), cos(x), tan(x)
asin(x), acos(x), atan(y, x), atan(x)
radians(degrees), degrees(radians)

// Exponential
pow(x, y), exp(x), log(x), exp2(x), log2(x)
sqrt(x), inversesqrt(x)

// Vector
length(v), distance(p0, p1), dot(x, y), cross(x, y)
normalize(v), reflect(I, N), refract(I, N, eta)
lessThan(x, y), greaterThan(x, y), equal(x, y)
any(bvec), all(bvec)
```

## Texture Functions

```glsl
// GLSL 1.0 (default)
texture2D(sampler, coord)
texture2D(sampler, coord, bias)
textureCube(sampler, coord)

// GLSL 3.0 (glslVersion: THREE.GLSL3)
// Use texture() instead, and: out vec4 fragColor instead of gl_FragColor
texture(sampler, coord)
textureSize(sampler, lod)  // GLSL 1.30+
```

## ShaderMaterial Properties

```javascript
const material = new THREE.ShaderMaterial({
  uniforms: { /* ... */ },
  vertexShader: "/* ... */",
  fragmentShader: "/* ... */",
  transparent: true,
  opacity: 1.0,
  side: THREE.DoubleSide,
  depthTest: true,
  depthWrite: true,
  blending: THREE.NormalBlending,
  wireframe: false,
  extensions: {
    derivatives: true,     // For fwidth, dFdx, dFdy
    fragDepth: true,       // gl_FragDepth
    drawBuffers: true,     // Multiple render targets
    shaderTextureLOD: true // texture2DLod
  },
  glslVersion: THREE.GLSL3, // WebGL2 features
});
```

## Three.js Shader Chunks

```javascript
import { ShaderChunk } from "three";

const fragmentShader = `
  ${ShaderChunk.common}
  ${ShaderChunk.packing}
  
  uniform sampler2D depthTexture;
  varying vec2 vUv;
  
  void main() {
    float depth = texture2D(depthTexture, vUv).r;
    float linearDepth = perspectiveDepthToViewZ(depth, 0.1, 1000.0);
    gl_FragColor = vec4(vec3(-linearDepth / 100.0), 1.0);
  }
`;
```
