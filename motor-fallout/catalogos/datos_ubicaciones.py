"""Arquetipos de ubicaciones (mapa) y sucesos (cosas que hacer en un lugar)."""

# nombre generico; clase (S segura/N normal/H hostil); espacio (int/ext/mixto); palabras clave; contenedores tipicos; gente/criaturas tipicas
UBICACIONES = """
instalación subterránea de origen; S; int; refugio, comunidad, secreto; baúl, alacena, locker, terminal; vecinos, guardias, técnicos
instalación subterránea abandonada; N; int; oscuro, polvo, terminales; locker, caja fuerte, cajón; robots, insectos
asentamiento grande; S; mixto; población, comercio, descanso, seguridad; cajones, baúles, estantes; comerciantes, guardias, vecinos
asentamiento mediano; S; mixto; comunidad, mercado, oficios; cajones, estantes, buzones; vecinos, comerciantes
aldea pequeña; S; ext; granjas, vecinos, camino; alacena, arcón; granjeros, pastores
campamento de viajeros; S; ext; fogata, caravana, descanso; mochilas, cajas; viajeros, buhoneros
puesto de guardia; S; ext; vigilancia, peaje, litera; arsenal, cajón; guardias, soldados
torre habitada; S; int; lujo, tensión, comercio; vitrinas, cajas fuertes, roperos; huéspedes, guardias, gerentes
zona residencial abandonada; N; mixto; casas, cajones, ropero, ruinas; cajón, ropero, caja fuerte pequeña; saqueadores, animales
barrio destruido; N; ext; escombros, trampas, huecos; mochilas, cajas; saqueadores, insectos
supermercado en ruinas; H; int; góndolas, depósito, mercancía; góndolas, mostrador, caja fuerte; saqueadores, animales
tienda abandonada; N; int; mostrador, estantes, trastienda; mostrador, vitrina; animales, insectos
farmacia abandonada; N; int; medicinas, vitrinas, depósito; góndolas, cajón; saqueadores
hospital abandonado; H; int; camillas, quirófano, farmacia; botiquines, archivo; robots, saqueadores
escuela abandonada; N; int; aulas, biblioteca, pupitres; escritorios, estantes; animales
biblioteca en ruinas; N; int; libros, archivo, polvo; estantes, archivo; insectos
iglesia o templo; N; mixto; altar, bancos, cripta; altar, cofre; cultistas, vecinos
oficina o edificio gubernamental; N; int; terminales, archivo, sótano; escritorios, caja fuerte; robots, saqueadores
estación de tren o metro; N; int; túneles, andenes, vías; lockers, maletas; parásitos, slimes
túnel de transporte; H; int; oscuridad, humedad, conexiones; lockers, cajas; parásitos, slimes
central eléctrica; H; mixto; turbinas, terminales, trampas; tablero, locker; robots
planta de agua o purificación; N; int; bombas, tuberías, terminales; tablero, armario; robots, mutantes
planta industrial; H; int; maquinaria, depósitos, trampas; estantes, taquillas; robots
fábrica pequeña; N; int; talleres, cintas, herramientas; banco, caja; robots
depósito o almacén; N; int; cajas, estantes, vehículos; cajas, estantes; saqueadores, robots
base militar; H; mixto; armería, barracones, torres; arsenal, caja fuerte; soldados, torretas
puesto de vigilancia; H; ext; torre, catalejo, trampas; cajón, baúl; soldados
aeropuerto en ruinas; H; mixto; pistas, hangares, torres; maletas, lockers; saqueadores, animales
puente; N; ext; paso, cobertura, estructura; carro, caja; bandidos, animales
presa o represa; N; ext; compuertas, sala de control; tablero, caja; robots
mina; H; int; túneles, minerales, derrumbes; cajas, cofres; criaturas, mutantes
cantera; N; ext; roca, nidos, herramientas; caja de herramientas; insectos
granja; S; ext; corrales, cultivos, granero; arcón, alacena; granjeros, ganado
rancho de cría; N; ext; ganado, vallas, establo; arcón, corral; ganado, caninos
taller de mecánico; S; int; banco, herramientas, piezas; banco, cajón; mecánicos
torre de radio; N; mixto; antena, sala de control, escalera; consola, locker; técnicos
faro; S; mixto; luz, escaleras, vistas; cajón, baúl; vigías
museo; N; int; vitrinas, reliquias, sala de archivo; vitrinas, caja fuerte; robots
monumento o plaza; N; ext; estatuas, bancos, fuentes; pedestal, buzón; viajeros
cementerio; N; ext; tumbas, mausoleo, silencio; tumbas, cripta; criaturas, espíritus
prisión; H; int; celdas, guardias, archivos; celdas, caja fuerte; esclavistas, saqueadores
campamento esclavista; H; ext; jaulas, tiendas, capataz; jaulas, tienda; esclavistas, perros
campamento de saqueadores; H; ext; fogata, botín, trampas; cofre, tienda; saqueadores
guarida de criaturas; H; int; nido, huesos, restos; nido, restos; criaturas
cueva; N; int; oscuridad, goteo, murciélagos; grietas, nidos; criaturas
cañón; N; ext; estructura de roca, pasos, ecos; grietas, carros; criaturas
meseta; N; ext; vistas, viento, vegetación baja; piedras, cajas; caninos
valle fértil; S; ext; cultivos, arroyo, calma; cabaña, arcón; granjeros
oasis; S; ext; agua, sombra, descanso; alacena, cofre; viajeros
laguna; N; ext; agua turbia, juncos, bote; bote hundido; marinos blandos
pantano; N; ext; fango, niebla, plataformas; botes, cajas; parásitos, slimes
río; N; ext; orilla, botes, pasos; botes, cajas; marinos blandos
costa; N; ext; playa, rocas, naufragios; naufragio, caja; marinos blandos
muelle; S; ext; barcos, redes, puestos; cajas, redes; marineros, pescadores
barco anclado; N; int; camarotes, bodega, cubierta; baúl, bodega; piratas, marineros
barco hundido; N; int; bodega inundada, cofres, restos; cofres, bodega; marinos blandos
isla; N; ext; playa, selva, ruinas; cofres, cajas; criaturas
faro marítimo; S; mixto; luz, balcón, bote; baúl, cajón; vigías
mercado flotante; S; ext; botes, puestos, regateo; cajas, puestos; comerciantes
mercado del páramo; S; ext; puestos, caravanas, trueque; puestos, cajones; comerciantes
casino o salón de juegos; S; int; mesas, cantina, trastienda; caja fuerte, barra; crupieres, apostadores
taberna; S; int; barra, mesas, habitaciones; barra, cajón; taberneros, viajeros
posada; S; int; habitaciones, cocina, camas; cajón, baúl; posaderos
cantina oculta; N; int; secretos, mesas, contrabando; barra, caja; contrabandistas
tienda de mapas; N; int; mapas, instrumentos, estantes; estantes, cajón; cartógrafos
taller de inventor; N; int; prototipos, piezas, banco; banco, cajón; inventores
laboratorio; H; int; mesas, terminales, muestras; locker, caja fuerte; robots, mutantes
invernadero; S; int; plantas, agua, luz; macetas, caja; botánicos
jardín antiguo; S; ext; flores, estatuas, sendas; cofre, banco; cuidadores
comunidad aislada subterránea; S; int; reglas propias, túneles, joven espíritu; alacena, almacén; vecinos, guardias
refugio de grupo infantil; S; mixto; cabañas, fogata, banderas; baúl, alacena; niños, guías
campamento del bosque; S; ext; fogata, cabañas, mapas; baúl, alacena; exploradores
cabaña solitaria; N; int; cama, chimenea, baúl; baúl, alacena; ermitaños
claro del bosque; N; ext; hierba, luz, huellas; mochila, cofre; animales
bosque sagrado; N; ext; árboles viejos, altares, silencio; altar, cofre; espíritus, animales
árbol gigante habitado; S; mixto; escaleras, plataformas, puentes; baúl, alacena; vecinos
puente colgante; N; ext; cuerdas, vacío, viento; caja; animales
senda de montaña; N; ext; roca, nieve, pasos; piedra, mochila; caninos
paso estrecho; N; ext; desfiladero, emboscada, eco; carro, caja; bandidos
refugio de montaña; S; int; fuego, camas, provisiones; baúl, alacena; guías
mirador; N; ext; vistas, catalejo, banco; cofre; vigías
fuerte antiguo; H; mixto; murallas, patio, calabozo; arsenal, cofre; soldados
castillo en ruinas; H; mixto; torres, salón, sótano; cofres, armaduras; criaturas
aldea de bestias amistosas; S; ext; casas grandes, fogata, tótems; baúl, almacén; gigantes amistosos
territorio de criaturas alfa; N; ext; zona alta, boscosa, huellas; cofre, altar; alfas
campo de cultivo; S; ext; surcos, espantapájaros, herramientas; cobertizo, arcón; granjeros
molino; S; int; piedra, harina, rueda; arcón, cajón; molineros
establo comunal; S; int; animales, paja, herramientas; arcón; pastores
mercado del comercio; S; mixto; puestos, tinglados, trueque; puestos, cajones; comerciantes
barrio comercial; S; ext; locales, kioscos, calles; locales, buzones; comerciantes, vecinos
barrio residencial habitado; S; ext; casas, patios, veredas; buzones, patios; vecinos
barrio portuario; S; ext; tinglados, redes, tabernas; cajas, barriles; marineros
plaza principal; S; ext; fuente, bancos, kioscos; kioscos, bancos; vecinos
supermercado habitado; S; int; góndolas, cajas, depósito; góndolas, depósito; comerciantes
heladería o kiosco; S; int; mostrador, vitrina, heladera; mostrador, heladera; comerciantes
estanco o almacén de barrio; S; int; mostrador, estantes; mostrador, estantes; comerciantes
cuartel de la guardia; S; int; arsenal, celdas, oficina; arsenal, escritorio; guardias
muralla y puertas; S; ext; torres, peajes, guardias; torre, cajón; guardias
sótano de ciudad; H; int; túneles, alcantarillas, trampas; cajas; parásitos, slimes
alcantarilla; N; int; agua, túneles, tuberías; cajas; slimes, parásitos
tejados; N; ext; pasos estrechos, antenas, vistas; cajas; palomas, ladrones
callejón; N; ext; basura, escondites, huecos; tachos, cajas; ladrones
mercado negro; N; mixto; contrabando, sigilo, puestos; cajas, bolsas; contrabandistas
astillero; N; mixto; esqueletos de barcos, madera, grúas; cajas, estantes; marineros
selva densa; N; ext; vegetación cerrada, humedad, sonidos; mochila, cofre; insectos, animales
sendero de selva; N; ext; hojas, barro, raíces; mochila; animales
campamento del pantano; S; ext; palafitos, botes, redes; baúl, alacena; gente del pantano
palafito; S; int; madera, redes, chimenea; baúl, alacena; vecinos
bote o balsa; N; int; remos, bodega, vela; baúl; marineros
plataforma flotante; S; ext; puestos, redes, faroles; cajas; comerciantes
torre de vigía del río; N; mixto; catalejo, escaleras, señal; cajón; vigías
cascada; N; ext; agua, cueva detrás, rocío; roca; animales
ruina cubierta de vegetación; N; mixto; raíces, muros, huecos; cofre, caja; animales
templo oculto; H; int; altar, trampas, acertijos; altar, cofre; guardianes
cripta; H; int; sarcófagos, trampas, silencio; sarcófagos; no muertos
isla de los piratas; H; mixto; barcos, cuevas, tesoros; cofres, bodega; piratas
cueva del tesoro; H; int; cofres, trampas, eco; cofres; criaturas
""".strip().splitlines()

