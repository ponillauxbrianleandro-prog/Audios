/* Motor de escenas 2D de Extra.  Determinista: renderAt(t) dibuja el cuadro exacto del segundo t.
 * Se usa tanto en el editor (index.html) como en la grabacion (herramientas/grabar.mjs).
 * No hay 3D: capas con paralaje, camara 2D, filtros de color por rol (fondo/sujeto). */
(function () {
  const W = 1920, H = 1080;
  const E = {
    lineal: t => t, in: t => t * t, out: t => 1 - (1 - t) * (1 - t),
    inout: t => t < .5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2,
    rebote: t => { const n = 7.5625, d = 2.75; if (t < 1 / d) return n * t * t; if (t < 2 / d) return n * (t -= 1.5 / d) * t + .75; if (t < 2.5 / d) return n * (t -= 2.25 / d) * t + .9375; return n * (t -= 2.625 / d) * t + .984375; },
    elastico: t => t === 0 || t === 1 ? t : Math.pow(2, -10 * t) * Math.sin((t * 10 - .75) * (2 * Math.PI) / 3) + 1,
    atras: t => { const c = 1.70158; return 1 + (c + 1) * Math.pow(t - 1, 3) + c * Math.pow(t - 1, 2); }
  };
  const SVGS = {};
  const M = {
    W, H, escena: null, catalogo: null, paletas: null, base: "", items: {}, capas: [], onCambio: null,

    async cargarBase(base) {
      M.base = base || "";
      M.catalogo = await (await fetch(M.base + "catalogo.json")).json();
      M.paletas = await (await fetch(M.base + "paletas.json")).json();
      M.porId = Object.fromEntries(M.catalogo.assets.map(a => [a.id, a]));
    },
    async svg(id) {
      if (SVGS[id]) return SVGS[id];
      const a = M.porId[id];
      if (!a) throw new Error("asset desconocido: " + id);
      return (SVGS[id] = await (await fetch(M.base + a.archivo)).text());
    },

    async cargarEscena(esc) {
      if (typeof esc === "string") esc = await (await fetch(M.base + esc)).json();
      M.escena = esc;
      const st = document.getElementById("stage");
      st.innerHTML = '<div id="mundo"></div><div id="tinte"></div><div id="bruma"></div><div id="vineta"></div><div id="grano"></div><div id="flash"></div><div id="barras"></div>';
      const mundo = document.getElementById("mundo");
      M.items = {}; M.capas = [];
      const tema = M.paletas.temas[esc.tema || "gta4"];
      M.tema = tema;
      mundo.style.background = `linear-gradient(${tema.cielo[0]},${tema.cielo[1]})`;
      const ti = document.getElementById("tinte");
      ti.style.background = tema.tinte; ti.style.opacity = tema.tinte_op * (esc.tinte ?? 1);
      document.getElementById("vineta").style.opacity = esc.vineta ?? .5;
      document.getElementById("grano").style.opacity = esc.grano ?? .08;
      document.getElementById("barras").dataset.on = esc.barras ? "1" : "0";
      let n = 0;
      for (const c of esc.capas) {
        const el = document.createElement("div");
        el.className = "capa"; el.dataset.nombre = c.nombre;
        if (c.mascara) {
          const a = M.porId[c.mascara.asset];
          const sc = c.mascara.esc ?? 1;
          const url = M.base + a.archivo;
          const s = `url(${url}) no-repeat ${c.mascara.x - a.w * sc / 2}px ${c.mascara.y - (a.ancla === "centro" ? a.h * sc / 2 : a.h * sc)}px / ${a.w * sc}px ${a.h * sc}px`;
          el.style.webkitMask = s; el.style.mask = s;
          el.dataset.mascara = "1";
        }
        mundo.appendChild(el);
        const capa = { def: c, el, items: [] };
        M.capas.push(capa);
        for (const it of c.items || []) {
          it.id = it.id || ("i" + (n++));
          await M.agregarItem(capa, it);
        }
      }
      M.renderAt(0);
      if (M.onCambio) M.onCambio();
      return esc;
    },

    async agregarItem(capa, it) {
      const el = document.createElement("div");
      el.className = "item"; el.dataset.id = it.id;
      if (it.texto && !it.asset) {
        el.classList.add("texto");
        el.textContent = it.texto;
        el.style.cssText += `;font:${it.peso || 900} ${it.tam || 64}px ${it.fuente || "Impact,Arial Black,sans-serif"};color:${it.color || "#fff"};white-space:nowrap;letter-spacing:${it.espaciado || 0}px;text-shadow:${it.sombra || "0 4px 0 rgba(0,0,0,.45)"}`;
        it._a = { w: 0, h: 0, ancla: "centro" };
      } else {
        const a = M.porId[it.asset];
        // ids unicos por instancia: evita que gradientes/filtros de distintos SVG se pisen
        let txt = await M.svg(it.asset);
        const uid = "u" + (M._uid = (M._uid || 0) + 1);
        const refs = new Set([...txt.matchAll(/url\(#([\w-]+)\)/g)].map(m => m[1]));
        refs.forEach(r => { txt = txt.split(`id="${r}"`).join(`id="${r}_${uid}"`).split(`url(#${r})`).join(`url(#${r}_${uid})`); });
        el.innerHTML = txt;
        const sv = el.firstElementChild; sv.style.display = "block"; sv.style.overflow = "visible";
        it._a = a;
        if (it.texto_editable) { const t = el.querySelector("#texto"); if (t) t.textContent = it.texto_editable; }
        if (it.silueta) el.querySelectorAll("path,rect,circle,ellipse,line").forEach(n => { n.style.fill = it.silueta; n.style.stroke = "none"; });
      }
      capa.el.appendChild(el); capa.items.push(it);
      M.items[it.id] = { it, el, capa };
      return el;
    },
    quitarItem(id) {
      const r = M.items[id]; if (!r) return;
      r.el.remove(); r.capa.items = r.capa.items.filter(i => i.id !== id); r.capa.def.items = r.capa.items; delete M.items[id];
    },

    anim(t) { // devuelve valores animados por item: {id: {x,y,esc,rot,op,flip, partes}}
      const out = {};
      for (const an of M.escena.anim || []) {
        const dur = an.t1 - an.t0;
        let u;
        if (an.loop) { u = ((t - an.t0) / (an.periodo || dur)); if (u < 0) continue; u = u % 1; if (an.pingpong) u = u < .5 ? u * 2 : 2 - u * 2; }
        else { if (t < an.t0 && !an.antes) continue; u = dur > 0 ? Math.min(1, Math.max(0, (t - an.t0) / dur)) : 1; }
        const f = (E[an.ease] || E.inout)(u);
        const v = an.from + (an.to - an.from) * f;
        const o = out[an.item] = out[an.item] || { partes: {} };
        if (an.parte) { const p = o.partes[an.parte] = o.partes[an.parte] || { pivote: an.pivote || [0, 0] }; p[an.prop] = (p[an.prop] || 0) + v; }
        else if (an.sum) o[an.prop] = (o[an.prop] || 0) + v;
        else o[an.prop] = v;
      }
      return out;
    },

    camara(t) {
      const k = (M.escena.camara || [{ t: 0, x: W / 2, y: H / 2, z: 1 }]);
      let a = k[0], b = k[k.length - 1];
      if (t <= a.t) b = a; else if (t >= b.t) a = b;
      else for (let i = 0; i < k.length - 1; i++) if (t >= k[i].t && t <= k[i + 1].t) { a = k[i]; b = k[i + 1]; break; }
      const u = b.t === a.t ? 1 : (t - a.t) / (b.t - a.t), f = (E[b.ease] || E.inout)(u);
      const c = { x: a.x + (b.x - a.x) * f, y: a.y + (b.y - a.y) * f, z: a.z + (b.z - a.z) * f };
      for (const s of M.escena.temblor || []) if (t >= s.t0 && t <= s.t1) { const m = s.fuerza * (1 - (t - s.t0) / (s.t1 - s.t0)); c.x += Math.sin(t * 91) * m; c.y += Math.cos(t * 77) * m; }
      return c;
    },

    renderAt(t) {
      const esc = M.escena; if (!esc) return;
      const cam = M.camara(t), an = M.anim(t), tema = M.tema;
      for (const capa of M.capas) {
        const p = capa.def.paralaje ?? 1, z = 1 + (cam.z - 1) * (p >= 1 ? 1 : p);
        const dx = -(cam.x - W / 2) * p, dy = -(cam.y - H / 2) * p;
        capa.el.style.transform = `translate(${W / 2}px,${H / 2}px) scale(${z}) translate(${-W / 2 + dx}px,${-H / 2 + dy}px)`;
        const vis = (capa.def.de == null || t >= capa.def.de) && (capa.def.hasta == null || t < capa.def.hasta);
        capa.el.style.opacity = vis ? (capa.def.op ?? 1) : 0;
        capa.el.style.display = vis ? "block" : "none";
        const dif = capa.def.desenfoque ? `blur(${capa.def.desenfoque}px)` : "";
        for (const it of capa.items) {
          const r = M.items[it.id]; if (!r) continue;
          const a = an[it.id] || { partes: {} };
          const x = (it.x ?? 0) + (a.x ?? 0), y = (it.y ?? 0) + (a.y ?? 0);
          const sc = (it.esc ?? 1) * (a.esc ?? 1), rot = (it.rot ?? 0) + (a.rot ?? 0), op = (it.op ?? 1) * (a.op ?? 1);
          const fl = (a.flip ?? (it.flip ? -1 : 1));
          const ctr = it._a.ancla === "centro";
          r.el.style.left = x + "px"; r.el.style.top = y + "px";
          r.el.style.transformOrigin = ctr ? "50% 50%" : "50% 100%";
          r.el.style.transform = `translate(-50%,${ctr ? "-50%" : "-100%"}) rotate(${rot}deg) scale(${sc * fl},${sc})`;
          r.el.style.opacity = it.visible === false ? 0 : op * (a.visible === 0 ? 0 : 1);
          // color selectivo: fondo descolorido, sujeto con color
          const rol = it.rol || it._a.rol || "fondo";
          let sat = rol === "sujeto" ? tema.sujeto_sat : tema.fondo_sat;
          if (it.afin) sat = sat + (1 - sat) * .45;
          if (esc.fondo_sat != null && rol !== "sujeto") sat = it.afin ? esc.fondo_sat + (1 - esc.fondo_sat) * .45 : esc.fondo_sat;
          if (it.sat != null) sat = it.sat;
          const br = it.brillo ?? (rol === "sujeto" ? 1 : (p < 1 ? .95 + .05 * p : 1));
          r.el.style.filter = `saturate(${sat}) brightness(${br}) hue-rotate(${it.hue ?? 0}deg) ${dif}`.trim();
          // partes del rig
          const sv = r.el.firstElementChild;
          if (sv && a.partes) for (const [nombre, v] of Object.entries(a.partes)) {
            const g = sv.querySelector("#" + nombre); if (!g) continue;
            g.style.transformBox = "view-box"; g.style.transformOrigin = `${v.pivote[0]}px ${v.pivote[1]}px`;
            g.style.transform = `translate(${v.dx || 0}px,${v.dy || 0}px) rotate(${v.rot || 0}deg) scale(${v.esc ?? 1})`;
          }
        }
      }
      // overlays
      const fl = (esc.destellos || []).reduce((m, d) => t >= d.t && t <= d.t + d.dur ? Math.max(m, 1 - (t - d.t) / d.dur) : m, 0);
      document.getElementById("flash").style.opacity = fl;
      const fu = (esc.fundidos || []).reduce((m, d) => {
        if (d.tipo === "entrada" && t <= d.t + d.dur) return Math.max(m, 1 - Math.max(0, t - d.t) / d.dur);
        if (d.tipo === "salida" && t >= d.t) return Math.max(m, Math.min(1, (t - d.t) / d.dur));
        return m;
      }, 0);
      const fe = document.getElementById("flash"); if (fu > 0 && fl === 0) { fe.style.background = "#000"; fe.style.opacity = fu; } else fe.style.background = "#fff";
      const bru = document.getElementById("bruma");
      bru.style.background = `linear-gradient(transparent 40%, ${tema.cielo[0]})`; bru.style.opacity = esc.bruma ?? .22;
      M.t = t;
    },

    auditar() { // reglas del PDF: ninguna capa vacia, suelo con textura, primer plano
      const w = [];
      const cats = new Set();
      for (const c of M.capas) { if (!c.items.length) w.push(`capa vacia: ${c.def.nombre}`); c.items.forEach(i => i._a && cats.add(i._a.cat)); }
      if (!cats.has("suelos")) w.push("falta suelo con textura (categoria 'suelos')");
      if (!M.capas.some(c => (c.def.paralaje ?? 1) > 1 && c.items.length)) w.push("sin primer plano (capa con paralaje > 1)");
      if (!cats.has("basura") && !cats.has("naturaleza")) w.push("faltan detalles de suelo (basura/naturaleza)");
      return w;
    }
  };
  window.Motor = M;
  window.renderAt = async t => { M.renderAt(t); await new Promise(r => requestAnimationFrame(() => r())); return true; };
})();
