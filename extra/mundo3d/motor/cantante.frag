#version 300 es
precision highp float;
out vec4 fragColor;
uniform vec2 R; uniform float T;
uniform vec3 camPos, camTgt; uniform float fov, uFish;
// expresion / pose
uniform float uJaw, uWide, uPucker, uSmile, uBrow, uQuiff, uYaw, uPitch, uLean, uArmR, uArmL, uBob, uBg;
#define PI 3.14159265
float h31(vec3 p){p=fract(p*.3183099+.1);p*=17.;return fract(p.x*p.y*p.z*(p.x+p.y+p.z));}
float vn(vec3 x){vec3 i=floor(x),f=fract(x);f=f*f*(3.-2.*f);
 return mix(mix(mix(h31(i),h31(i+vec3(1,0,0)),f.x),mix(h31(i+vec3(0,1,0)),h31(i+vec3(1,1,0)),f.x),f.y),
            mix(mix(h31(i+vec3(0,0,1)),h31(i+vec3(1,0,1)),f.x),mix(h31(i+vec3(0,1,1)),h31(i+vec3(1,1,1)),f.x),f.y),f.z);}
float fbm(vec3 p){return .55*vn(p)+.3*vn(p*2.1)+.15*vn(p*4.3);}
float smin(float a,float b,float k){float h=max(k-abs(a-b),0.)/k;return min(a,b)-h*h*k*.25;}
float smax(float a,float b,float k){return -smin(-a,-b,k);}
float dot2(vec3 v){return dot(v,v);}
float sdEll(vec3 p,vec3 r){float k0=length(p/r);float k1=length(p/(r*r));return k0*(k0-1.)/k1;}
float sdCap(vec3 p,vec3 a,vec3 b,float r){vec3 pa=p-a,ba=b-a;float h=clamp(dot(pa,ba)/dot(ba,ba),0.,1.);return length(pa-ba*h)-r;}
float sdRBox(vec3 p,vec3 b,float r){vec3 q=abs(p)-b;return length(max(q,0.))+min(max(q.x,max(q.y,q.z)),0.)-r;}
float sdRC(vec3 p,vec3 a,vec3 b,float r1,float r2){
 vec3 ba=b-a;float l2=dot(ba,ba);float rr=r1-r2;float a2=l2-rr*rr;float il2=1./l2;
 vec3 pa=p-a;float y=dot(pa,ba);float z=y-l2;float x2=dot2(pa*l2-ba*y);float y2=y*y*l2;float z2=z*z*l2;
 float k=sign(rr)*rr*rr*x2;
 if(sign(z)*a2*z2>k) return sqrt(x2+z2)*il2-r2;
 if(sign(y)*a2*y2<k) return sqrt(x2+y2)*il2-r1;
 return (sqrt(x2*a2*il2)+y*rr)*il2-r1;}
