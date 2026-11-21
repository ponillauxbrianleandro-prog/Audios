# 10 · OBJETOS E INVENTARIO

## FICHA DE OBJETO
`O-0042 | nombre | cat/subcat | desc | cant | peso | valor | estado | dur(0-100) | origen | procedencia(L-xxx) | compatibilidad | efectos | lore | usable | comerciable | fabricable`
No todo campo es obligatorio. Objetos especiales pueden tener campos extra. Los objetos clave conservan identidad (ID propio); los apilables comparten ID de tipo con cantidad.

## CINCO CATEGORÍAS
1. **Consumibles:** alimentos, bebidas, agua, recuperación, médicos ficticios, supervivencia, ambientales, mejoras temporales, materiales de uso limitado. Campos: efecto, duración, condición, compatibilidad.
2. **Equipo:** ropa, exteriores, calzado, accesorios, mochilas, protección corporal, equipo ambiental, dispositivos, herramientas, instrumentos. Campos: durabilidad, protección abstracta, modificadores, efectos pasivos.
3. **Armas y equipamiento de combate:** según lore. Campos: ID, categoría, estado, compatibilidad, cantidad, propiedades abstractas, requisitos (stat mínimo), modificadores (daño, %impacto, alcance, costo PA).
4. **Objetos generales:** basura, chatarra, materiales, documentos, libros, fotos, notas, llaves, tarjetas, personales, coleccionables, componentes, piezas, herramientas, objetos de misión, decorativos, valor, desconocidos. La chatarra puede servir para comercio, fabricación o misiones.
5. **Recursos:** naturales, industriales, componentes, biológicos, minerales, tecnológicos, ambientales, fabricación, intercambio. Disponibilidad por bioma.

## ARMADURA Y ARMAS (valores abstractos)
- **Arma:** daño min-max, %base, alcance (cuerpo/corto/medio/largo), costo PA, requisito (FUE/PER/AGI mínimo), munición (si aplica), durabilidad. Armas deben pertenecer al lore. Lore puede reemplazar todo.
- **Armadura:** reducción de daño (RD) por pieza: cabeza 1-3, torso 2-8, piernas 1-4, pies 0-2. Total RD = suma; resistencias a ambiente.
- **Durabilidad:** pierde 1-3 por uso/golpe. A 0 → "roto": sin bonus, reparable.

## CARGA
`carga = suma(peso×cant)`; `cargamax = 50 + FUE×10`. Si carga > cargamax: "Sobrecargado" (−10 AGI efectivo, viaje ×1.5). No puedes recoger si excede cargamax + 20% sin soltar algo.

## MONEDA
`chapas` (o la moneda del lore). Peso 0. Se puede perder, robar, gastar.

## REGLAS DE USO
- Usar consumible: reduce cantidad, aplica efecto y duración. Consumible caducado/contaminado: riesgo (estado enfermo).
- Equipar: reemplaza el equipo del mismo slot (el reemplazado vuelve a inventario). Requisitos de uso se validan (sin requisitos: penalización −20%).
- Reparar: requiere herramienta + componentes (tirada INT); recupera durabilidad.
- Fabricar: planos + componentes + estación. Tirada de éxito (50 + INT×4 + bono_nivel), fallo pierde parte de componentes.
- Desarmar: objeto → componentes (según lore).
- Valor base por rareza: Común 1×, Útil 3×, Raro 10×, Excepcional 40×.

## ANTI-DUPLICACIÓN
- Antes de generar un objeto, verificar que no existe ya con ese ID/rol (especialmente objetos clave y únicos).
- Al recoger, eliminar del contenedor/escena. Al soltar, registrar en la ubicación.
- Objetos de misión no se venden ni descartan salvo regla.
- IDs únicos y secuenciales; nunca reutilizar.
- Mostrar cambios de inventario como deltas.

## GENERACIÓN SEGÚN LORE
El lore define: objetos habituales, excepcionales, materiales, monedas y valores por bioma. Si el lore no define algo, usar categoría universal más cercana, nombrada coherentemente. Rechazar objetos de otro universo.
Rareza por tirada (un objeto): Común 55 · Útil 28 · Raro 13 · Excepcional 4 (Se ajusta con SUE: +1% hacia raro por cada punto sobre 5.)

## PLANTILLA INVENTARIO (ver 15)
Mostrar por categoría, con cantidad, peso total/carga, chapas y equipo.
