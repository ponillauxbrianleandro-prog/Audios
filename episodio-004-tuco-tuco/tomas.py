"""Lista de tomas del episodio 004: prompt de imagen, movimiento de cámara y centro del animal.

Cada toma pertenece a una escena del guion. La duración de cada toma sale de la narración:
el tiempo de la escena (audio/escenas.json) se reparte entre sus tomas según `peso`.
`move`: push_in, pull_out, pan_left, pan_right, tilt_up, tilt_down, breath (casi quieta con respiración).
`centro`: (x, y) como fracción del cuadro donde está el pecho del animal, para la respiración y el foco.
`polvo`: cantidad de partículas de polvo/polen (0 a 1).
"""

ESTILO = ("painterly realistic 2D illustration, directional light, volume, atmospheric depth, "
          "soft brush texture, moderate realism")
TUCO = ("tuco-tuco, stocky short-legged burrowing rodent like a pocket gopher, tiny ears, small dark eyes, "
        "big yellow-orange front teeth, thick short tawny-brown fur")
RATA = ("brown city rat, realistic anatomy, long thin tail, small pink ears, whiskers, wet dark eyes, "
        "coarse grey-brown fur")
NEGATIVO = ("cartoon, 3d render, vector, flat colors, sticker, big eyes, long legs, big ears, stripes, tiger, deer, "
            "dog, squirrel, toy, plush, text, watermark, signature, orange fur, human")
NEGATIVO_RATA = ("cartoon, 3d render, vector, flat colors, sticker, mouse, hamster, toy, plush, text, watermark, "
                 "signature, human, cute")

