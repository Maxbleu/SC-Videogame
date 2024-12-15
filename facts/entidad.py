from experta import Fact
from experta import *

# Clase de hechos
class Entidad(Fact):
    tipo_entidad = Field(str)
    vidas = Field(int)
    accion = Field(str)
    posicion_x = Field(int)
    posicion_y = Field(int)