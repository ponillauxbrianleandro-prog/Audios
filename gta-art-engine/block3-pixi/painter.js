// Bloque 3 — PixiJS "pintor": convierte las pasadas 3D (Blender + Three.js) en arte pintado estilo GTA IV.
// Un único filtro GLSL: pinta el fondo (Three) y el personaje (Blender), los compone y aplica gradación + spray + grano.
import * as PIXI from 'pixi.js';

const q = new URLSearchParams(location.search);
const W = +q.get('w'), H = +q.get('h');
const dir = q.get('dir'), pose = q.get('pose'), bgdir = q.get('bg');
const meta = await (await fetch(`${dir}/${pose}_meta.json`)).json();

const loadImg = (u) => new Promise((res, rej) => { const i = new Image(); i.onload = () => res(i); i.onerror = rej; i.src = u; });
const src = async (u) => new PIXI.ImageSource({ resource: await loadImg(u), scaleMode: 'linear', alphaMode: 'no-premultiply-alpha' });
const S = {};
for (const k of ['beauty', 'albedo', 'normal', 'depth', 'id', 'ao']) S[k] = await src(`${dir}/${pose}_${k}.png`);
for (const k of ['beauty', 'albedo', 'normal', 'depth']) S['bg_' + k] = await src(`${bgdir}/bg_${k}.png`);

