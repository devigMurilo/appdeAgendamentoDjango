from datetime import datetime, time, timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

User = get_user_model()


class Perfil(models.Model):
    TIPO_CLIENTE = 'CLIENTE'
    TIPO_ADMIN = 'ADMIN'
    TIPO_CHOICES = [
        (TIPO_CLIENTE, 'Cliente'),
        (TIPO_ADMIN, 'Administrador'),
    ]

    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    tipo_usuario = models.CharField(max_length=20, choices=TIPO_CHOICES, default=TIPO_CLIENTE)

    def __str__(self):
        return f'{self.usuario.username} - {self.get_tipo_usuario_display()}'


class Servico(models.Model):
    nome = models.CharField(max_length=120, unique=True)
    descricao = models.TextField(blank=True)
    duracao = models.PositiveIntegerField(help_text='Duração em minutos')
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    ativo = models.BooleanField(default=True)

    class Meta:
        ordering = ['nome']
        verbose_name = 'Serviço'
        verbose_name_plural = 'Serviços'

    def __str__(self):
        return self.nome


class HorarioDisponivel(models.Model):
    horario = models.TimeField(unique=True)
    ativo = models.BooleanField(default=True)

    class Meta:
        ordering = ['horario']
        verbose_name = 'Horário disponível'
        verbose_name_plural = 'Horários disponíveis'

    def __str__(self):
        return self.horario.strftime('%H:%M')


class Agendamento(models.Model):
    STATUS_PENDENTE = 'PENDENTE'
    STATUS_CONFIRMADO = 'CONFIRMADO'
    STATUS_CANCELADO = 'CANCELADO'
    STATUS_CONCLUIDO = 'CONCLUIDO'
    STATUS_CHOICES = [
        (STATUS_PENDENTE, 'Pendente'),
        (STATUS_CONFIRMADO, 'Confirmado'),
        (STATUS_CANCELADO, 'Cancelado'),
        (STATUS_CONCLUIDO, 'Concluído'),
    ]

    cliente = models.ForeignKey(User, on_delete=models.CASCADE, related_name='agendamentos')
    servico = models.ForeignKey(Servico, on_delete=models.PROTECT, related_name='agendamentos')
    horario_disponivel = models.ForeignKey(HorarioDisponivel, on_delete=models.PROTECT, related_name='agendamentos')
    data = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDENTE)
    observacao = models.TextField(blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-data', '-horario_disponivel__horario']
        verbose_name = 'Agendamento'
        verbose_name_plural = 'Agendamentos'
        constraints = [
            # Impede duplicidade de horário no mesmo dia para registros não cancelados.
            models.UniqueConstraint(
                fields=['data', 'horario_disponivel'],
                condition=~Q(status='CANCELADO'),
                name='unique_data_horario_ativo',
            )
        ]

    def __str__(self):
        return f'{self.cliente.username} - {self.servico.nome} - {self.data} {self.horario_disponivel}'

    def get_data_hora(self):
        return datetime.combine(self.data, self.horario_disponivel.horario)

    def can_cancel(self):
        if self.status in (self.STATUS_CANCELADO, self.STATUS_CONCLUIDO):
            return False
        # A janela mínima de cancelamento é configurável no settings.
        data_hora_agendamento = timezone.make_aware(self.get_data_hora(), timezone.get_current_timezone())
        limite = timezone.now() + timedelta(hours=settings.CANCELLATION_MIN_HOURS)
        return data_hora_agendamento >= limite

    def clean(self):
        super().clean()

        if self.data and self.data < timezone.localdate():
            raise ValidationError({'data': 'Não é permitido agendar em data passada.'})

        # weekday(): segunda=0 ... domingo=6
        if self.data and self.data.weekday() == 6:
            raise ValidationError({'data': 'A barbearia não funciona aos domingos.'})

        if self.horario_disponivel and not self.horario_disponivel.ativo:
            raise ValidationError({'horario_disponivel': 'Este horário não está disponível.'})

        # Regras de funcionamento: 09:00 às 19:00, intervalo de 1h.
        if self.horario_disponivel:
            hora = self.horario_disponivel.horario
            if hora < time(9, 0) or hora > time(19, 0) or hora.minute != 0:
                raise ValidationError({'horario_disponivel': 'Horário fora do funcionamento da barbearia.'})

        conflito = Agendamento.objects.filter(
            data=self.data,
            horario_disponivel=self.horario_disponivel,
        ).exclude(status=self.STATUS_CANCELADO)

        if self.pk:
            conflito = conflito.exclude(pk=self.pk)

        if conflito.exists():
            raise ValidationError({'horario_disponivel': 'Este horário já está ocupado para a data selecionada.'})

    def save(self, *args, **kwargs):
        # full_clean reforça validações também em cenários concorrentes.
        self.full_clean()
        super().save(*args, **kwargs)


@receiver(post_save, sender=User)
def criar_perfil_usuario(sender, instance, created, **kwargs):
    if created:
        tipo = Perfil.TIPO_ADMIN if (instance.is_staff or instance.is_superuser) else Perfil.TIPO_CLIENTE
        Perfil.objects.create(usuario=instance, tipo_usuario=tipo)
