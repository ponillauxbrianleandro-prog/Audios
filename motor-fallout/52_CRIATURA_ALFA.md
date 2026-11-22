# 52 · TEMA «CRIATURAS ALFA» (tema T14)

## QUÉ SON (tal cual)
Las **criaturas alfa** son un tema propio e **independiente de los animales**: una variante emparentada con los **lobos** que tiene su propia especie base (**Alfa**), su propia cadena de **14 fases** y su propio comportamiento. Se agregan por lore como cualquier otro tema (18). Pueden aparecer en cualquier fase que el lore active.
- Son criaturas **muy altas, de musculatura extrema y fuerza enorme**.
- Su lenguaje, cultura y conducta dependen de la fase (a partir de la 4, hablan).
- **Apariencia corporal:** la define el lore (50). El motor no fija sexo ni género.
- Pueden ser **aliadas, neutrales u hostiles** según el lore; por defecto son **territoriales** y respetan a quien se comporta con respeto.
- Todo alfa humanoide o humano es **adulto**.

## FICHA DE ESPECIE BASE
| ID | Nombre | Talla | Slot | Comportamiento | V1 | V2 | V3 |
|---|---|---|---|---|---|---|---|
| AL-01 | Alfa | T4 | 9 | territorial, gran fuerza, rastrea, aúlla (llama a 1 aliado) | Común | Veterano (+PV) | Guardián del territorio (RD+3) |
| AL-02 | Alfa de rango bajo (adulto) | T3 | 6 | manada 2-4, aprende, flanquea | Común | Corredor | Líder de grupo |
| AL-03 | Alfa mayor | T5 | 13 | territorial, aplasta, protege | Común | Anciano | Patriarca/Matriarca del territorio |
Fórmulas de PV, daño y XP: las de su talla (19, 27). Slots desplazados por fase (25).

## CADENA DE 14 FASES DEL ALFA (descripción neutra, tal cual; el lore la sobrescribe donde quiera)
| Fase | Descripción general | Habla | Manos | Equipo máx. | Notas |
|---|---|---|---|---|---|
| 1 | Alfa en cuatro patas, lobuno enorme, musculatura extrema | No | No | — | instinto de manada y territorio |
| 2 | Alfa lobuno con rasgos humanoides en rostro y torso | No | No | — | observa antes de actuar |
| 3 | Alfa erguido, usa las patas delanteras como manos | No | Patas | objetos simples | curioso, protector |
| 4 | Alfa humanoide de cuerpo erguido, hipermusculado | **Sí** | Patas-mano | E1 | negocia, cuida su territorio |
| 5 | Mitad lobuno, mitad humano, hipermusculado | Sí | Manos | E3 | líder de manada |
| 6 | Humano hipermusculado con rasgos lobunos marcados (dientes inferiores prominentes, vello largo) | Sí | Humanas | E3 | altura absurda |
| 7 | Humano muy alto, hipermusculado, con pocos rasgos lobunos | Sí | Humanas | E4 | sociable |
| 8 | Humano que se identifica con la manada, con accesorios permanentes | Sí | Humanas | E3 | imita la conducta lobuna |
| 9 | Persona con traje o disfraz alfa completo | Sí | Humanas | E2 | juguetona |
| 10 | Persona con accesorios alfa por identidad | Sí | Humanas | E4 | individual |
| 11 | Trabajador con accesorios alfa por obligación laboral | Sí | Humanas | E1 | servicial |
| 12 | Persona con instintos alfa marcados | Sí | Humanas | E3 | iniciativa +10 |
| 13 | Humano alto y robusto, sin rasgos alfa | Sí | Humanas | E5 | normal |
| 14 | Humano que rechaza lo que no parece humano | Sí | Humanas | E5 | evita al alfa |
Los modificadores de PV/daño por fase son los de 25.

## FASES TÍPICAS DE LOS ALFAS DE CAMPAÑA (referencia para lores, tal cual)
- **Fase 1 salvaje:** musculatura extrema, mucho vello largo que rodea los músculos sin cubrirlos del todo, mandíbula con dientes inferiores prominentes, vive en zonas altas y boscosas.
- **Fase 2:** la más común; hipermusculado, vello largo y abundante *para un humano* pero escaso *para un lobo*, dentadura casi humana salvo los colmillos inferiores, sin garras ni colmillos superiores.
- **Fase 3:** la más humana; alto, hipermusculado con algo de grasa corporal, dientes inferiores grandes pero no prominentes.
El lore **puede describir con más detalle estas fases y su vestimenta** (ropa de pieles en las fases 1-2, ropa humana en la fase 3). El motor solo exige: **adulto, sin contenido sexual, vestido según lo que diga el lore.**

## COMPORTAMIENTO (tal cual)
- **Territorial:** no persigue fuera de su territorio; avisa antes de atacar (aúlla).
- **Confianza:** si se les trata con respeto y se les ofrece ayuda o alimento, bajan la guardia. Si se les ataca o se invade su zona, se vuelven hostiles y llaman a su manada (1 aliado por aullido, máx. 2 veces por combate).
- **Combate:** golpes potentes (+20% daño en CORTA), pero movimientos más lentos (−10% velocidad). Se les puede **empujar** menos (la talla T4 no se derriba).
- **Amistad:** pueden convertirse en **aliados temporales** o **compañeros** si el lore lo permite (no hay compañeros alfa por defecto).
- **Conflicto con otras especies:** atacan a las criaturas hostiles de su territorio; son enemigos naturales de los parásitos y los slimes (choque entre especies, 37).

## CÓMO LOS INCORPORA EL LORE (tal cual)
Un lore agrega el tema con `TEMAS_ACTIVOS += [T14]`, lista las fases activas (`ALFA_FASES = [1, 2, 3]`), define su territorio, su ropa y su carácter (cordial, hostil, neutral) y su apariencia. Sin esa entrada, **no existen**.

## FASE 1-3: SLOTS Y NIVELES (referencia)
AL-01 en fase 1 aparece al nivel 18 (slot 9); fase 2: +0; fase 3: +0; fases 4-12 con el desplazamiento de 25. Los gigantes amistosos de un lore pueden saltarse el gating por nivel si son de misión (13).