const frag = `
in vec2 vTextureCoord; out vec4 finalColor;
uniform sampler2D uTexture, uBeauty, uAlbedo, uNormal, uDepth, uId, uAO, uBgB, uBgA, uBgN, uBgD;
uniform vec2 uRes; uniform vec4 uHead; uniform vec4 uFeet; uniform float uSeed; uniform float uGrain; uniform float uDbg; uniform highp vec4 uInputSize; uniform highp vec4 uOutputFrame;

float hash(vec2 p){ p = fract(p*vec2(123.34,456.21)); p += dot(p,p+45.32); return fract(p.x*p.y); }
float vnoise(vec2 p){ vec2 i=floor(p), f=fract(p); f=f*f*(3.-2.*f);
  return mix(mix(hash(i),hash(i+vec2(1,0)),f.x), mix(hash(i+vec2(0,1)),hash(i+vec2(1,1)),f.x), f.y); }
float fbm(vec2 p){ float s=0., a=.5; for(int i=0;i<5;i++){ s+=a*vnoise(p); p=p*2.03+7.1; a*=.5; } return s; }
float lum(vec3 c){ return dot(c, vec3(.2126,.7152,.0722)); }
vec3 sat(vec3 c, float s){ return mix(vec3(lum(c)), c, s); }
float soft(float x, float e, float w){ return smoothstep(e-w, e+w, x); }

// cuantización "aerógrafo": escalones de luz con borde suavizado + salpicado de spray en las transiciones
float paintBands(float L, vec2 px, float spray){
  float n = fbm(px/9.0)-0.5;
  float x = L + n*0.10;
  float e[4]; e[0]=0.34; e[1]=0.72; e[2]=1.08; e[3]=1.45;
  float lv[5]; lv[0]=0.30; lv[1]=0.55; lv[2]=0.82; lv[3]=1.08; lv[4]=1.38;
  float r = lv[0];
  for(int i=0;i<4;i++){
    float t = soft(x, e[i], 0.075);
    float sp = step(hash(px*0.5+float(i)*17.3+uSeed), t);   // salpicado
    t = mix(t, sp, spray*(1.-abs(2.*t-1.))*1.6);
    r = mix(r, lv[i+1], clamp(t,0.,1.));
  }
  return r;
}

vec3 decN(vec3 c){ return normalize(c*2.-1.); }
float decDepthBg(vec4 d){ float v = d.r + d.g/255.; return 3.0*exp(v*log(2000.0)); }

// ---------------------------------------------------------------- fondo pintado
vec3 paintBG(vec2 uv, vec2 px){
  vec2 wob = (vec2(fbm(px/23.), fbm(px/23.+9.))-.5)*1.4/uRes;
  vec2 u = uv + wob;
  vec3 A = texture(uBgA, u).rgb, B = texture(uBgB, u).rgb;
  vec3 N = decN(texture(uBgN, u).rgb);
  float z = decDepthBg(texture(uBgD, u));
  float irr = clamp(lum(B)/max(lum(A),0.06), 0., 2.6);
  // el cielo y emisivos usan el color directo
  bool isSky = z > 3000.;
  float L = paintBands(irr, px, 0.35);
  float L2 = mix(irr, L, 0.62);
  vec3 col = A * mix(vec3(.62,.64,.84), vec3(1.12,1.0,.88), smoothstep(.25,1.2,L2)) * (0.5+0.62*L2);
  if(isSky) col = B;
  // perspectiva atmosférica: lejos = más claro, más rosado y desaturado (como el arte oficial)
  float haze = 1.-exp(-z/1100.);
  vec3 hz = vec3(.93,.70,.64);
  col = mix(col, hz, haze*0.62);
  col = sat(col, mix(0.95, 0.55, haze));
  // pincelada/textura: luminancia a gran escala
  col *= 0.94+0.12*fbm(px/5.0);
  // contornos suaves por discontinuidad de profundidad
  float dpx = 1.5/uRes.x*2.0;
  float d0 = log(z);
  float e = 0.;
  e += abs(log(decDepthBg(texture(uBgD, u+vec2(dpx,0))))-d0);
  e += abs(log(decDepthBg(texture(uBgD, u+vec2(0,dpx))))-d0);
  e += abs(log(decDepthBg(texture(uBgD, u-vec2(dpx,0))))-d0);
  e += abs(log(decDepthBg(texture(uBgD, u-vec2(0,dpx))))-d0);
  col *= 1. - clamp(e*1.2,0.,.5)*(1.-haze*.6);
  return col;
}

// ---------------------------------------------------------------- personaje pintado
vec4 paintChar(vec2 uv, vec2 px){
  vec4 Bt = texture(uBeauty, uv);
  float a = Bt.a;
  if(a < 0.002) return vec4(0.);
  vec3 A = texture(uAlbedo, uv).rgb, B = Bt.rgb;
  vec3 N = decN(texture(uNormal, uv).rgb);
  float ao = texture(uAO, uv).r;
  float id = floor(texture(uId, uv).r*255.+0.5);
  float px1 = 1.0/uRes.x;
  float irr = clamp(lum(B)/max(lum(A),0.05), 0., 3.0);

  bool skin = (id==2.|| id==3.), cloth = (id==13.||id==14.), leather=(id==16.||id==15.||id==17.), metal=(id==5.||id==8.), isface=(id==3.);
  // --- detalle de superficie en espacio de pantalla (pintura de textura fina)
  float pores = vnoise(px/1.4)*0.6 + vnoise(px/3.1)*0.4;
  vec3 Ad = A;
  if(skin){
    // variación de tono: rubor en mejillas/nariz/hombros, cálido; venas/pecas sutiles
    float t = fbm(px/38.);
    Ad = mix(Ad, Ad*vec3(1.10,0.88,0.80), smoothstep(.45,.8,t)*0.5);
    Ad *= 0.93 + 0.13*pores;
    float hair = smoothstep(.62,.9, vnoise(px/1.9+3.)) * smoothstep(.1,.5,irr);
    Ad *= 1. - hair*0.07*step(0.3, N.z);
    // barba corta en la cara
    if(isface){
      vec2 hp = (px - uHead.xy)/uHead.z;
      float jaw = smoothstep(0.05,0.6, hp.y) * smoothstep(1.35,0.75,length(hp*vec2(.95,.8)));
      float up = smoothstep(.15,.55, hp.y)*smoothstep(.75,.35,abs(hp.x))*(1.-smoothstep(.55,.7,hp.y));
      float stub = smoothstep(.45,.75, vnoise(px/1.1)) * clamp(jaw+up*0.8,0.,1.) * smoothstep(-0.1,0.4,N.z+0.5);
      Ad = mix(Ad, vec3(.13,.09,.07), stub*0.6);
    }
  } else if(cloth){
    float weave = sin(px.x*1.9+px.y*0.3)*sin(px.y*1.9-px.x*0.3);
    if(id==14.){ weave = sin((px.x+px.y)*1.4)*0.6; Ad = mix(Ad*0.82, Ad*1.18, fbm(px/14.)); Ad *= mix(0.9,1.0,fbm(px/60.)); }
    Ad *= 0.955 + 0.045*weave + 0.05*(fbm(px/2.5)-.5);
  } else if(leather){
    Ad *= 0.82+0.3*fbm(px/2.2);
  }
  // --- luz pintada
  float spray = skin ? 0.5 : 0.35;
  float Lb = paintBands(irr, px, spray);
  float L = mix(irr, Lb, skin ? 0.5 : 0.62);
  L *= mix(0.55, 1.0, pow(ao, 0.8));
  vec3 shadowTint = skin ? vec3(.62,.46,.58) : vec3(.58,.62,.86);
  vec3 lightTint = vec3(1.16,1.02,.86);
  float k = smoothstep(.28,1.05,L);
  vec3 tint = mix(shadowTint, mix(vec3(1.0,.96,.92), lightTint, smoothstep(.95,1.5,L)), k);
  vec3 col = Ad * tint * (0.40+0.74*smoothstep(0.0,1.5,L)) * 1.12;
  // subsuperficial: bordes de sombra de piel se calientan
  if(skin){ float tr = smoothstep(.3,.7,L)*(1.-smoothstep(.7,1.0,L)); col += Ad*vec3(.35,.06,.0)*tr*0.35; }
  // reflejo / sudor: brillos duros
  float spec = max(irr - 1.55, 0.);
  col += (skin? vec3(1.,.9,.78)*0.45 : vec3(1.))*smoothstep(0.0,0.5,spec)*(metal?0.7:(leather?0.2:0.55));
  if(metal) col = mix(col, A*(0.5+lum(B)*1.1), 0.5);
  // luz de recorte (rim) cálida desde atrás-derecha + relleno frío desde la izquierda
  float rim = pow(1.-clamp(N.z,0.,1.), 2.4);
  col += vec3(1.0,.72,.45) * rim * smoothstep(-.1,.7,N.x+.2) * 0.55 * (0.3+0.7*smoothstep(.2,1.,irr));
  col += vec3(.35,.5,.9) * rim * smoothstep(.0,-.8,N.x) * 0.16;
  // contornos pintados (id + silueta), de color oscuro cálido, no negro
  float eid = 0., ea = 0.;
  vec2 o = vec2(px1*1.3, px1*1.3*uRes.x/uRes.y);
  float c0 = texture(uId, uv).r;
  eid += abs(texture(uId, uv+vec2(o.x,0)).r - c0) + abs(texture(uId, uv-vec2(o.x,0)).r - c0);
  eid += abs(texture(uId, uv+vec2(0,o.y)).r - c0) + abs(texture(uId, uv-vec2(0,o.y)).r - c0);
  float nd = 0.;
  nd += length(decN(texture(uNormal, uv+vec2(o.x,0)).rgb) - N) + length(decN(texture(uNormal, uv-vec2(o.x,0)).rgb) - N);
  nd += length(decN(texture(uNormal, uv+vec2(0,o.y)).rgb) - N) + length(decN(texture(uNormal, uv-vec2(0,o.y)).rgb) - N);
  float line = clamp(eid*40., 0., 1.)*0.85 + clamp((nd-0.9)*0.7, 0., 1.)*0.35;
  col = mix(col, Ad*vec3(.16,.11,.12), clamp(line,0.,1.)*0.75);
  // borde exterior
  float aa = 0.;
  aa += texture(uBeauty, uv+vec2(o.x*1.6,0)).a + texture(uBeauty, uv-vec2(o.x*1.6,0)).a + texture(uBeauty, uv+vec2(0,o.y*1.6)).a + texture(uBeauty, uv-vec2(0,o.y*1.6)).a;
  col = mix(col, col*vec3(.45,.38,.42), (1.-aa/4.)*0.8);
  return vec4(col, a);
}

void main(){
  vec2 uv = vTextureCoord * uInputSize.xy / uOutputFrame.zw;
  if(uDbg>0.5){ if(uDbg<1.5) finalColor=vec4(texture(uBeauty,uv).rgb,1.); else if(uDbg<2.5) finalColor=vec4(texture(uBgB,uv).rgb,1.); else finalColor=vec4(uv,0.,1.); return; }
  vec2 px = uv*uRes;
  vec3 bg = paintBG(uv, px);
  // sombra de contacto + sombra proyectada larga (sol bajo a la izquierda)
  vec2 f = uFeet.xy;
  vec2 d = px - f;
  float sh = 0.;
  float cs = exp(-pow(length(d*vec2(1./(uFeet.z*0.55), 1./(uFeet.z*0.12))),2.));
  vec2 dl = d - vec2(uFeet.z*1.1, -uFeet.z*0.02);
  float ls = exp(-pow(length(dl*vec2(1./(uFeet.z*1.5), 1./(uFeet.z*0.10))),2.));
  float deckMask = smoothstep(uFeet.w-8., uFeet.w+8., px.y);   // solo sobre la cubierta
  bg *= 1. - clamp(cs*0.55 + ls*0.38,0.,.7)*deckMask*vec3(.8,.9,1.).x;
  bg = mix(bg, bg*vec3(.62,.66,.86), clamp(cs*0.5+ls*0.4,0.,.6)*deckMask);
  vec4 c = paintChar(uv, px);
  vec3 col = mix(bg, c.rgb, c.a);
  // gradación global estilo Rockstar: contraste suave, sombras violáceas, luces cálidas, viñeta
  col = sat(col, 0.92);
  float l = lum(col);
  col = mix(col, col*vec3(.92,.94,1.08), smoothstep(.5,.0,l)*0.5);
  col = mix(col, col*vec3(1.06,1.0,.92), smoothstep(.5,1.,l)*0.5);
  col = (col-0.5)*1.07+0.5+0.01;
  vec2 vc = uv-.5; col *= 1. - dot(vc,vc)*0.55;
  // grano de pintura / lienzo
  float g = (hash(px+uSeed)-.5)*0.035*uGrain + (fbm(px/1.7)-.5)*0.03*uGrain;
  col += g;
  finalColor = vec4(clamp(col,0.,1.), 1.);
}`;

