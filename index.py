from facts.trampa import Trampa
from facts.entidad import Entidad

from experta import *
from experta import KnowledgeEngine, Rule
from random import choice
import random


class EjecucionJuego(KnowledgeEngine):

    # No he podido encontrar ninguna propiedad existente dentro de las
    # clases que hay en la libreria de experta que almacene todas las reglas
    # que se han ejecutado, solo he podido encontrar lo siguiente:

        # get_rules() -> Que te devuelve todas las reglas cargadas en el motor

        # "get_activations()" -> Devuelve en tiempo de ejecucción la regla que se va a activar
        # Si en alguna regla tu pones self.get_activations() te devolverá la regla que se
        # ejecutará posteriormente y se para, simplmente no continua la ejecucción.

        # "get_next()" y "activations" campo de la clase agenda no los he conseguido
        # poner a funcionar siempre me devuelven un arreglo vacio "[]".

    # Puedes verlo tu mismo si descomentas la última línea de código del método
    # siguiente_movimiento.
    # ¿Porqué aquí? Simplemente porque es el mejor lugar donde puedes ver si
    # hay una siguiente acción cargada.

    # Asique he optado por dar una nueva implementación creando una nueva lista
    # donde almacenaré las reglas que se ejecutarán

    # En la inicialización del propio motor
    # crearemos una lista para almacenar
    # las reglas que se ejecutarán
    def __init__(self):
        super().__init__()
        self.activations_rules = []

    # Definimos las entidades del jugador y el monstruo antes
    # de su spawn
    @DefFacts()
    def inicializacion(self):
        yield Entidad(tipo_entidad = "jugador", accion = "spawn", vidas = 3, posicion_x = 0, posicion_y = 0)
        yield Entidad(tipo_entidad = "monstruo", accion = "spawn", vidas = 3, posicion_x = 0, posicion_y = 0)
        yield Trampa(tipo="trampa", posicion_x=random.randint(0,1), posicion_y=random.randint(0,1), no_ha_sido_activada=True)
        print("INICIA EL JUEGO")


    # JUGADOR

    # ----------------------------------------------------------------------------

    # 2. ACTIVACIÓN DE REGLAS A PARTIR DE LA MODIFICACIÓN DE HECHOS

    # Esta regla se ejecutará únicamente al principio del programa
    # para que el jugador haga spawn y podemos asignarle un acción
    # inicial
    @Rule(Entidad(tipo_entidad="jugador", accion = "spawn"),
        AS.jugador << Entidad(tipo_entidad = "jugador"), salience=1)
    def spawn_jugador(self, jugador):
        self.modify(jugador, accion="siguiente_movimiento")
        print(f"PLY: El jugador ha hecho spawn en las coordenadas {0},{0}")
        self.activations_rules.append("spawn_jugador")

    # Esta regla se activará por el método spawn_jugador debido
    # a la modificación de la propiedad accion del hecho jugador
    # indicando que el valor de la propiedad accion pasará a ser
    # siguiente_movimiento, haciendo que en la siguiente evaluación
    # de las reglas se active esta.

    # Esta regla se ejecutará cuando el jugador acabe de realizar una acción
    # asignandole una acción aleotoria a realizar posteriormente
    @Rule(Entidad(tipo_entidad="jugador", accion="siguiente_movimiento"),
            AS.jugador << Entidad(tipo_entidad = "jugador"))
    def siguiente_movimiento_jugador(self, jugador):
        ACCIONES_PRIMARIAS = ["atacar", "caminar", "correr"]
        self.accion = choice(ACCIONES_PRIMARIAS)
        self.modify(jugador, accion = self.accion)
        #print(self.get_activations())                          <------------------
        self.activations_rules.append("siguiente_movimiento_jugador")


    # ----------------------------------------------------------------------------



    # ----------------------------------------------------------------------------

    # 1. HECHOS MODIFICADOS A PARTIR DE REGLAS

    # A lo largo de la ejecucción en casí cada una de las reglas modificamos
    # las propiedades de los hechos pero esta en particular es donde más resalta.

    # En esta acción si el monstruo no está en rango o lo está se modificará
    # la acción o vidas del monstruo y al final también se modificará la
    # acción del jugador.

    # Esta regla se ejecutará cuando la acción de la entidad jugador es atacar
    # desde cualquier punto si se activa esta regla el monstruo perderá una vida
    # En caso de que el monstruo no esté en el área del jugador llamará la atención
    # del monstruo y lo matará de un golpe
    @Rule(Entidad(tipo_entidad="jugador", accion="atacar", posicion_x = MATCH.posicion_x_jugador, posicion_y = MATCH.posicion_y_jugador),
        Entidad(tipo_entidad="monstruo", vidas=MATCH.vidas_monstruo, posicion_x = MATCH.posicion_x_monstruo, posicion_y = MATCH.posicion_y_monstruo),
        AS.monstruo << Entidad(tipo_entidad="monstruo"),
        AS.jugador << Entidad(tipo_entidad="jugador"))
    def atacar_jugador(self, monstruo, jugador, vidas_monstruo, posicion_x_monstruo, posicion_y_monstruo, posicion_x_jugador, posicion_y_jugador):
        rango = 2
        if abs(posicion_x_monstruo - posicion_x_jugador) <= rango and abs(posicion_y_monstruo - posicion_y_jugador) <= rango:
            vidas_monstruo = vidas_monstruo - 1
            self.modify(monstruo, vidas = vidas_monstruo)
            print(f"PLY: El jugador ha atacado al monstruo. Vidas monstruo {vidas_monstruo}")
        else:
            self.modify(monstruo, accion = "correr_monstruo_al_jugador")
            print("PLY: El jugador ha atacado al aire. ¡El monstruo sabe donde estas!")
        self.modify(jugador, accion = "siguiente_movimiento")
        self.activations_rules.append("atacar_jugador")

    # ----------------------------------------------------------------------------



    # Esta regla solo se ejecutará cuando la acción de la entidad jugador es correr
    # indicando también que el monstruo también correrá hacia el jugador
    @Rule(Entidad(tipo_entidad="jugador", accion="correr"),
        AS.jugador << Entidad(tipo_entidad = "jugador"),
        AS.monstruo << Entidad(tipo_entidad = "monstruo"))
    def correr_jugador(self, jugador, monstruo):
        posicion_x = random.randint(7, 10)
        posicion_y = random.randint(7, 10)
        self.modify(jugador, accion = "siguiente_movimiento", posicion_x = posicion_x, posicion_y = posicion_y)
        print(f"PLY: El jugador ha corrido a las coordenadas {posicion_x}:{posicion_y}")
        self.modify(monstruo, accion = "correr_monstruo_al_jugador")
        self.activations_rules.append("correr_jugador")



    # ----------------------------------------------------------------------------

    # 3. ACTIVACIÓN DE DOS REGLAS DE MANERA SIMULTANEA

    # Estas dos reglas se activan simultaneamente ya que, las dos se activan
    # cuando la entidad tipo jugador tiene asignada la acción caminar

    # Esta regla se ejecutará cuando el jugador tenga la
    # acción de caminar primero comprobará si la trampa se
    # activa.
    @Rule(Entidad(tipo_entidad="jugador", accion="caminar", posicion_x=MATCH.posicion_x_jugador, posicion_y=MATCH.posicion_y_jugador, vidas=MATCH.vidas_jugador),
        AS.jugador << Entidad(tipo_entidad = "jugador"),
        Trampa(no_ha_sido_activada=True, posicion_x=MATCH.posicion_x_trampa, posicion_y=MATCH.posicion_y_trampa),
        AS.trampa << Trampa(tipo="trampa"), salience=2)
    def activar_trampa(self, jugador, posicion_x_jugador, posicion_y_jugador, vidas_jugador, trampa, posicion_x_trampa, posicion_y_trampa):
        if posicion_x_jugador == posicion_x_trampa and posicion_y_jugador == posicion_y_trampa:
            vidas_jugador = vidas_jugador - 1
            self.modify(jugador, vidas=vidas_jugador)
            print(f"PLY: El jugador cayó en una trampa en la posición {posicion_x_jugador}:{posicion_y_jugador}. Vidas restantes: {vidas_jugador}")
            self.modify(trampa, no_ha_sido_activada = False)
        self.activations_rules.append("activar_trampa")


    # Esta regla solo se ejecutará cuando la acción de la entidad jugador es caminar
    # indicando también al monstruo que también realizará la acción de caminar posteriormente
    @Rule(Entidad(tipo_entidad="jugador", accion = "caminar"),
        AS.jugador << Entidad(tipo_entidad = "jugador"),
        AS.monstruo << Entidad(tipo_entidad = "monstruo"))
    def caminar_jugador(self, jugador, monstruo):
        posicion_x_jugador = random.randint(1,3)
        posicion_y_jugador = random.randint(1,3)
        self.modify(jugador, accion = "siguiente_movimiento", posicion_x = posicion_x_jugador, posicion_y = posicion_y_jugador)
        print(f"PLY: El jugador ha caminado a las coordenadas {posicion_x_jugador}:{posicion_y_jugador}")
        self.modify(monstruo, accion = "caminar")
        self.activations_rules.append("caminar_jugador")

    # ----------------------------------------------------------------------------



    # Esta regla se ejecutará cuando las vidas del jugador
    # sea igual a cero teniendo una prioridad de 1
    @Rule(Entidad(tipo_entidad="jugador", vidas=0), salience=3)
    def jugador_muerto(self):
        print("PLY: El jugador ha muerto. ¡El monstruo ha ganado!")
        self.halt()

    # MONSTRUO

    # Esta regla se ejecutará únicamente al principio del programa
    # para que el monstruo haga spawn en una posición random del mapa
    # quedando a la espera de las acciones del jugador
    @Rule(Entidad(tipo_entidad="monstruo", accion = "spawn"),
        AS.monstruo << Entidad(tipo_entidad = "monstruo"), salience=1)
    def spawn_monstruo(self, monstruo):
        posicion_x = random.randint(4, 7)
        posicion_y = random.randint(4, 7)
        self.modify(monstruo, accion="esperar_movimiento_jugador", posicion_x = posicion_x, posicion_y = posicion_y)
        print(f"MOS: El monstruo ha hecho spawn en las coordenadas {posicion_x}:{posicion_y}")
        self.activations_rules.append("spawn_monstruo")

    # Esta regla solo se ejecutará cuando la acción de la entidad jugador es correr
    # indicando que el monstruo correrá hacia la posición del jugador he indicando
    # que la siguiente acción del monstruo es matar al jugador de un golpe
    @Rule(Entidad(tipo_entidad="monstruo", accion="correr_monstruo_al_jugador"),
        Entidad(tipo_entidad="jugador",posicion_x=MATCH.posicion_x_jugador, posicion_y=MATCH.posicion_y_jugador),
        AS.monstruo << Entidad(tipo_entidad = "monstruo"))
    def correr_monstruo_al_jugador(self, monstruo, posicion_x_jugador, posicion_y_jugador):
        self.modify(monstruo, accion = "one_shot_monstruo_al_jugador", posicion_x = posicion_x_jugador, posicion_y = posicion_y_jugador)
        print(f"MOS: El mostruo ha corrido hasta la posición del jugador")
        self.activations_rules.append("correr_monstruo_al_jugador")

    # Esta regla se ejecutará cuando el jugador camine por el mapa y
    # posteriormente perderá una vida.
    @Rule(Entidad(tipo_entidad="monstruo", accion = "caminar", vidas=MATCH.vidas),
            AS.monstruo << Entidad(tipo_entidad = "monstruo"))
    def caminar_monstruo(self, monstruo, vidas):
        posicion_x = random.randint(1,3)
        posicion_y = random.randint(1,3)
        vidas = vidas - 1
        self.modify(monstruo, accion = "esperar_movimiento_jugador", vidas = vidas, posicion_x = posicion_x, posicion_y = posicion_y)
        print(f"MOS: El monstruo ha caminado a las coordenadas {posicion_x}:{posicion_y}. Vidas restantes {vidas}")
        self.activations_rules.append("caminar_monstruo")

    # Esta regla solo se ejecutará cuando la acción de la entidad monstruo es one_shot_monstruo_al_jugador
    # haciendo que el jugador muera con un solo golpe del monstruo acabando el juego
    @Rule(Entidad(tipo_entidad="monstruo", accion="one_shot_monstruo_al_jugador"),
        AS.jugador << Entidad(tipo_entidad = "jugador"))
    def one_shot_monstruo_al_jugador(self, jugador):
        self.modify(jugador, vidas = 0)
        print("MOS: El jugador ha sido ONE SHOTEADO por el monstruo.")
        self.activations_rules.append("one_shot_monstruo_al_jugador")

    # Esta regla se ejecutará cuando las vidas del monstruo
    # sea igual a cero teniendo una prioridad de 1
    @Rule(Entidad(tipo_entidad="monstruo", vidas=0), salience=3)
    def monstruo_muerto(self):
        print("MOS: El monstruo ha muerto. ¡El jugador ha ganado!")
        self.halt()

engine = EjecucionJuego()
engine.reset()
engine.run()