# (categoria, suceso, detalle)
SUCESOS = """
Descanso; dormir en una cama libre; recupera PV y quita fatiga (si es ajena, pedir permiso o delito)
Descanso; sentarse y esperar; avanza el tiempo en 1-8 h sin dormir
Descanso; cocinar en una fogata o cocina; mejora comidas y quita riesgo
Descanso; beber y llenar cantimplora; agua limpia o turbia
Descanso; lavarse; quita suciedad y algunos estados
Exploración; mirar el mapa del lugar; muestra cuadras vecinas conocidas
Exploración; subir a un mirador; revela cuadras lejanas
Exploración; escuchar a escondidas; pistas y rumores
Exploración; seguir rastros; revela criaturas o personas
Exploración; buscar una conexión oculta; garantía en la 4.ª búsqueda
Exploración; excavar con herramienta; recursos o reliquias
Exploración; trepar a un techo o árbol; vistas, atajos
Exploración; cruzar a nado; riesgo y objetos mojados
Exploración; seguir una senda; une dos cuadras
Registro; abrir cajón, ropero, caja o baúl; 05
Registro; forzar caja fuerte; 05
Registro; saquear un cadáver; contenedor con ID
Registro; leer notas y carteles; pistas y misiones
Registro; escuchar grabaciones; información
Registro; revisar vehículos y carros; piezas y recursos
Social; hablar con un NPC; diálogos por botones
Social; negociar un precio; tirada de CAR
Social; pedir que te siga; acompañante temporal
Social; compartir comida; sube relación
Social; contar un chiste o historia; relación pequeña
Social; intimidar o persuadir; tirada, consecuencias
Social; participar en un concurso; premios y XP
Social; apostar cuñas; juegos de azar (adultos)
Social; dar un regalo; sube amistad
Social; enseñar o aprender a leer; XP y pistas
Combate; emboscar a un enemigo desprevenido; golpe sigiloso
Combate; huir por un paso estrecho; 49
Combate; usar cobertura; reduce vulnerabilidad
Combate; poner una trampa; 33
Combate; defender un lugar; oleadas
Combate; rendirse; termina el combate con robo reducido
Técnica; hackear un terminal; INT
Técnica; reparar un dispositivo; INT
Técnica; fabricar en un banco; 46
Técnica; desactivar una trampa o mina; 33
Técnica; encender o apagar una máquina; interruptores y bombas
Técnica; sintonizar una radio; eventos y música
Técnica; usar un ascensor; con energía
Técnica; levantar una antena o puente; misión de construcción
Comercio; comprar y vender; 09, 46
Comercio; pedir un trabajo; tablones de misiones
Comercio; contratar un guía; viaje seguro
Comercio; alquilar una cama; 10 monedas
Comercio; vender rumores; relación y cuñas
Comercio; robar a un comerciante; 33
Criaturas; domar o calmar; CAR
Criaturas; cazar; carne y pieles
Criaturas; pescar; comida y recursos
Criaturas; recolectar plantas; medicinas
Criaturas; seguir a un guía animal; rastros
Criaturas; observar el choque entre especies; oportunidad
Mundo; ver amanecer o atardecer; evento de clima
Mundo; clima extremo; refugiarse
Mundo; encontrar un campamento de viajeros; descanso y comercio
Mundo; escuchar una historia en la fogata; misión o rumor
Mundo; encontrar una escena del pasado; nota, restos, pista
Mundo; evento aleatorio; 13
Mundo; fiesta del lugar; comida, música y XP
Mundo; mercado ambulante; comercio especial
Mundo; ritual o ceremonia; misión y ofrendas
Mundo; caída de una estructura; derrumbe y paso estrecho
Mundo; lluvia que llena un pozo; recurso de agua
Viaje; ir a la cuadra vecina; 47
Viaje; marcar en el mapa de muñeca; sin riesgo
Viaje; abrir el mapa grande; vulnerable
Viaje; viaje rápido; riesgo según zona
Viaje; usar un bote o balsa; tramos de agua
Viaje; usar una carreta o caravana; tramos largos
Viaje; cruzar un puente roto; paso estrecho o reparación
Viaje; esperar a la noche; sigilo +10
Hogar; guardar objetos en el baúl; almacén
Hogar; decorar o mejorar; moral y descanso
Hogar; recibir visitas; amigos del hogar
Hogar; defender de un asalto nocturno; 39
Hogar; salir por la ventana; 49
Moral; ayudar a un NPC sin recompensa; karma
Moral; dejar una ofrenda; karma
Moral; devolver lo robado; karma y relación
Moral; decidir quién tiene la razón; bandos
Moral; perdonar a un derrotado; relación
Moral; enterrar a un caído (solo adultos de misión); karma
""".strip().splitlines()
