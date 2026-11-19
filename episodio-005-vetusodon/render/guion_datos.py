"""Texto de la narración (episodio 005) por escena y ortografía rioplatense para el sintetizador.

LINEAS[escena] = lista de frases (una por toma de voz; nunca se solapan).
sheismo(texto): «ll» y «y» consonánticas -> «sh» (llanura -> shanura, yo -> sho, playa -> plasha); la «y» suelta
(conjunción) y la «y» final (hoy, muy, hay) se conservan.
"""
import re

LINEAS = {
    0: ["Esto no es una película de monstruos.",
        "Es un animal. Y es tu pariente.",
        "Caminaba por un mundo sin flores, sin pasto, sin pájaros.",
        "Y estuvo a punto de no contarlo."],
    1: ["Los zulúes tienen una palabra: elikhulu. Significa «el grande».",
        "Los paleontólogos se la pusieron a este bicho en dos mil diecinueve.",
        "Porque, para su tiempo, lo era."],
    2: ["Hace unos doscientos cincuenta y dos millones de años, este valle era otro planeta.",
        "No había hierba. Había helechos con semillas, colas de caballo gigantes, árboles con forma de paraguas.",
        "Y bichos. Muchos bichos.",
        "Algunos con alas. Otros, con demasiadas patas."],
    3: ["Lo encontraron en rocas del Karoo. Cuatro ejemplares.",
        "Y lo que vieron en los dientes y en el cráneo los hizo dudar.",
        "Porque no era un reptil.",
        "Era un cinodonte. Del grupo que, millones de años después, nos incluye a nosotros."],
    4: ["Se despertaba con hambre, como todos.",
        "Comía lo que encontraba: raíces, insectos, lo que se moviera despacio.",
        "Tenía el cuerpo de un animal que no se apura.",
        "Y, casi seguro, la piel cubierta de pelo.",
        "Nadie encontró nunca el pelaje. Pero sus parientes cercanos lo tenían, o estaban en camino."],
    5: ["Mandíbula fuerte. Dientes de distintos tipos. Más cerca de un ratón que de un lagarto."],
    6: ["Pero este mundo tenía dueños.",
        "Los gorgonopsios eran los depredadores más grandes del valle.",
        "Dientes como sables.",
        "Y hambre.",
        "El Vetusodon no tenía garras de cazador ni colmillos de sable.",
        "Tenía algo mejor: un agujero."],
    7: ["Hay un detalle que cambió la ciencia.",
        "Los huesos que hoy tenés dentro del oído...",
        "...en un cinodonte formaban parte de la mandíbula.",
        "Con millones de años, esos huesos se fueron achicando. Hasta que dejaron de masticar, y empezaron a escuchar."],
    8: ["Pero el clima empezaba a cambiar.",
        "El calor subía. El agua bajaba.",
        "Y en el horizonte, una nube marrón que no era de lluvia."],
    9: ["A miles de kilómetros, en lo que hoy es Siberia, la tierra se estaba abriendo.",
        "Volcanes, durante miles de años.",
        "Gases. Ceniza. Lluvia que quema.",
        "Y las plantas, las que alimentaban a todos, empezaron a morir.",
        "Fue la peor extinción de la historia de la Tierra."],
    10: ["Los grandes cayeron primero.",
         "Los gorgonopsios no sobrevivieron.",
         "Pero algunos cinodontes sí. Los pequeños. Los que cavaban.",
         "Los que tenían pelo."],
    11: ["El Vetusodon no llegó al final de esa historia.",
         "Pero el camino que siguió su familia llegó hasta vos.",
         "Cada vez que escuchás una canción, estás usando huesos que alguna vez fueron mandíbula."],
}

_V = "aeiouáéíóúüAEIOUÁÉÍÓÚÜ"


def sheismo(t):
    def palabra(m):
        w = m.group(0)
        if len(w) == 1:
            return w
        w = re.sub(r"ll", "sh", w)
        w = re.sub(r"LL", "SH", w)
        w = re.sub(r"Ll", "Sh", w)
        w = re.sub(r"(?<=[^\W\d_])y(?=[%s])" % _V, "sh", w)       # y entre letras y antes de vocal (mayor, playa, ayuda)
        w = re.sub(r"^y(?=[%s])" % _V, "sh", w)                    # y inicial (yo, ya, yunque)
        w = re.sub(r"^Y(?=[%s])" % _V, "Sh", w)
        return w
    return re.sub(r"[A-Za-zÁÉÍÓÚáéíóúÜüÑñ]+", palabra, t)


def todas():
    return [(e, i, t) for e, ls in sorted(LINEAS.items()) for i, t in enumerate(ls)]


if __name__ == "__main__":
    for t in ("Yo vi la playa y el valle: llanura, mayor, hoy, muy, ayuda. Y bichos.", "Llegó ya con yeso y caballo, ayer."):
        print(sheismo(t))
    print(len(todas()), "líneas", sum(len(t.split()) for _, _, t in todas()), "palabras")