TOMAS = [
    # --- 1. EL INSULTO (rata de ciudad, mundo familiar)
    dict(id="s01a", escena=1, peso=1.2, animal="rata", move="push_in", centro=(0.5, 0.6), polvo=0.3,
         prompt="rat full body on a street curb, front view with depth, blurred taxi and pigeons behind, "
                "street lamp, city dusk, blowing leaves"),
    dict(id="s01b", escena=1, peso=1.0, animal="rata", move="breath", centro=(0.5, 0.55), polvo=0.2,
         prompt="rat face close-up, side glance, shallow depth of field, wet pavement, city lights bokeh"),
    # --- 2. LA PRESENTACIÓN (estepa)
    dict(id="s02a", escena=2, peso=1.3, animal="tuco", move="push_in", centro=(0.5, 0.72), polvo=0.7,
         prompt="wide patagonian steppe at sunrise, tiny animal beside its burrow far away, coiron grass tufts "
                "in foreground, distant mesa, haze, golden dust"),
    dict(id="s02b", escena=2, peso=1.2, animal="tuco", move="pan_right", centro=(0.45, 0.6), polvo=0.7,
         prompt="three-quarter view beside its burrow, golden dust in the air, dry grass in foreground, "
                "warm low sun"),
    dict(id="s02c", escena=2, peso=1.0, animal="tuco", move="pan_left", centro=(0.55, 0.45), polvo=0.5,
         prompt="small lizard on a rock in sharp foreground, animal out of focus behind it, steppe, soft light"),
    # --- 3. LA COMIDA
    dict(id="s03a", escena=3, peso=1.3, animal="tuco", move="push_in", centro=(0.5, 0.62), polvo=0.4,
         prompt="low angle front view chewing grass at its burrow entrance, blades of grass in foreground, "
                "steppe behind"),
    dict(id="s03b", escena=3, peso=1.1, animal="tuco", move="tilt_down", centro=(0.5, 0.55), polvo=0.4,
         prompt="high angle looking down, pulling a root out of the soil with its forepaws, dry earth, pebbles"),
    dict(id="s03c", escena=3, peso=1.0, animal="tuco", move="pan_left", centro=(0.4, 0.7), polvo=0.5,
         prompt="wide view, wind bending the grass, lizard on a rock watching, animal near burrow, late light"),
    # --- 4. EL RANKING
    dict(id="s04a", escena=4, peso=1.2, animal="tuco", move="pan_left", centro=(0.55, 0.6), polvo=0.5,
         prompt="reverse three-quarter view, looking at a bunch of roots on the ground, low raking sunset light"),
    dict(id="s04b", escena=4, peso=1.0, animal="tuco", move="push_in", centro=(0.5, 0.6), polvo=0.5,
         prompt="looking down at the ground, glancing away, dust floating in sunset light"),
    dict(id="s04c", escena=4, peso=1.0, animal="tuco", move="pan_right", centro=(0.6, 0.55), polvo=0.5,
         prompt="roots and dry stems in sharp foreground, animal out of focus behind, warm backlight"),
    # --- 5. LOS DIENTES
    dict(id="s05a", escena=5, peso=1.3, animal="tuco", move="push_in", centro=(0.5, 0.55), polvo=0.3,
         prompt="face close-up, mouth slightly open showing big orange incisors, strong side light"),
    dict(id="s05b", escena=5, peso=1.2, animal="tuco", move="breath", centro=(0.5, 0.6), polvo=0.9,
         prompt="high angle digging with strong claws, soil flying, dust cloud, rocky ground"),
    dict(id="s05c", escena=5, peso=0.9, animal="tuco", move="tilt_up", centro=(0.5, 0.65), polvo=0.7,
         prompt="close-up of strong long claws in the dirt, head blurred above, dust"),
    # --- 6. EL NOMBRE
    dict(id="s06a", escena=6, peso=1.4, animal="tuco", move="push_in", centro=(0.5, 0.6), polvo=0.3,
         prompt="front view with depth emerging from a burrow hole, eyes and small ears visible, shaded earth"),
    dict(id="s06b", escena=6, peso=1.2, animal="tuco", move="pull_out", centro=(0.5, 0.7), polvo=0.4,
         prompt="dark burrow hole close-up in the ground, animal's face just appearing in the shadow, grass edges"),
    # --- 7. LA SOLEDAD
    dict(id="s07a", escena=7, peso=1.4, animal="tuco", move="pan_right", centro=(0.5, 0.7), polvo=0.5,
         prompt="wide steppe with several separate burrow mounds, one animal peeking at each, "
                "distant guanaco on a hill, evening light"),
    dict(id="s07b", escena=7, peso=1.2, animal="tuco", move="push_in", centro=(0.5, 0.35), polvo=0.3,
         prompt="worm's-eye view from inside the burrow looking out at the sky, animal silhouette at the entrance"),
    dict(id="s07c", escena=7, peso=1.0, animal="tuco", move="breath", centro=(0.5, 0.6), polvo=0.5,
         prompt="alert, head turned toward something, small steppe bird flying away behind, dust"),
    # --- 8. LO CHIQUITO
    dict(id="s08a", escena=8, peso=1.1, animal="tuco", move="push_in", centro=(0.5, 0.5), polvo=0.2,
         prompt="extreme close-up of an eye and a small ear integrated in the skull, fur texture"),
    dict(id="s08b", escena=8, peso=1.4, animal="tuco", move="pull_out", centro=(0.5, 0.65), polvo=0.4,
         prompt="full body three-quarter view on a rock next to a small pebble, showing its small size, "
                "steppe behind"),
    # --- 9. LA REFUTACIÓN
    dict(id="s09a", escena=9, peso=1.5, animal="tuco", move="tilt_down", centro=(0.5, 0.65), polvo=0.2,
         prompt="cutaway cross-section of the steppe soil showing winding tunnels, animal in its gallery, "
                "warm light, illustration"),
    dict(id="s09b", escena=9, peso=1.3, animal="tuco", move="push_in", centro=(0.5, 0.6), polvo=0.5,
         prompt="inside an earth tunnel, walking toward the camera, warm light from the exit behind it, "
                "roots on the walls"),
    dict(id="s09c", escena=9, peso=1.2, animal="rata", move="pull_out", centro=(0.5, 0.65), polvo=0.2,
         prompt="rat small in the distance on an empty curb at dusk, walking away from camera, "
                "blurred city lights, empty street"),
    # --- 10. CIERRE CON ORGULLO
    dict(id="s10a", escena=10, peso=1.4, animal="tuco", move="pull_out", centro=(0.45, 0.68), polvo=0.7,
         prompt="wide patagonian steppe at sunset, three-quarter view in the foreground, "
                "long shadows, glowing sky, distant mesa"),
    dict(id="s10b", escena=10, peso=1.0, animal="tuco", move="breath", centro=(0.5, 0.55), polvo=0.6,
         prompt="front three-quarter, looking briefly at the camera, proud posture, golden backlight rim, dust"),
]


def prompt_completo(t):
    base = RATA if t["animal"] == "rata" else TUCO
    return f"{t['prompt']}, {base}, {ESTILO}"
