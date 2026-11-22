"""Catalogo de NPC por arquetipo (sin nombres originales de ningun juego).

Formato de cada linea: rol; palabras clave; tipo de lugar; tipos de mision posibles.
Tipo de lugar: REF refugio/instalacion · ASE asentamiento · MIL orden armada · TOR torre/enclave ·
HOS hostil/campamento · CAM camino/ruina · ESP especial · SUB comunidad subterranea · IND granja/industria ·
CIE ciencia/radio · COM comercio · PUE puerto/muelle.
"""

ADULTOS = """
supervisor/a de instalación; autoritario/a, controlador/a, secreto; REF; BND,INV,NEG,FAM
jefe/a médico/a de instalación; culto/a, amable, reservado/a; REF; MED,CUR,INV
guardia de seguridad de instalación; estricto/a, cansado/a, leal; REF; VIG,AMN,DEF
maestro/a de instalación; paciente, firme, protector/a; REF; ENS,FAM,REC
cocinero/a comunal; generoso/a, mandón/a, chismoso/a; REF; COM,RCL,FIE
técnico/a de mantenimiento; obsesivo/a, ingenioso/a, impaciente; REF; FAB,HCK,CON
científico/a de instalación; curioso/a, distraído/a, brillante; REF; INV,HCK,PUZ
guía de la instalación; amable, ordenado/a, nervioso/a; REF; ESC,MAP
cuidador/a de archivos; metódico/a, callado/a, curioso/a; REF; INV,REC,HCK
radio operador/a de instalación; alegre, hablador/a, solitario/a; REF; HCK,MSJ
intendente de instalación; ahorrativo/a, estricto/a; REF; COM,REC
vecino/a mayor de instalación; nostálgico/a, terco/a, protector/a; REF; FAM,REC
comisario/a de asentamiento; honesto/a, rígido/a, orgulloso/a; ASE; DET,AMN,VIG,BND
alcalde/sa de asentamiento; pragmático/a, firme, diplomático/a; ASE; NEG,BND,DEF
sacerdote/sa de comunidad; sereno/a, persuasivo/a, bondadoso/a; ASE; MED,NEG,PUZ
médico/a de asentamiento; cansado/a, ético/a, sarcástico/a; ASE; MED,CUR,RCL
comerciante de armas; charlatán/a, codicioso/a, leal; COM; COM,REC,CTR
comerciante de recursos generales; curioso/a, ahorrativo/a, regateador/a; COM; COM,RCL,REC
comerciante de comida; generoso/a, mandón/a, supersticioso/a; COM; COM,RCL,FIE
comerciante de medicinas; cauto/a, ético/a, reservado/a; COM; MED,CUR,COM
comerciante de animales de carga; bonachón/a, miedoso/a, hablador/a; COM; TRA,ESC,COM
comerciante de ropa y telas; creativo/a, vanidoso/a, simpático/a; COM; COM,FAB,FIE
comerciante de libros y notas; erudito/a, tranquilo/a, curioso/a; COM; ENS,REC,INV
mecánico/a; obsesivo/a, perfeccionista, impaciente; ASE; FAB,REC,CON
herrero/a; fuerte, orgulloso/a, paciente; ASE; FAB,CON,COM
armero/a; meticuloso/a, desconfiado/a, hábil; ASE; FAB,REC,INF
curtidor/a; callado/a, trabajador/a, práctico/a; ASE; RCL,CAZ,COM
tabernero/a; cálido/a, discreto/a, chismoso/a; ASE; INV,COM,FIE
posadero/a; hospitalario/a, curioso/a, cansado/a; ASE; ESC,COM,FAM
cantinero/a de local; sarcástico/a, cordial, atento/a; ASE; INV,CTR,DET
animador/a de espectáculo; carismático/a, trabajador/a, risueño/a; ASE; FIE,MSJ
apostador/a profesional; astuto/a, ambicioso/a, supersticioso/a; ASE; FIE,COB,DET
prestamista; frío/a, calculador/a, educado/a; ASE; COB,NEG,CTR
cobrador/a de deudas; insistente, tenso/a, cumplidor/a; ASE; COB,NEG
mensajero/a; nervioso/a, veloz, chismoso/a; ASE; MSJ,EXP,TRA
pregonero/a; fuerte, divertido/a, dramático/a; ASE; MSJ,FIE
cartero/a del pueblo; puntual, amable, cansado/a; ASE; MSJ,TRA
bibliotecario/a; erudito/a, sereno/a, protector/a; ASE; ENS,REC,PUZ
maestro/a de pueblo; paciente, firme, soñador/a; ASE; ENS,FAM,FIE
científico/a de asentamiento; distraído/a, brillante, curioso/a; ASE; INV,HCK,RCL
inventor/a; excéntrico/a, optimista, distraído/a; ASE; FAB,CON,ART
juez/a improvisado/a; justo/a, severo/a, cansado/a; ASE; DET,NEG,BND
abogado/a del pueblo; elocuente, escéptico/a, ocupado/a; ASE; DET,NEG
periodista local; curioso/a, insistente, valiente; ASE; INV,MSJ,DET
locutor/a de radio; carismático/a, nocturno/a, solitario/a; CIE; HCK,MSJ,FIE
escritor/a del páramo; soñador/a, introvertido/a, crítico/a; ASE; INV,ENS
cartógrafo/a; meticuloso/a, aventurero/a, curioso/a; ASE; MAP,EXP,ESC
adivino/a o vidente; misterioso/a, teatral, amable; ESP; PUZ,INV,ART
borracho/a del pueblo; simpático/a, llorón/a, desordenado/a; ASE; REC,FAM
mendigo/a sabio/a; humilde, observador/a, bromista; ASE; INV,MSJ
guardia de puerta; estricto/a, aburrido/a, leal; ASE; VIG,DEF
cazador/a de recompensas; callado/a, preciso/a, desconfiado/a; CAM; CAZ,DET,COB
escribano/a; metódico/a, tímido/a, perfeccionista; ASE; DET,INV,MSJ
artesano/a; creativo/a, paciente, orgulloso/a; ASE; FAB,COM,FIE
recolector/a de chatarra; ingenioso/a, ahorrativo/a, solitario/a; CAM; RCL,REC,COM
sepulturero/a; callado/a, filósofo/a, tranquilo/a; ASE; PUZ,INV
partera o enfermero/a comunal; bondadoso/a, firme, incansable; ASE; MED,CUR
panadero/a; madrugador/a, generoso/a, mandón/a; ASE; COM,RCL
carnicero/a; directo/a, trabajador/a, práctico/a; ASE; CAZ,COM
pescador/a; alegre, supersticioso/a, valiente; PUE; RCL,CAZ,ESC
barquero/a; callado/a, hábil, ahorrativo/a; PUE; ESC,TRA
guardia del puerto; estricto/a, cansado/a, curioso/a; PUE; VIG,AMN
contrabandista; astuto/a, encantador/a, tenso/a; PUE; CTR,INF
capitán/a de barco; carismático/a, valiente, orgulloso/a; PUE; ESC,EXP,JEF
vigía de faro; solitario/a, soñador/a, atento/a; PUE; MSJ,INV
oficial de aduana; meticuloso/a, desconfiado/a, formal; PUE; DET,CTR
líder de orden armada; carismático/a, disciplinado/a, justo/a; MIL; BND,DEF,NEG
caballero/a de orden; honesto/a, orgulloso/a, leal; MIL; AMN,DEF,ESC
escriba o técnico/a de orden; erudito/a, distraído/a, curioso/a; MIL; INV,HCK,ART
paladín/a de orden; fuerte, noble, severo/a; MIL; JEF,AMN,DEF
intendente de orden; ahorrativo/a, estricto/a, justo/a; MIL; COM,REC
armero/a de orden; meticuloso/a, orgulloso/a; MIL; FAB,REC
reclutador/a de orden; persuasivo/a, directo/a; MIL; EXP,VIG
desertor/a de orden; culposo/a, asustado/a, noble; MIL; RSC,NEG
médico/a militar; práctico/a, cansado/a, bondadoso/a; MIL; MED,CUR
estratega militar; frío/a, calculador/a, paciente; MIL; DEF,BND
vigía de torre militar; atento/a, callado/a, leal; MIL; VIG,AMN
instructor/a de campo; severo/a, motivador/a, exigente; MIL; ENS,VIG
ingeniero/a de campo; ingenioso/a, impaciente, práctico/a; MIL; CON,FAB,HCK
exploradora de orden; valiente, curioso/a, ágil; MIL; EXP,MAP
cazadora de bestias de orden; callada, precisa, respetuosa; MIL; CAZ,JEF
archivero/a de orden; callado/a, metódico/a, protector/a; MIL; INV,REC
dueño/a de torre habitada; ambicioso/a, elegante, desconfiado/a; TOR; BND,NEG,CTR
gerente de torre; formal, nervioso/a, eficiente; TOR; NEG,REC,DET
conserje de torre; amable, chismoso/a, observador/a; TOR; MSJ,INV
chef de torre; exigente, creativo/a, orgulloso/a; TOR; RCL,FIE
guardia de torre; estricto/a, aburrido/a, leal; TOR; VIG,AMN
huésped adinerado/a; vanidoso/a, caprichoso/a, curioso/a; TOR; COM,ART
excluido/a de la torre; resentido/a, valiente, digno/a; TOR; BND,NEG
activista por la inclusión; apasionado/a, terco/a, generoso/a; TOR; NEG,BND
médico/a de torre; discreto/a, ocupado/a, ético/a; TOR; MED,CUR
secretario/a de torre; eficiente, tenso/a, discreto/a; TOR; MSJ,DET
asesor/a de torre; frío/a, estratega, amable; TOR; NEG,DET
capitán/a de saqueadores; bravucón/a, carismático/a, cruel; HOS; BND,AMN,NEG
líder de esclavistas; cruel, calculador/a, falso/a cortés; HOS; RSC,JEF,BND
traficante de cautivos; frío/a, hablador/a, codicioso/a; HOS; RSC,CTR
jefe/a de pandilla; bravucón/a, leal, impulsivo/a; HOS; BND,NEG,DEF
mercenaria; fría, pragmática, leal al pago; HOS; ESC,CAZ,AMN
francotirador/a de banda; callado/a, preciso/a, paciente; HOS; JEF,INF
líder de culto; carismático/a, fanático/a, amable; HOS; BND,INV,PUZ
sacerdote/sa de culto; sereno/a, fanático/a, persuasivo/a; HOS; PUZ,INV
médico/a de culto; amable, obediente, miedoso/a; HOS; MED,RSC
capataz de campamento; autoritario/a, cruel, ambicioso/a; HOS; JEF,RSC
domador/a de bestias; paciente, rudo/a, orgulloso/a; HOS; DOM,CAZ,JEF
ladrón/a de camino; astuto/a, ágil, bromista; CAM; INF,DET,REC
bandido/a de peaje; bravucón/a, calculador/a, ruidoso/a; CAM; AMN,NEG
infiltrado/a; astuto/a, encantador/a, tenso/a; HOS; INF,DET
ex saqueador/a arrepentido/a; culposo/a, servicial, asustadizo/a; CAM; REC,RSC,FAM
jefe/a de caravana; astuto/a, cansado/a, protector/a; CAM; ESC,TRA,CTR
guardia de caravana; leal, ruidoso/a, cansado/a; CAM; ESC,DEF
buhonero/a ambulante; nervioso/a, misterioso/a, simpático/a; CAM; COM,MSJ,INV
viajero/a perdido/a; educado/a, asustado/a, agradecido/a; CAM; RSC,ESC
superviviente aislado/a; desconfiado/a, ingenioso/a, solitario/a; CAM; RSC,INV
náufrago/a; agradecido/a, agotado/a, valiente; PUE; RSC,FAM
prisionero/a; digno/a, asustado/a, ingenioso/a; HOS; RSC,INF
explorador/a herido/a; valiente, cansado/a, orgulloso/a; CAM; RSC,MSJ
peregrino/a; sereno/a, resistente, curioso/a; CAM; ESC,PUZ
ermitaño/a; solitario/a, filósofo/a, gruñón/a; ESP; PUZ,INV,ART
anciano/a sabio/a; paciente, tozudo/a, bondadoso/a; ESP; ENS,PUZ,FAM
guardián/a de un archivo; callado/a, protector/a, desconfiado/a; ESP; PUZ,HCK
curador/a de museo; erudito/a, orgulloso/a, meticuloso/a; ESP; ART,REC
coleccionista; excéntrico/a, ambicioso/a, curioso/a; ESP; ART,COM
guía de supervivencia; práctico/a, directo/a, sabio/a; ESP; MAP,ENS
botánico/a; curioso/a, paciente, distraído/a; ESP; RCL,MED
domadora de criaturas; paciente, valiente, tierna; ESP; DOM,CAZ
apicultor/a; paciente, tranquilo/a, valiente; IND; RCL,AMN
criador/a de ganado; cansado/a, protector/a, terco/a; IND; AMN,CAZ,COM
agricultor/a; trabajador/a, paciente, supersticioso/a; IND; RCL,DEF
sembradora de cultivos raros; soñadora, paciente, creativa; IND; RCL,ART
mecánico/a rural; práctico/a, quejoso/a, ingenioso/a; IND; FAB,CON
pastor/a de rebaños; callado/a, protector/a, tranquilo/a; IND; AMN,DOM
molinero/a; amable, trabajador/a, hablador/a; IND; REC,CON
aguatero/a; cansado/a, justo/a, sociable; IND; TRA,CUR
minero/a; fuerte, supersticioso/a, silencioso/a; IND; JEF,RCL
capataz de silo; autoritario/a, justo/a, cansado/a; IND; HCK,REC
capataz de granja; severo/a, justo/a, trabajador/a; IND; AMN,DEF
panadera de campo; generosa, madrugadora, mandona; IND; COM,FIE
jefe/a de comunidad subterránea; carismático/a, protector/a, terco/a; SUB; BND,NEG,DEF
alcalde/sa subterráneo/a; ingenioso/a, serio/a, joven de espíritu; SUB; NEG,DEF
curandero/a subterráneo/a; sabio/a, amable, reservado/a; SUB; MED,CUR
guía de túneles; ágil, callado/a, hábil; SUB; ESC,EXP
vigía subterráneo/a; atento/a, nervioso/a, leal; SUB; VIG,DEF
almacenero/a subterráneo/a; ahorrativo/a, estricto/a; SUB; COM,REC
anciano/a subterráneo/a; sabio/a, nostálgico/a, tozudo/a; SUB; PUZ,ENS
operador/a de radio nocturno/a; solitario/a, simpático/a, cansado/a; CIE; HCK,MSJ
ingeniero/a de purificación; metódico/a, brillante, obsesivo/a; CIE; ART,HCK,CON
científico/a del agua; curioso/a, paciente, distraído/a; CIE; INV,CUR,RCL
archivista de datos; callado/a, ordenado/a, curioso/a; CIE; HCK,INV
programador/a de inteligencia artificial; brillante, tímido/a, perfeccionista; CIE; HCK,PUZ
técnico/a de antenas; práctico/a, aventurero/a, bromista; CIE; CON,SAB
voz de un sistema antiguo; amable, perdido/a, servicial; CIE; HCK,PUZ
robot servicial (apariencia a elección); amable, literal, leal; ESP; FAB,ENS,REC
robot guardián de lugar; estricto, leal, literal; ESP; JEF,PUZ
robot comerciante; cortés, calculador, curioso; COM; COM,REC
crupier de casino; elegante, discreto/a, observador/a; COM; FIE,DET
dueño/a de casino; ambicioso/a, carismático/a, desconfiado/a; COM; BND,NEG,COB
cantante de local; carismático/a, sensible, perfeccionista; COM; FIE,MSJ
diplomático/a de facción; elocuente, paciente, calculador/a; ASE; NEG,BND
guardia fronteriza; estricta, justa, cansada; MIL; VIG,DEF
ranger de patrulla; práctico/a, leal, silencioso/a; MIL; VIG,CAZ,ESC
enfermero/a de campo; amable, incansable, práctico/a; MIL; MED,CUR
inversor/a ambicioso/a; calculador/a, nervioso/a, encantador/a; COM; COM,CTR
entrenador/a de combate; severo/a, motivador/a, generoso/a; ASE; ENS,FIE
cocinero/a ambulante; alegre, hablador/a, generoso/a; CAM; COM,RCL,FIE
jardinero/a de oasis; paciente, tierno/a, protector/a; ESP; RCL,DOM
guardián/a de un manantial; solemne, celoso/a, amable; ESP; PUZ,CUR
cuidador/a de faro; solitario/a, soñador/a, hospitalario/a; PUE; INV,MSJ
pregonera de feria; ruidosa, dramática, divertida; ASE; FIE,MSJ
encargado/a de depósito; ahorrativo/a, meticuloso/a, tenso/a; IND; COM,DET
sereno/a de barrio; atento/a, bromista, cansado/a; ASE; VIG,DEF
vendedor/a de rumores; chismoso/a, astuto/a, simpático/a; ASE; INV,MSJ
organizador/a de torneos; entusiasta, justo/a, hablador/a; ASE; FIE
curtidora de pieles raras; callada, orgullosa, práctica; ASE; CAZ,RCL
lavandero/a comunal; chismoso/a, trabajador/a, bondadoso/a; ASE; MSJ,FAM
maestra de oficios; paciente, firme, generosa; ASE; ENS,FAB
decano/a de un grupo de oficios; justo/a, anciano/a, tradicionalista; ASE; NEG,BND
vigilante de cementerio; callado/a, supersticioso/a, valiente; ASE; PUZ,AMN
jefe/a de obras; autoritario/a, práctico/a, apurado/a; ASE; CON,DEF
reparador/a de relojes y máquinas finas; meticuloso/a, tímido/a, perfeccionista; ASE; FAB,ART
juglar o narrador/a de historias; carismático/a, soñador/a, mentiroso/a; ASE; FIE,INV
exiliado/a de otra región; digno/a, nostálgico/a, reservado/a; CAM; FAM,MSJ
guardiana de un puente; severa, justa, aburrida; CAM; VIG,CON
maestro/a de armas; severo/a, noble, paciente; MIL; ENS,FIE
chamán/a o guía espiritual; sereno/a, enigmático/a, bondadoso/a; ESP; PUZ,MED,INV
domador/a de aves mensajeras; paciente, hablador/a, cuidadoso/a; ESP; MSJ,DOM
buscador/a de reliquias; aventurero/a, obsesivo/a, ambicioso/a; CAM; ART,EXP,REC
vigía de los caminos; callado/a, observador/a, leal; CAM; VIG,AMN
tejedor/a; creativo/a, tranquilo/a, orgulloso/a; ASE; FAB,COM
alfarero/a; paciente, creativo/a, charlatán/a; ASE; FAB,RCL
carpintero/a de ribera o de pueblo; trabajador/a, práctico/a, bromista; ASE; CON,FAB
albañil o constructor/a; fuerte, práctico/a, estricto/a; ASE; CON,DEF
vendedor/a de agua; cansado/a, justo/a, regateador/a; ASE; CUR,TRA
pregonero/a de noticias; ruidoso/a, informado/a, dramático/a; ASE; MSJ,INV
guardián/a de una biblioteca; erudito/a, estricto/a, protector/a; ASE; REC,ENS
niñero/a o cuidador/a de grupo (adulto/a); paciente, firme, cálido/a; ASE; FAM,ENS
organizador/a de caravanas; práctico/a, ahorrativo/a, estricto/a; CAM; TRA,ESC
ex militar retirado/a; callado/a, honesto/a, cansado/a; ASE; ENS,AMN
guardia de la tumba de un héroe; solemne, orgulloso/a, leal; ESP; PUZ,AMN
descifradora de mensajes; brillante, nerviosa, paciente; CIE; HCK,PUZ,INV
cuidadora de un jardín antiguo; tierna, protectora, tozuda; ESP; RCL,DOM
""".strip().splitlines()


