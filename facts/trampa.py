from experta import Fact
from experta import *

class Trampa(Fact):
    tipo = Field(str)
    posicion_x = Field(int)
    posicion_y = Field(int)
    no_ha_sido_activada = Field(bool, default=True)