mat2 rot(float a){float c=cos(a),s=sin(a);return mat2(c,-s,s,c);}
vec2 U(vec2 a,vec2 b){return a.x<b.x?a:b;}
// ids: 1 piel 2 pelo 3 chaqueta 4 remera 5 oro 6 guante 7 cinturon 8 pantalon 9 bota 10 lente 11 boca 12 cromo 13 hebilla 14 labio 15 marco gafas
const vec3 HC=vec3(0.,1.68,0.);
vec3 headLocal(vec3 p){vec3 q=p-HC; q.xz=rot(uYaw)*q.xz; q.yz=rot(uPitch)*q.yz; return q;}
vec2 head(vec3 q){
 q.y=mix(q.y,q.y*1.3,smoothstep(.03,-.03,q.y));
 float cran=sdEll(q-vec3(0,.022,-.006),vec3(.088,.108,.1));
 float face=sdEll(q-vec3(0,-.035,.03),vec3(.076,.1,.082));
 float d=smin(cran,face,.045);
 // mandibula con rotacion
 vec3 qj=q-vec3(0,-.03,-.04); qj.yz=rot(-uJaw*.42)*qj.yz; qj+=vec3(0,-.03,-.04);
 float jaw=sdEll(qj-vec3(0,-.085,.04),vec3(.068,.052,.07));
 float jbox=sdRBox(qj-vec3(0,-.08,.034),vec3(.054,.034,.062),.02);
 float chin=sdEll(qj-vec3(0,-.118,.094),vec3(.036,.03,.034));
 float J=smin(smin(jaw,jbox,.03),chin,.025);
 d=smin(d,J,.035);
 // pomulos marcados y mejillas hundidas
 float ck=sdEll(vec3(abs(q.x),q.y,q.z)-vec3(.054,-.012+.005*uSmile,.07),vec3(.03,.022,.026));
 d=smin(d,ck,.03);
 d=smax(d,-sdEll(vec3(abs(q.x),q.y,q.z)-vec3(.07,-.056,.044),vec3(.03,.032,.04)),.035);
 // frente/arco superciliar
 float bro=sdCap(vec3(abs(q.x),q.y,q.z),vec3(0,.043+.01*uBrow,.09),vec3(.058,.04+.012*uBrow,.082),.014);
 d=smin(d,bro,.025);
 // nariz
 float nz=sdRC(q,vec3(0,.026,.092),vec3(0,-.044,.118),.0095,.0165);
 nz=smin(nz,length(q-vec3(0,-.052,.13))-.0165,.014);
 nz=smin(nz,sdEll(vec3(abs(q.x),q.y,q.z)-vec3(.017,-.046,.106),vec3(.012,.012,.012)),.012);
 d=smin(d,nz,.018);
 d=smax(d,-sdEll(vec3(abs(q.x),q.y,q.z)-vec3(.009,-.054,.113),vec3(.005,.005,.012)),.006);
 // orejas
 float ear=sdEll(vec3(abs(q.x),q.y,q.z)-vec3(.092,-.006,-.012),vec3(.011,.033,.022));
 d=smin(d,ear,.012);
 // cuello + trapecio
 float neck=sdRC(q,vec3(0,-.1,-.03),vec3(0,-.23,-.045),.044,.058);
 d=smin(d,neck,.03);
 // boca: dominio deformado por sonrisa
 vec3 qm=q; qm.y+=uSmile*3.4*qm.x*qm.x*1.4-uPucker*0.0; qm.x/=(1.-.22*uPucker+.2*uWide);
 vec3 qlj=qm-vec3(0,-.03,-.04); qlj.yz=rot(-uJaw*.42)*qlj.yz; qlj+=vec3(0,-.03,-.04);
 float lipU=sdEll(qm-vec3(0,-.074,.1),vec3(.027,.0095,.0145));
 float lipL=sdEll(qlj-vec3(0,-.09,.099),vec3(.025,.0105,.0145));
 float cav=sdEll(qm-vec3(0,-.082-.012*uJaw,.1),vec3(.026,.004+.02*uJaw,.05));
 float dl=smin(lipU,lipL,.006);
 d=smin(d,dl,.008);
 d=smax(d,-cav,.007);
 float id=1.; if(dl<.004) id=14.; if(cav<.006&&uJaw>.05) id=11.;
 vec2 r=vec2(d,id);
 // dientes superiores
 float teeth=sdEll(qm-vec3(0,-.079,.088),vec3(.019,.0055,.007));
 if(uJaw>.12) r=U(r,vec2(teeth+.002,16.));
 // pelo: casquete + pompadour + cabello largo hacia atras
 float hl=q.y-.056-.8*(q.z-.095);
 float cap=sdEll(q-vec3(0,.05,-.012),vec3(.094,.108,.108));
 float hair=smax(cap,-hl,.012);
 vec3 qq=q-vec3(0,.115+.02*uQuiff,.085); qq.yz=rot(.75)*qq.yz;
 float quiff=sdEll(qq,vec3(.066,.045+.02*uQuiff,.125+.03*uQuiff));
 hair=smin(hair,quiff,.04);
 hair=smin(hair,sdEll(q-vec3(0,.075,-.1),vec3(.084,.1,.075)),.04);
 hair=smin(hair,sdRC(q,vec3(0,.05,-.095),vec3(0,-.19,-.105),.088,.058),.04);
 hair=smin(hair,sdEll(vec3(abs(q.x),q.y,q.z)-vec3(.088,.015,-.015),vec3(.022,.07,.085)),.03);
 hair=smax(hair,-sdEll(vec3(abs(q.x),q.y,q.z)-vec3(.1,-.02,.012),vec3(.02,.03,.025)),.012);   // deja ver la oreja
 float gr=sin(q.x*170.+sin(q.y*30.+q.z*22.)*1.2+q.z*30.)*.0012+sin(q.y*110.+q.x*30.)*.0006;
 hair+=gr;
 r=U(r,vec2(hair,2.));
 // lentes de sol (wayfarer)
 vec3 ql=vec3(abs(q.x),q.y,q.z); ql.xz=rot(.14)*(ql.xz-vec2(.04,.1))+vec2(.04,.1);
 float lens=sdRBox(ql-vec3(.04,.018,.103),vec3(.027,.016,.003),.009);
 float frame=max(sdRBox(ql-vec3(.04,.018,.103),vec3(.03,.019,.006),.011),-(lens+.003)+0.0);
 frame=min(frame,sdRBox(ql-vec3(.04,.032,.106),vec3(.03,.004,.005),.004));
 float bridge=sdCap(q,vec3(-.012,.032,.106),vec3(.012,.032,.106),.0045);
 float temple=sdCap(vec3(abs(q.x),q.y,q.z),vec3(.073,.03,.09),vec3(.096,.028,.0),.0033);
 r=U(r,vec2(lens,10.)); r=U(r,vec2(min(min(frame,bridge),temple),15.));
 return r;}