ADULTOS += """
líder de una facción rival; carismático/a, ambicioso/a, calculador/a; ASE; BND,NEG,DEF
embajador/a o enviado/a de una facción; elocuente, paciente, cauto/a; ASE; NEG,MSJ
jefe/a de una compañía de transporte; práctico/a, ahorrativo/a, estricto/a; CAM; TRA,ESC,COM
guardia de un banco o depósito de valores; leal, serio/a, aburrido/a; ASE; VIG,DEF
cajero/a o tesorero/a de la comunidad; metódico/a, nervioso/a, honesto/a; ASE; DET,COB
jefa de cuadrilla de recolectores; autoritaria, trabajadora, justa; CAM; RCL,ESC
comisaria de un campamento minero; severa, cansada, justa; IND; DET,AMN
dueña de una cantina de frontera; sarcástica, cordial, observadora; ASE; INV,CTR,DET
cuidadora de un orfanato o casa de acogida (adulta); paciente, firme, cálida; ASE; FAM,REC,ENS
domadora de caravanas de animales; paciente, rudo/a, orgulloso/a; CAM; TRA,DOM
farmacéutico/a; meticuloso/a, cauto/a, ético/a; ASE; MED,CUR,COM
organizadora de un mercado; entusiasta, mandona, justa; COM; FIE,NEG
ingeniera de caminos y puentes; práctica, impaciente, ingeniosa; MIL; CON,EXP
mensajera de una orden; veloz, leal, reservada; MIL; MSJ,ESC
archivera de un refugio olvidado; callada, metódica, curiosa; REF; INV,HCK,REC
cartomántica o lectora de señales; teatral, amable, enigmática; ESP; PUZ,INV
guardiana de un santuario de agua; solemne, protectora, amable; ESP; CUR,PUZ
cocinera de campamento; alegre, generosa, mandona; CAM; COM,RCL,FIE
leñadora o guardabosques; fuerte, callada, protectora; CAM; AMN,CAZ,DOM
guía de pantano o de ribera; hábil, callada, resistente; CAM; ESC,EXP
curtidora de redes y velas; paciente, trabajadora, orgullosa; PUE; FAB,COM
maestra de navegación; severa, soñadora, precisa; PUE; ENS,MAP
vigilante de mercado negro; astuta, tensa, discreta; COM; INF,CTR,DET
reparadora de relojes y radios; meticulosa, tímida, perfeccionista; ASE; FAB,HCK
curandera de hierbas; sabia, amable, reservada; ASE; MED,RCL,CUR
""".strip().splitlines()

