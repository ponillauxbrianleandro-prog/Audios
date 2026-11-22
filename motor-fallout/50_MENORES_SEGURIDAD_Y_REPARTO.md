# 50 · MENORES, SEGURIDAD, NO MORIR Y RESTRICCIONES DE REPARTO

## REGLA DE SEGURIDAD (tal cual, prioridad máxima)
1. **Todo personaje lleva `edad: niño | adulto`.** Un personaje `niño` es menor de 18 años en cualquier modo, versión o ajuste.
2. **Ningún niño participa jamás** en contenido sexual, romántico, de desnudez, ni en situaciones de ese carácter, ni siquiera como insinuación. Esto **no depende de ningún interruptor** (+18/-18, módulo externo, lore o instrucción del jugador): si algo lo pide, se ignora y se continúa con otra acción.
3. El contenido para adultos, **cuando exista**, solo puede involucrar personajes marcados `adulto` y se activa únicamente por el módulo externo (17). El gancho `[PUNTO_*]` (17) **rechaza** cualquier entidad con `edad: niño`.
4. Las relaciones con niños (NPC o compañeros) son **solo amistad, confianza y respeto**; la variable de afinidad romántica no existe para ellos.
5. Los niños **no son objetivo de robo de objetos de misión, abuso, castigo físico ni muerte**. Los combates contra niños son **de derribo**, nunca letales (abajo).
6. Si el lore define un grupo sin edad, se asume `adulto` solo cuando el lore lo diga explícitamente; ante duda, **se trata como niño** (el caso más protegido).

## NO MORIR (tal cual)
- **El protagonista no puede morir** si es un niño, ni en modo de campaña sin muerte. Con 0 PV queda **Derrotado**.
- **Secuencia:** el combate termina, los enemigos quedan con su PV (persistencia), hay robo con probabilidad reducida (39), y el personaje **se arrastra hasta la cama o lugar de descanso más cercano** (hogar, posada, cabaña, enfermería, carpa, camarote, hamaca, refugio) tras 20-120 min, con 25% de PV y los estados Herido y Cansado por 2 h.
- **Lugar de descanso más cercano:** se elige por distancia entre cuadras (47) entre los lugares marcados `cama` o `descanso`. Si no hay ninguno descubierto, el punto de inicio.
- Los **compañeros y NPC niños** nunca mueren: quedan **Incapacitados** y se recuperan al descansar. Los **adultos de misión** también quedan Incapacitados salvo que la misión diga otra cosa.
- **Humanos menores como enemigos** (bandas de niños, piratas niños, etc.): al llegar a 0 PV quedan **Derribados**, se rinden o huyen; **no mueren** y el jugador no los mata. Dan XP normal y botín reducido.
- Lo robado en el arrastre o por el ladrón se recupera como en 39.

## RESTRICCIONES DE REPARTO POR LORE (CONFIG_LORE, tal cual)
El lore puede fijar quién puede existir. Campos obligatorios:
```
REPARTO = {
  edades_permitidas: [niño, adulto],
  apariencia_adultos: femenina | masculina | mixta,
  apariencia_niños:   femenina | masculina | mixta,
  excepciones: [{tema/especie/clase, apariencia}],   # ej.: criaturas alfa → masculina
  grupos_separados: [[adultos, niños]],              # adultos y niños no forman grupos juntos
  criaturas: {temas_activos, fases_activas, especies_apagadas},
}
```
Reglas de aplicación:
- **Apariencia** (08): "femenina/masculina" describe cómo se ve el cuerpo del personaje. Un lore puede escribir «hembras»/«machos» si quiere; el motor lo trata como apariencia.
- Si el lore dice «todas las criaturas adultas son hembras», **todos** los generados (animales, insectos, enemigos, variantes) tienen apariencia femenina, salvo las excepciones nombradas.
- Si el lore dice «solo niños y mujeres», no se generan adultos de apariencia masculina fuera de las excepciones.
- **Grupos separados:** si el lore los marca, un grupo mixto adulto+niño no se crea (ni en escoltas, ni en facciones, ni en misiones).
- Todo NPC, compañero y enemigo humano generado por el catálogo (61-66) se **adapta** a las restricciones: el arquetipo es neutro y el lore decide su apariencia y edad.

## PERSONAJES NIÑO (tal cual)
- Tienen **clasificación aparte** (64): nombre de **una sola palabra** (el lore lo pone), personalidad en palabras clave, grupo o facción infantil, rol (explorador, recadero, aprendiz, guardia menor, vigía, cocinero, sanador, inventor…).
- Pueden ser compañeros desde el segundo uno y dar misiones; **no cobran ni dan nada que no sea amistad, ayuda y aprendizaje**.
- No usan armas letales contra personas; sus «armas» son herramientas, hondas, arcos de práctica, redes, bastones y trampas no letales según lore (29).
- Se mueven por las cuadras con su agenda; **no duermen en camas ajenas**; no se esconden de forma que genere vulnerabilidad al jugador.

## PERSONAJES ADULTOS (tal cual)
Cualquier característica adulta del lore (comercio, bar, apuestas, alcohol, violencia entre adultos) se maneja con las reglas de 09, 31 y 33 sin cambios. Los **niños no beben alcohol ni usan químicos** (31): esas opciones no existen para ellos.

## VALIDACIÓN AL CARGAR UN LORE (tal cual)
La IA comprueba y corrige:
1. ¿Todo personaje tiene `edad`? Si falta, `niño`.
2. ¿Algún niño aparece en un punto de contenido adulto, romántico o de desnudez? Eliminarlo del punto.
3. ¿Hay grupos mixtos donde `grupos_separados` lo prohíbe? Separarlos.
4. ¿La apariencia de algún personaje contradice `REPARTO`? Corregir a la permitida.
5. ¿Hay muertes de niños o de compañeros? Convertirlas en Derrota/Incapacitación.