// brazos (poses por interpolacion)
void armPts(float s,float m,out vec3 sh,out vec3 el,out vec3 wr){
 sh=vec3(s*.235,1.5,0.);
 vec3 elR=vec3(s*.30,1.28,.07), wrR=vec3(s*.28,1.06,.14);
 vec3 elM=vec3(s*.255,1.4,.22), wrM=vec3(s*.07,1.60,.24);
 vec3 elG=vec3(s*.36,1.5,.16), wrG=vec3(s*.31,1.75,.2);
 float aR=(s>0.)?uArmR:uArmL;
 vec3 e1=(s>0.)?elM:elG, w1=(s>0.)?wrM:wrG;
 el=mix(elR,e1,aR); wr=mix(wrR,w1,aR);}
vec2 body(vec3 p){
 vec3 b=p; b.y-=uBob; float a=uLean*smoothstep(.9,1.4,p.y); b.xy=rot(a)*b.xy; vec3 bh=p; // cuerpo inclinado
 float chest=sdEll(b-vec3(0,1.4,0),vec3(.215,.245,.13));
 float lat=sdEll(b-vec3(0,1.46,-.01),vec3(.24,.14,.12));
 float abd=sdEll(b-vec3(0,1.17,0),vec3(.175,.2,.108));
 float pel=sdEll(b-vec3(0,.99,0),vec3(.178,.13,.115));
 float torso=smin(smin(smin(chest,lat,.07),abd,.09),pel,.08);
 float trap=sdEll(b-vec3(0,1.565,-.02),vec3(.15,.06,.09));
 torso=smin(torso,trap,.05);
 vec2 r=vec2(1e3,1.);
 // remera (debajo)
 float tee=torso+.0;
 vec2 teeV=vec2(smax(tee,b.y-1.04,.01),4.);
 // chaqueta
 float jk=torso-.014; jk=smax(jk,1.07-b.y,.015);
 float wedge=max(abs(b.x)-(.012+(1.555-b.y)*.17),max(.02-b.z,b.y-1.57));
 wedge=max(wedge,1.05-b.y);
 jk=smax(jk,-wedge,.012);
 float lapel=min(sdRC(vec3(abs(b.x),b.y,b.z),vec3(.082,1.56,.075),vec3(.03,1.29,.14),.02,.016),sdEll(vec3(abs(b.x),b.y,b.z)-vec3(.085,1.575,.03),vec3(.06,.03,.06)));
 float collar=max(sdEll(b-vec3(0,1.585,-.015),vec3(.105,.045,.095)),-sdEll(b-vec3(0,1.6,-.005),vec3(.075,.06,.07)));
 jk=smin(jk,min(lapel,collar),.01);
 // brazos
 vec3 sh,el,wr; float jkArm=1e3, skin=1e3, glove=1e3;
 for(int i=0;i<2;i++){float s=(i==0)?1.:-1.; armPts(s,0.,sh,el,wr);
  float up=sdRC(p,sh,el,.064,.054), fo=sdRC(p,el,wr,.055,.04);
  jkArm=min(jkArm,smin(up,fo,.02)-.0);
  vec3 hd=wr+normalize(wr-el)*.045;
  glove=min(glove,min(sdEll(p-hd,vec3(.034,.045,.025)),sdCap(p,hd,hd+normalize(wr-el)*.05+vec3(0,0,.01),.022)));
  jkArm=max(jkArm,-sdCap(p,wr,wr-(wr-el)*.2,.001)); }
 jk=smin(jk,jkArm,.03);
 r=U(r,vec2(jk,3.)); r=U(r,teeV);
 r=U(r,vec2(glove,6.));
 // cuello expuesto por el cuello abierto (piel del pecho)
 float chestSkin=max(torso+.004,wedge+.0); chestSkin=max(chestSkin,b.y-1.57);
 r=U(r,vec2(max(chestSkin,-jk+.0),1.));
 // cinturon
 float belt=max(sdEll(b-vec3(0,1.04,0),vec3(.184,.03,.122)),-sdEll(b-vec3(0,1.04,0),vec3(.172,.04,.11)));
 r=U(r,vec2(belt,7.));
 r=U(r,vec2(sdRBox(b-vec3(0,1.04,.118),vec3(.028,.022,.006),.006),13.));
 // cadena de oro + medallon
 float ch=1e3;
 for(int k=0;k<10;k++){float t=float(k)/9.; float sx=(t*t*.3)*.06;
  vec3 c1=vec3(-0.058+t*.058, 1.545-(.2*sin(t*1.57)), .052+t*.088+ .02*sin(t*3.14));
  vec3 c2=vec3(.058-t*.058, c1.y, c1.z);
  ch=min(ch,min(sdEll(b-c1,vec3(.0085,.0085,.004)),sdEll(b-c2,vec3(.0085,.0085,.004))));
  ch=min(ch,min(sdCap(b,c1,c1+vec3(.004,-.011,.003),.0025),sdCap(b,c2,c2+vec3(-.004,-.011,.003),.0025))); }
 vec3 mc=vec3(0,1.325,.152);
 float med=sdRC(b-mc,vec3(0,0,-.006),vec3(0,0,.006),.041,.036);
 med=min(med,max(length((b-mc).xy)-.046,abs(b.z-mc.z-.002)-.0095)); 
 r=U(r,vec2(min(ch,med),5.));
 // piernas y botas
 float legs=1e3, boots=1e3;
 for(int i=0;i<2;i++){float s=(i==0)?1.:-1.;
  vec3 hip=vec3(s*.1,.95,0.), kn=vec3(s*.11,.52,.03), an=vec3(s*.115,.13,-.01);
  legs=min(legs,smin(sdRC(p,hip,kn,.105,.074),sdRC(p,kn,an,.074,.058),.03));
  vec3 fp=p-vec3(s*.12,.05,.07);
  boots=min(boots,min(sdRC(p,an,an+vec3(0,.2,0),.07,.074)*0.+sdRC(p,vec3(s*.115,.14,-.01),vec3(s*.115,.3,-.012),.068,.074),smin(sdRBox(fp,vec3(.04,.034,.1),.028),sdEll(p-vec3(s*.115,.1,-.01),vec3(.07,.08,.08)),.03)));
  boots=min(boots,sdRBox(p-vec3(s*.12,.018,-.035),vec3(.045,.016,.04),.012)); }
 float pant=smin(legs,smax(sdEll(b-vec3(0,.99,0),vec3(.18,.135,.117)),b.y-1.03,.01),.05);
 r=U(r,vec2(pant,8.)); r=U(r,vec2(boots,9.));
 // microfono
 vec3 hd=vec3(.07,1.60,.24); 
 float mic=min(length(p-(hd+vec3(0,.075,.01)))-.034,sdCap(p,hd+vec3(0,.05,.01),hd+vec3(.0,-.09,-.01),.016));
 float micOn=smoothstep(.3,.6,uArmR); r=U(r,vec2(mic+(1.-micOn)*1.,12.));
 return r;}