# Respawneables / genericos: nombre del grupo con placeholder de faccion; claves; tipo de lugar
RESPAWN = """
Guardia [facción]; disciplinado/a, alerta, leal; ASE
Guardia de puerta [ubicación]; aburrido/a, estricto/a; ASE
Patrulla [facción]; atento/a, leal; CAM
Soldado [facción]; disciplinado/a, obediente; MIL
Explorador [grupo]; curioso/a, ágil; CAM
Cazador [grupo]; callado/a, preciso/a; CAM
Saqueador [grupo]; bravucón/a, ruidoso/a; HOS
Bandido [grupo]; astuto/a, ágil; CAM
Mercenario [grupo]; frío/a, pragmático/a; HOS
Francotirador [grupo]; callado/a, paciente; HOS
Esclavista [grupo]; cruel, calculador/a; HOS
Cautivo [grupo]; asustado/a, digno/a; HOS
Cultista [grupo]; fanático/a, sereno/a; HOS
Capataz [grupo]; autoritario/a, cruel; HOS
Cobrador [grupo]; insistente, tenso/a; ASE
Pueblerino de [ubicación]; ocupado/a, sociable; ASE
Ciudadano de [ubicación]; ocupado/a, chismoso/a; ASE
Ocupante de [ubicación]; tranquilo/a, reservado/a; ASE
Trabajador de [ubicación]; cansado/a, trabajador/a; IND
Granjero de [ubicación]; terco/a, paciente; IND
Pastor de [ubicación]; callado/a, tranquilo/a; IND
Minero de [ubicación]; fuerte, silencioso/a; IND
Pescador de [ubicación]; alegre, supersticioso/a; PUE
Marinero de [ubicación]; ruidoso/a, valiente; PUE
Estibador de [ubicación]; fuerte, bromista; PUE
Vendedor ambulante de [ubicación]; hablador/a, astuto/a; COM
Comerciante de caravana [caravana]; práctico/a, cansado/a; CAM
Guardia de caravana [caravana]; leal, alerta; CAM
Peregrino [grupo]; sereno/a, resistente; CAM
Viajero [ubicación]; curioso/a, cansado/a; CAM
Mensajero [facción]; veloz, nervioso/a; CAM
Obrero de [ubicación]; trabajador/a, resignado/a; IND
Técnico de [facción]; ingenioso/a, impaciente; MIL
Médico de campo [facción]; práctico/a, cansado/a; MIL
Enfermero de [facción]; amable, incansable; MIL
Escriba de [facción]; metódico/a, distraído/a; MIL
Intendente de [facción]; ahorrativo/a, estricto/a; MIL
Vigía de [facción]; atento/a, callado/a; MIL
Recluta de [facción]; nervioso/a, entusiasta; MIL
Veterano de [facción]; cansado/a, honesto/a; MIL
Oficial de [facción]; severo/a, justo/a; MIL
Aprendiz de [oficio]; curioso/a, torpe; ASE
Artesano de [ubicación]; paciente, orgulloso/a; ASE
Tabernero de [ubicación]; cordial, atento/a; ASE
Cocinero de [ubicación]; alegre, mandón/a; ASE
Guardia de torre [facción]; estricto/a, aburrido/a; TOR
Huésped de [torre]; vanidoso/a, curioso/a; TOR
Sirviente de [torre]; amable, discreto/a; TOR
Excluido de [grupo]; resentido/a, digno/a; TOR
Habitante de [comunidad subterránea]; sociable, curioso/a; SUB
Vigía de [comunidad subterránea]; atento/a, nervioso/a; SUB
Guía de [comunidad subterránea]; ágil, callado/a; SUB
Robot de seguridad de [lugar]; estricto, literal; ESP
Robot servicial de [lugar]; amable, literal; ESP
Robot de mantenimiento de [lugar]; trabajador, literal; ESP
Dron explorador de [lugar]; veloz, curioso; ESP
Torreta de [lugar]; vigilante, literal; ESP
Superviviente de [ubicación]; desconfiado/a, ingenioso/a; CAM
Vagabundo de [ubicación]; simpático/a, desconfiado/a; CAM
Contrabandista de [grupo]; astuto/a, encantador/a; PUE
Pirata de [grupo]; bravucón/a, ágil; PUE
Pescador de [río o pantano]; callado/a, paciente; PUE
Barquero de [río o pantano]; hábil, callado/a; PUE
Cazador de pantano [grupo]; callado/a, resistente; CAM
Recolector de [ubicación]; ingenioso/a, ahorrativo/a; CAM
Curandero de [ubicación]; sabio/a, reservado/a; ASE
Sacerdote de [culto]; sereno/a, persuasivo/a; ASE
Peregrino de [culto]; fervoroso/a, resistente; CAM
Domador de [grupo]; paciente, rudo/a; HOS
Cuidador de [lugar]; atento/a, cálido/a; ASE
Voluntario de [facción]; entusiasta, nervioso/a; ASE
Delegado de [facción]; elocuente, calculador/a; ASE
Miembro de [grupo vecinal]; indignado/a, organizado/a; ASE
Miembro de [grupo de oficio]; orgulloso/a, trabajador/a; ASE
Vecino de [barrio]; sociable, chismoso/a; ASE
Anciano de [barrio]; sabio/a, nostálgico/a; ASE
Patrullero de [barrio]; atento/a, bromista; ASE
Repartidor de [ubicación]; veloz, simpático/a; ASE
Cuidador de ganado de [ubicación]; protector/a, callado/a; IND
Cazador furtivo de [grupo]; astuto/a, silencioso/a; CAM
Buscador de reliquias de [grupo]; aventurero/a, obsesivo/a; CAM
""".strip().splitlines()

