// Render por pasadas del mundo Three.js: beauty / albedo / normal / depth(16-bit log empaquetado en RG)
import * as THREE from 'three';
import { buildWorld, buildSky } from './world.js';

const q = new URLSearchParams(location.search);
const W = +q.get('w') || 1600, H = +q.get('h') || 1000;
const cam = JSON.parse(q.get('cam'));            // {lens, loc:[x,y,z], look:[x,y,z]} en coords Blender
const seed = +q.get('seed') || 4;
const B2T = (v) => new THREE.Vector3(v[0], v[2], -v[1]);

const renderer = new THREE.WebGLRenderer({ antialias: true, preserveDrawingBuffer: true });
renderer.setSize(W, H, false); renderer.setPixelRatio(1);
renderer.shadowMap.enabled = true; renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.outputColorSpace = THREE.SRGBColorSpace;
document.body.appendChild(renderer.domElement);

const scene = new THREE.Scene();
const world = buildWorld({ seed });
const holder = new THREE.Group(); holder.rotation.x = -Math.PI / 2; holder.add(world); scene.add(holder);
const { sky, clouds, sun } = buildSky();
scene.add(sky); world.add(clouds);
scene.fog = new THREE.FogExp2(0xe6b7a2, 0.00028);

const hemi = new THREE.HemisphereLight(0xc8d0f0, 0x9a7a68, 1.9); scene.add(hemi);
const sunL = new THREE.DirectionalLight(0xffd2a0, 3.6);
const sunT = new THREE.Vector3(sun.x, sun.z, -sun.y).normalize();
sunL.position.copy(sunT.clone().multiplyScalar(160)); sunL.target.position.set(0, 0, 0);
sunL.castShadow = true; sunL.shadow.mapSize.set(4096, 4096);
const sc = sunL.shadow.camera; sc.left = -60; sc.right = 60; sc.top = 60; sc.bottom = -60; sc.near = 1; sc.far = 500; sunL.shadow.bias = -0.0004;
scene.add(sunL, sunL.target);

const camera = new THREE.PerspectiveCamera(1, W / H, 0.2, 9000);
const hfov = 2 * Math.atan(18 / cam.lens);
camera.fov = THREE.MathUtils.radToDeg(2 * Math.atan(Math.tan(hfov / 2) * H / W));
camera.position.copy(B2T(cam.loc)); camera.lookAt(B2T(cam.look)); camera.updateProjectionMatrix();

const out = {};
const grab = (name) => { out[name] = renderer.domElement.toDataURL('image/png'); };
const store = new Map();
function swapMaterials(fn) { scene.traverse(o => { if (o.isMesh && o !== sky) { if (!store.has(o)) store.set(o, o.material); o.material = fn(store.get(o), o); } }); }
function restore() { store.forEach((m, o) => { o.material = m; }); }

// 1) beauty
renderer.render(scene, camera); grab('beauty');
// 2) albedo
scene.fog = null; hemi.visible = sunL.visible = false;
swapMaterials((m) => new THREE.MeshBasicMaterial({ color: m.color ? m.color : 0xffffff, map: m.map || null, side: m.side, vertexColors: !!m.vertexColors }));
renderer.render(scene, camera); grab('albedo'); restore();
// 3) normal (vista) y 4) depth
const nm = new THREE.ShaderMaterial({ side: THREE.DoubleSide,
  vertexShader: 'varying vec3 vN; void main(){ vN = normalize(normalMatrix*normal); gl_Position = projectionMatrix*modelViewMatrix*vec4(position,1.); }',
  fragmentShader: 'varying vec3 vN; void main(){ vec3 n = normalize(vN); if(!gl_FrontFacing) n=-n; gl_FragColor = vec4(n*0.5+0.5, 1.); }' });
const dm = new THREE.ShaderMaterial({ side: THREE.DoubleSide,
  vertexShader: 'varying float vZ; void main(){ vec4 mv = modelViewMatrix*vec4(position,1.); vZ = -mv.z; gl_Position = projectionMatrix*mv; }',
  fragmentShader: `varying float vZ; void main(){ float v = clamp(log(vZ/3.0)/log(6000.0/3.0), 0., 1.); float r = floor(v*255.)/255.; float g = fract(v*255.); gl_FragColor = vec4(r,g,0.,1.); }` });
clouds.visible = false;
const skyMat = sky.material;
sky.material = new THREE.MeshBasicMaterial({ color: new THREE.Color(0.5, 0.5, 1.0), side: THREE.BackSide }); // normal del cielo
scene.overrideMaterial = nm; renderer.setClearColor(0x8080ff, 1); renderer.render(scene, camera); grab('normal');
sky.material = new THREE.ShaderMaterial({ side: THREE.BackSide, vertexShader: 'void main(){ gl_Position = projectionMatrix*modelViewMatrix*vec4(position,1.); }', fragmentShader: 'void main(){ gl_FragColor = vec4(1.,1.,0.,1.); }' });
scene.overrideMaterial = dm; renderer.setClearColor(0xffff00, 1); renderer.render(scene, camera); grab('depth');
window.__out = out; window.__done = true;
