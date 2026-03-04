from django.urls import path

from . import views

app_name = 'agendamentos'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('cadastro/', views.RegistroUsuarioView.as_view(), name='register'),

    path('admin/dashboard/', views.DashboardAdminView.as_view(), name='dashboard_admin'),

    path('servicos/', views.ServicoListView.as_view(), name='servico_list'),
    path('servicos/novo/', views.ServicoCreateView.as_view(), name='servico_create'),
    path('servicos/<int:pk>/editar/', views.ServicoUpdateView.as_view(), name='servico_update'),
    path('servicos/<int:pk>/excluir/', views.ServicoDeleteView.as_view(), name='servico_delete'),

    path('horarios/', views.HorarioListView.as_view(), name='horario_list'),
    path('horarios/novo/', views.HorarioCreateView.as_view(), name='horario_create'),
    path('horarios/<int:pk>/editar/', views.HorarioUpdateView.as_view(), name='horario_update'),
    path('horarios/<int:pk>/excluir/', views.HorarioDeleteView.as_view(), name='horario_delete'),

    path('meus-agendamentos/', views.AgendamentoListClienteView.as_view(), name='agendamento_cliente_list'),
    path('meus-agendamentos/novo/', views.AgendamentoCreateView.as_view(), name='agendamento_create'),
    path('meus-agendamentos/<int:pk>/editar/', views.AgendamentoUpdateView.as_view(), name='agendamento_update'),
    path('meus-agendamentos/<int:pk>/cancelar/', views.AgendamentoCancelView.as_view(), name='agendamento_cancel'),

    path('agendamentos/', views.AgendamentoAdminListView.as_view(), name='agendamento_admin_list'),
    path('agendamentos/<int:pk>/status/', views.AgendamentoStatusUpdateView.as_view(), name='agendamento_status'),
]