# NINOS (todos `edad: niño`). Formato: rol; claves; grupo/lugar tipo; tipos de mision.
# En el lore cada uno recibe UN solo nombre (sin apellido ni apodo).
NINOS = """
niño/a de instalación subterránea; curioso/a, travieso/a, valiente; REF; REC,MSJ,FAM
niño/a amigo/a de la infancia; leal, bromista, sincero/a; REF; ESC,FAM,REC
niño/a matón con buen corazón; bravucón/a, leal, torpe; REF; AMN,DEF,FAM
niño/a líder de un grupo de amigos; carismático/a, mandón/a, protector/a; REF; BND,ESC
niño/a estudioso/a; brillante, tímido/a, ordenado/a; REF; ENS,INV,HCK
niño/a aprendiz de mecánico; ingenioso/a, manchado/a de grasa, entusiasta; REF; FAB,CON
niño/a aprendiz de curandero; sensible, atento/a, valiente; ASE; MED,RCL
niño/a recadero/a; veloz, hablador/a, astuto/a; ASE; MSJ,TRA
niño/a vendedor/a de periódicos o avisos; ruidoso/a, informado/a, simpático/a; ASE; MSJ,INV
niño/a de calle ingenioso/a; astuto/a, libre, generoso/a; ASE; INF,REC,DET
niño/a ladrón/a arrepentido/a; ágil, culposo/a, servicial; ASE; REC,INF
niño/a huérfano/a; sensible, protegido/a, valiente; ASE; FAM,REC
niño/a cocinero/a; creativo/a, goloso/a, mandón/a; ASE; RCL,FIE
niño/a pastor/a; callado/a, protector/a, tranquilo/a; IND; AMN,DOM
niño/a granjero/a; trabajador/a, curioso/a, risueño/a; IND; RCL,DEF
niño/a pescador/a; alegre, supersticioso/a, valiente; PUE; RCL,ESC
niño/a de puerto; aventurero/a, ruidoso/a, curioso/a; PUE; EXP,MSJ
niño/a grumete; obediente, soñador/a, valiente; PUE; ESC,EXP
niño/a vigía de torre; atento/a, callado/a, leal; MIL; VIG,MSJ
niño/a explorador/a de grupo; curioso/a, ágil, disciplinado/a; CAM; EXP,MAP,ESC
niño/a rastreador/a; paciente, observador/a, preciso/a; CAM; CAZ,DET
niño/a arquero/a de práctica; concentrado/a, orgulloso/a, tímido/a; CAM; CAZ,DEF
niño/a cartógrafo/a; meticuloso/a, soñador/a, curioso/a; CAM; MAP,EXP
niño/a guardia menor de grupo; serio/a, leal, nervioso/a; MIL; VIG,DEF
niño/a jefe de un grupo explorador; carismático/a, justo/a, valiente; CAM; BND,ESC,NEG
niño/a mensajero/a de grupo; veloz, hablador/a, nervioso/a; CAM; MSJ,TRA
niño/a sanador/a; amable, atento/a, incansable; ASE; MED,CUR
niño/a inventor/a; excéntrico/a, optimista, distraído/a; ASE; FAB,ART,CON
niño/a bibliotecario/a; erudito/a, silencioso/a, protector/a; ASE; REC,ENS
niño/a narrador/a de historias; carismático/a, soñador/a, fabulador/a; ASE; FIE,INV
niño/a músico/a; sensible, alegre, tímido/a; ASE; FIE,MSJ
niño/a que entrena animales; paciente, tierno/a, valiente; ESP; DOM,CAZ
niño/a que cuida un jardín; paciente, tierno/a, protector/a; ESP; RCL,DOM
niño/a de comunidad aislada; sociable, desconfiado/a, curioso/a; SUB; EXP,MSJ,NEG
niño/a alcalde/sa de comunidad subterránea; carismático/a, serio/a, ingenioso/a; SUB; NEG,DEF,BND
niño/a de seguridad de comunidad subterránea; estricto/a, leal, orgulloso/a; SUB; VIG,DEF
niño/a guía de túneles; ágil, callado/a, hábil; SUB; ESC,EXP
niño/a mendigo/a con historia; humilde, observador/a, bromista; SUB; INV,MSJ
niño/a que colecciona objetos; curioso/a, ahorrativo/a, soñador/a; SUB; REC,ART
niño/a vecino/a de un barrio; sociable, travieso/a, leal; ASE; AMN,FAM
niño/a campeón/a de un juego; competitivo/a, risueño/a, honesto/a; ASE; FIE
niño/a organizador/a de equipos; mandón/a, justo/a, entusiasta; ASE; FIE,NEG
niño/a mascota-cuidador/a; tierno/a, protector/a; ASE; DOM,FAM
niño/a mecánico/a de botes; hábil, práctico/a, bromista; PUE; FAB,CON
niño/a timonel; concentrado/a, orgulloso/a, valiente; PUE; ESC,EXP
niño/a capitán/a de un barco; carismático/a, valiente, justo/a; PUE; JEF,BND,ESC
niño/a navegante; soñador/a, preciso/a, curioso/a; PUE; MAP,EXP
niño/a pirata de tierra; bravucón/a, ingenioso/a, leal; ASE; BND,INF
niño/a contrabandista; astuto/a, encantador/a, nervioso/a; PUE; CTR,INF
niño/a de la gente del pantano; callado/a, resistente, curioso/a; CAM; RCL,CAZ
niño/a de los barcos del río; alegre, ágil, hablador/a; PUE; TRA,ESC
niño/a ladrón/a de ribera; ágil, astuto/a, generoso/a; PUE; INF,REC
niño/a que aprende un oficio; curioso/a, torpe, entusiasta; ASE; FAB,ENS
niño/a de caravana; viajero/a, curioso/a, cansado/a; CAM; TRA,MSJ
niño/a guardia de caravana; serio/a, leal, nervioso/a; CAM; ESC,DEF
niño/a médico/a de campo; práctico/a, amable, incansable; MIL; MED,CUR
niño/a escriba; metódico/a, tímido/a, perfeccionista; MIL; INV,MSJ
niño/a ayudante de cocina; alegre, goloso/a, trabajador/a; ASE; RCL,FIE
niño/a vendedor/a de rumores; chismoso/a, astuto/a, simpático/a; ASE; INV,MSJ
niño/a de familia comerciante; educado/a, regateador/a, curioso/a; COM; COM,TRA
niño/a que ayuda a su comunidad; generoso/a, entusiasta, leal; ASE; REC,DEF
niño/a perdido/a; asustado/a, agradecido/a, valiente; CAM; RSC,FAM
niño/a atrapado/a; ingenioso/a, asustado/a, digno/a; HOS; RSC
niño/a liberado/a de una banda; tímido/a, agradecido/a, valiente; HOS; FAM,REC
niño/a que sigue al protagonista; leal, entusiasta, bromista; ASE; ESC,FAM
niño/a científico/a; curioso/a, brillante, distraído/a; CIE; INV,HCK
niño/a de radio; hablador/a, nocturno/a, simpático/a; CIE; HCK,MSJ
niño/a dibujante; soñador/a, sensible, observador/a; ASE; MAP,FIE
niño/a que juega con robots; curioso/a, amable; ESP; ENS,HCK
niño/a tejedor/a; tranquilo/a, creativo/a; ASE; FAB,COM
niño/a de la tormenta; valiente, ruidoso/a, leal; CAM; ESC,DEF
niño/a vigilante de un puente; atento/a, serio/a, bromista; CAM; VIG,CON
niño/a de oasis; sereno/a, tierno/a, protector/a; ESP; RCL,DOM
niño/a de las alturas; ágil, silencioso/a, aventurero/a; CAM; EXP,CAZ
niño/a de campo; trabajador/a, risueño/a, honesto/a; IND; RCL,AMN
niño/a de la selva; curioso/a, ágil, respetuoso/a; CAM; EXP,CAZ
niño/a que repara juguetes; ingenioso/a, paciente, amable; ASE; FAB,REC
niño/a que enseña a leer; paciente, estudioso/a, cálido/a; ASE; ENS
niño/a rescatador/a; valiente, sensible, decidido/a; CAM; RSC,MED
niño/a de la fiesta; alegre, ruidoso/a, generoso/a; ASE; FIE
niño/a de la lluvia; soñador/a, tranquilo/a, sensible; CAM; PUZ,MSJ
niño/a que cuida el fuego; responsable, serio/a, protector/a; ASE; DEF,RCL
niño/a que juega a ser adulto; mandón/a, imaginativo/a, tierno/a; ASE; FIE,NEG
niño/a de los túneles; ágil, curioso/a, silencioso/a; SUB; EXP,RSC
niño/a de la biblioteca; silencioso/a, estudioso/a; ASE; REC,ENS
niño/a de la sal; trabajador/a, resistente, callado/a; PUE; RCL,TRA
niño/a de los faroles; atento/a, soñador/a, leal; PUE; VIG,MSJ
niño/a de los techos; ágil, bromista, libre; ASE; EXP,INF
niño/a de las barricadas; valiente, serio/a, decidido/a; ASE; DEF,BND
niño/a de las redes; hábil, alegre, paciente; PUE; RCL,ESC
""".strip().splitlines()