const app = new PIXI.Application();
await app.init({ width: W, height: H, preference: 'webgl', antialias: false, preserveDrawingBuffer: true, backgroundAlpha: 1, resolution: 1, autoDensity: false });
const base = new PIXI.Sprite(new PIXI.Texture({ source: S.albedo }));
base.width = W; base.height = H;
const filter = new PIXI.Filter({
  glProgram: PIXI.GlProgram.from({ vertex: PIXI.defaultFilterVert ?? PIXI.defaultFilterVertex, fragment: frag.trim() }),
  resources: {
    uBeauty: S.beauty, uAlbedo: S.albedo, uNormal: S.normal, uDepth: S.depth, uId: S.id, uAO: S.ao,
    uBgB: S.bg_beauty, uBgA: S.bg_albedo, uBgN: S.bg_normal, uBgD: S.bg_depth,
    P: { uRes: { value: [W, H], type: 'vec2<f32>' }, uHead: { value: meta.head, type: 'vec4<f32>' }, uFeet: { value: meta.feet, type: 'vec4<f32>' },
         uSeed: { value: 3.7, type: 'f32' }, uGrain: { value: 1.0, type: 'f32' }, uDbg: { value: +(q.get('dbg')||0), type: 'f32' } },
  },
});
base.filters = [filter];
app.stage.addChild(base);
app.renderer.render(app.stage);
const canvas = app.renderer.extract.canvas(app.stage);
window.__png2 = canvas.toDataURL('image/png');
app.renderer.render(app.stage);
window.__png = app.canvas.toDataURL('image/png');
window.__done = true;