vec2 map(vec3 p){
 vec2 r=body(p);
 vec3 q=headLocal(p);
 vec3 hc=p-HC;
 if(length(hc)<.4){ r=U(r,head(q)); }
 else r=U(r,vec2(length(hc)-.35,1.));
 return r;}
vec3 calcN(vec3 p){vec2 e=vec2(.0016,-.0016);
 return normalize(e.xyy*map(p+e.xyy).x+e.yyx*map(p+e.yyx).x+e.yxy*map(p+e.yxy).x+e.xxx*map(p+e.xxx).x);}
float softShadow(vec3 ro,vec3 rd){float res=1.,t=.01;for(int i=0;i<28;i++){float h=map(ro+rd*t).x;res=min(res,10.*h/t);t+=clamp(h,.012,.12);if(res<.02||t>1.2)break;}return clamp(res,0.,1.);}
float calcAO(vec3 p,vec3 n){float o=0.,s=1.;for(int i=0;i<4;i++){float h=.012+.045*float(i);o+=(h-map(p+n*h).x)*s;s*=.8;}return clamp(1.-3.*o,0.,1.);}
vec3 albedo(vec3 p,vec3 n,float id,vec3 q,out float spec,out float shin){
 spec=0.;shin=20.; vec3 c=vec3(.8);
 if(id<1.5){ // piel: calida, con variacion
  c=vec3(.9,.6,.45); float f=fbm(p*40.); c*=.95+.1*f;
  c=mix(c,vec3(.8,.42,.36),smoothstep(.0,.05,.06-abs(q.x))*smoothstep(-.03,-.06,q.y)*.0); spec=.15; shin=30.;
  float cheek=smoothstep(.05,.0,length(vec2(abs(q.x)-.055,q.y+.02)))*.18; c=mix(c,vec3(.85,.38,.32),cheek);
  float stub=smoothstep(.0,.02,-q.y-.05)*smoothstep(.07,.04,abs(q.x))*step(q.z,.12); c*=1.-.22*stub*smoothstep(.2,.7,vn(p*210.)); }
 else if(id<2.5){ c=mix(vec3(.035,.025,.022),vec3(.13,.085,.06),smoothstep(.45,.8,vn(p*140.+vec3(0,p.x*30.,0)))); spec=.7; shin=80.; }
 else if(id<3.5){ c=vec3(.13,.14,.18)*(0.85+.3*fbm(p*26.)); spec=.6; shin=28.; }
 else if(id<4.5){ c=vec3(.93,.93,.9)*(.9+.1*fbm(p*60.)); }
 else if(id<5.5){ c=vec3(1.,.74,.2); spec=1.; shin=90.; }
 else if(id<6.5){ c=vec3(.05,.05,.06); spec=.45; shin=40.; }
 else if(id<7.5){ c=vec3(.27,.14,.07); spec=.5; shin=30.; }
 else if(id<8.5){ c=vec3(.1,.11,.14)*(.8+.4*fbm(p*50.)); }
 else if(id<9.5){ c=vec3(.05,.045,.045); spec=.7; shin=45.; }
 else if(id<10.5){ c=vec3(.09,.05,.025); spec=1.2; shin=140.; }
 else if(id<11.5){ c=vec3(.28,.04,.05); }
 else if(id<12.5){ c=vec3(.7,.72,.75); spec=1.; shin=90.; }
 else if(id<13.5){ c=vec3(.85,.78,.5); spec=1.; shin=90.; }
 else if(id<14.5){ c=vec3(.66,.28,.27); spec=.35; shin=30.; }
 else if(id<15.5){ c=vec3(.025,.025,.03); spec=.8; shin=70.; }
 else { c=vec3(.95,.93,.86); }
 return c;}