# COMPAÑEROS: solo femeninos (apariencia femenina) o niños. Formato: arquetipo; edad; personalidad larga.
# El lore les pone UN nombre (el que mejor los represente), sin apellido ni apodo.
COMPANEROS = """
perra leal de guardia (apariencia hembra); animal; Leal hasta el final, silenciosa y atenta. Detecta emboscadas antes que nadie, se interpone entre el grupo y el peligro y se ablanda con la comida y el cariño. Desconfía de los extraños y adora a quien la cuida. No habla; comunica con la mirada y el cuerpo.
cazadora de la región, veterana; adulto; Curtida, seria y de humor seco. Perdió a los suyos y encontró en el grupo un hogar que no admite. Cuando confía, se vuelve la más fiel y protectora; no tolera la crueldad contra los débiles.
guardia de caravana, bebedora de buen humor; adulto; Franca, jovial y ruidosa, con una historia de pérdidas que prefiere contar entre bromas. Detrás de la coraza hay una mujer que quiere un lugar al que volver.
chica de la facción científica, curiosa; adulto; Brillante, nerviosa, tozuda y con ganas de probarlo todo. Se disculpa al hablar y opina de todo. Pelea por convicción y crece cuando la tratan con respeto.
guerrera de orden, disciplinada; adulto; Seria, honorable, apegada a las normas, que descubre fuera de la orden otra forma de justicia. Respeta el rango, dice la verdad aunque duela y se ríe tarde y poco.
exploradora de frontera; adulto; Valiente, observadora y con una brújula interior. Vive en el camino y odia los edificios cerrados. Cuenta anécdotas de lugares que nadie vio.
médica ambulante; adulto; Paciente, práctica, de voz suave y manos firmes. Cura a quien lo necesite sin preguntar bando. Se enoja si hay violencia innecesaria.
mecánica de campo, ingeniosa; adulto; Impaciente, práctica y con grasa hasta el codo. Arregla lo imposible con alambres y mala palabra. Se pierde en detalles técnicos.
guía de supervivencia, mayor; adulto; Sabia, directa y de pocas palabras. Enseña con ejemplos y predice el clima por el dolor de rodillas.
domadora de criaturas; adulto; Tierna y firme, habla con los animales como si fueran personas. Cree que todo ser merece una segunda oportunidad.
cantante errante; adulto; Carismática, sensible y a veces ausente. Compone canciones sobre lo que ve y siente el ánimo del grupo mejor que nadie.
ex contrabandista, astuta; adulto; Rápida de palabra y de manos, siempre con una salida preparada. Aprendió a confiar poco, pero cuando lo hace, lo da todo.
sacerdotisa viajera; adulto; Serena, curiosa y de fe práctica. Escucha a todos, aconseja sin imponer y resuelve discusiones con una historia.
cartógrafa valiente; adulto; Meticulosa y soñadora; dibuja el mundo como lo ve y se pierde con gusto. Discute con el grupo por una línea mal hecha.
ex guardia de torre; adulto; Elegante, estricta y de ironía filosa. Descubre que lo que protegía no merecía su lealtad y busca algo mejor.
ladrona arrepentida; adulto; Ágil, culposa y generosa. Roba solo lo que necesita y se ofende si le piden mentir a los amigos.
robot de apoyo (apariencia a elección del lore); neutro; Literal, servicial y curioso. Aprende frases del grupo y las repite en mal momento. Se preocupa por las personas con cálculos cómicos.
comerciante viajera, pragmática; adulto; Charlatana, ahorrativa y de buen corazón. Convierte cualquier problema en un negocio, pero reparte las ganancias con el grupo.
campeona de torneos, humilde; adulto; Fuerte, noble y tímida fuera del campo. Entrena sin descanso y sueña con enseñar a otros.
niño amigo de la infancia, leal; niño; Bromista, sincero y valiente a su manera. Siempre dice lo que piensa, sigue al protagonista a todos lados y se alegra con cualquier descubrimiento.
niño explorador, entusiasta; niño; Disciplinado, ágil y optimista. Conoce los senderos del bosque, anota todo y se emociona con los mapas.
niño rastreador, callado; niño; Observador y paciente, habla poco y lee huellas como libros. Es leal y reservado.
niño inventor, distraído; niño; Excéntrico, entusiasta y despistado. Construye aparatos con restos y se emociona con cada idea.
niño sanador, amable; niño; Sensible, atento y valiente; no soporta ver sufrir a nadie y carga siempre vendas y hierbas.
niño recadero, veloz; niño; Hablador, astuto y siempre apurado; conoce atajos y chismes de todos los puntos del mapa.
niño líder de grupo, carismático; niño; Mandón, justo y protector. Organiza a todos y se hace cargo de los errores.
niño navegante, soñador; niño; Preciso, curioso y atento a las estrellas. Cuenta historias del mar y del río.
niño grumete, obediente; niño; Valiente, dispuesto y algo ingenuo; aprende rápido y se ofende si lo tratan de pequeño.
niña estudiosa, brillante; niño; Tímida, ordenada y sorprendentemente decidida. Sabe de plantas, mapas y bichos.
niña arquera, concentrada; niño; Orgullosa, seria y de puntería fina. Entrena sin descanso y se pone nerviosa cuando la miran.
niña pastora, protectora; niño; Callada, tierna y firme con los animales. Se enoja si alguien los maltrata.
niña mecánica de botes, ingeniosa; niño; Práctica, bromista y manchada de aceite; arregla todo con cuerda y paciencia.
""".strip().splitlines()
