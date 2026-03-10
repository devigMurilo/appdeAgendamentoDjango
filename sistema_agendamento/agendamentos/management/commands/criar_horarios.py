from django.core.management.base import BaseCommand
from agendamentos.utils import _garantir_horarios_base


class Command(BaseCommand):
    help = 'Garante que os horários base existem no banco'

    def handle(self, *args, **kwargs):
        _garantir_horarios_base()
        self.stdout.write(self.style.SUCCESS('Horários criados/verificados.'))