vec3 bgCol(vec2 uv,vec3 rd){ float y=uv.y*.5+.5; vec3 c=mix(vec3(.9,.92,.9),vec3(.76,.8,.8),smoothstep(.2,1.,y));
 // siluetas de ciudad lavadas
 float sk=0.; for(int i=0;i<6;i++){float fi=float(i); float x=uv.x*1.4+fi*.37; float h=-.1+.25*fract(sin(fi*91.7)*437.1); sk+=step(abs(fract(x)-.5),.17)*step(uv.y,h)*0.;}
 return mix(c,vec3(.72,.76,.76),sk)*uBg+vec3(.88,.9,.9)*(1.-uBg);}
void main(){
 vec2 uv=(gl_FragCoord.xy*2.-R)/R.y;
 vec3 ww=normalize(camTgt-camPos), uu=normalize(cross(ww,vec3(0,1,0))), vv=cross(uu,ww);
 vec3 rd;
 float tf=tan(fov*.5);
 if(uFish>.001){float r=length(uv); float ang=r*tf*(1.+uFish*1.6); vec2 d=r>1e-4?uv/r:vec2(0); vec3 fd=normalize(uu*d.x*sin(ang)+vv*d.y*sin(ang)+ww*cos(ang)); vec3 pd=normalize(uu*uv.x*tf+vv*uv.y*tf+ww); rd=normalize(mix(pd,fd,clamp(uFish,0.,1.)));}
 else rd=normalize(uu*uv.x*tf+vv*uv.y*tf+ww);
 float t=.2,id=0.; vec2 h; bool hit=false;
 for(int i=0;i<150;i++){vec3 p=camPos+rd*t; h=map(p); if(h.x<.0006*t){hit=true;break;} t+=h.x*.85; if(t>6.)break;}
 vec3 col;
 vec3 key=normalize(vec3(-.8,.56,.34)); vec3 fillD=normalize(vec3(.7,.15,.4));
 if(hit){
  vec3 p=camPos+rd*t; vec3 n=calcN(p); id=h.y; vec3 q=headLocal(p);
  float sp,sh; vec3 alb=albedo(p,n,id,q,sp,sh);
  float brush=(fbm(p*22.+vec3(0,T*0.,0))-.5)*.16 + (vn(p*95.)-.5)*.05;
  float ndl=dot(n,key); float tt=ndl*.5+.5+brush;
  float ss=softShadow(p+n*.004,key); float ao=calcAO(p,n);
  float lit=smoothstep(.5,.62,tt)*mix(.25,1.,ss);       // plano de luz
  float mid=smoothstep(.27,.46,tt);                       // media sombra
  vec3 cShadow=alb*vec3(.3,.36,.55);                      // sombra fria
  vec3 cMid=alb*vec3(.68,.72,.82);
  vec3 cLit=alb*vec3(1.1,1.03,.92);
  col=mix(cShadow,cMid,mid); col=mix(col,cLit,lit);
  col*=mix(.55,1.,ao);
  // luz de relleno fria desde la derecha y rebote calido desde abajo
  col+=alb*vec3(.05,.09,.14)*max(dot(n,fillD),0.)*.8; col+=alb*vec3(.07,.045,.02)*max(-n.y,0.);
  // brillos duros tipo pintura
  vec3 hv=normalize(key-rd); float s=pow(max(dot(n,hv),0.),sh)*sp*mix(.2,1.,ss); col+=vec3(1.,.95,.85)*smoothstep(.25,.5,s)*min(sp,1.)*.9;
  if(id>9.5&&id<10.5){vec3 rf=reflect(rd,n); col+=mix(vec3(.45,.55,.6),vec3(.95,.95,.9),smoothstep(-.2,.6,rf.y))*.7*pow(1.-max(dot(n,-rd),0.),2.)+vec3(.9)*smoothstep(.93,.97,dot(rf,key));}
  if(id>11.5&&id<12.5){vec3 rf=reflect(rd,n); col=mix(col,mix(vec3(.18,.2,.22),vec3(.95),smoothstep(-.1,.5,rf.y)),.7);}
  // medallon: simbolo de rock (cuernos + estrella grabados)
  if(id>4.5&&id<5.5){vec3 b=p; float a=uLean*smoothstep(.9,1.4,p.y); b.xy=rot(a)*b.xy; vec2 m=(b.xy-vec2(0,1.325))/.035;
   if(length(m)<.9&&b.z>.15){float star=1.-smoothstep(.0,.06,abs(length(m)-.62)); float horns=smoothstep(.12,.06,abs(abs(m.x)-.3-.2*m.y*m.y)-.0)*step(-.5,m.y)*step(m.y,.6); col=mix(col,vec3(.42,.27,.05),clamp(star*.8+horns*.8,0.,1.));}}
  // oscurecer bordes de silueta (borde pictorico)
  col*=mix(.82,1.,smoothstep(.0,.35,dot(n,-rd)));
 } else { col=bgCol(uv,rd); }
 // grading tipo GTA IV: desaturar leve, contraste, tinte frio en sombras
 float l=dot(col,vec3(.3,.59,.11)); col=mix(vec3(l),col,hit?1.05:.35); col=pow(clamp(col,0.,1.),vec3(.95));
 col+= (h31(vec3(gl_FragCoord.xy,T))-.5)*.018;
 fragColor=vec4(col,1.);}
