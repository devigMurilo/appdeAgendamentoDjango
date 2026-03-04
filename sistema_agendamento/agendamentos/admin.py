from django.contrib import admin

from .models import Agendamento, HorarioDisponivel, Perfil, Servico


@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'tipo_usuario')
    list_filter = ('tipo_usuario',)
    search_fields = ('usuario__username', 'usuario__first_name', 'usuario__last_name')


@admin.register(Servico)
class ServicoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'duracao', 'preco', 'ativo')
    list_filter = ('ativo',)
    search_fields = ('nome',)


@admin.register(HorarioDisponivel)
class HorarioDisponivelAdmin(admin.ModelAdmin):
    list_display = ('horario', 'ativo')
    list_filter = ('ativo',)


@admin.register(Agendamento)
class AgendamentoAdmin(admin.ModelAdmin):
    list_display = ('cliente', 'servico', 'data', 'horario_disponivel', 'status')
    list_filter = ('status', 'data', 'servico')
    search_fields = ('cliente__username', 'cliente__first_name', 'cliente__last_name')
