from datetime import time
from .models import HorarioDisponivel

HORARIO_INICIO = 9
HORARIO_FIM = 19

def _horarios_barbearia():
    return [time(hora, 0) for hora in range(HORARIO_INICIO, HORARIO_FIM + 1)]

def _garantir_horarios_base():
    for hora in _horarios_barbearia():
        HorarioDisponivel.objects.get_or_create(horario=hora, defaults={'ativo': True})