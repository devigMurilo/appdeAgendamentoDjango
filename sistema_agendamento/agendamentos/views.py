from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Count, Q
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, TemplateView, UpdateView

from .forms import AgendamentoForm, AlterarStatusAgendamentoForm, RegistroUsuarioForm
from .models import Agendamento, HorarioDisponivel, Perfil, Servico


class PerfilMixin:
    def is_admin(self):
        return self.request.user.is_staff or (
            hasattr(self.request.user, 'perfil') and self.request.user.perfil.tipo_usuario == Perfil.TIPO_ADMIN
        )

    def is_cliente(self):
        return hasattr(self.request.user, 'perfil') and self.request.user.perfil.tipo_usuario == Perfil.TIPO_CLIENTE


class AdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin, PerfilMixin):
    def test_func(self):
        return self.is_admin()


class ClienteRequiredMixin(LoginRequiredMixin, UserPassesTestMixin, PerfilMixin):
    def test_func(self):
        return self.is_cliente()


class HomeView(TemplateView):
    template_name = 'agendamentos/home.html'


class RegistroUsuarioView(CreateView):
    form_class = RegistroUsuarioForm
    template_name = 'registration/register.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        messages.success(self.request, 'Cadastro realizado com sucesso. Faça login para continuar.')
        return super().form_valid(form)


class DashboardAdminView(AdminRequiredMixin, TemplateView):
    template_name = 'agendamentos/dashboard_admin.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_servicos'] = Servico.objects.count()
        context['total_horarios'] = HorarioDisponivel.objects.filter(ativo=True).count()
        context['total_agendamentos'] = Agendamento.objects.count()
        context['por_status'] = Agendamento.objects.values('status').annotate(total=Count('id')).order_by('status')
        return context


class ServicoListView(AdminRequiredMixin, ListView):
    model = Servico
    template_name = 'agendamentos/servico_list.html'
    context_object_name = 'servicos'
    paginate_by = 10


class ServicoCreateView(AdminRequiredMixin, CreateView):
    model = Servico
    fields = ('nome', 'descricao', 'duracao', 'preco', 'ativo')
    template_name = 'agendamentos/servico_form.html'
    success_url = reverse_lazy('agendamentos:servico_list')

    def form_valid(self, form):
        messages.success(self.request, 'Serviço criado com sucesso.')
        return super().form_valid(form)


class ServicoUpdateView(AdminRequiredMixin, UpdateView):
    model = Servico
    fields = ('nome', 'descricao', 'duracao', 'preco', 'ativo')
    template_name = 'agendamentos/servico_form.html'
    success_url = reverse_lazy('agendamentos:servico_list')

    def form_valid(self, form):
        messages.success(self.request, 'Serviço atualizado com sucesso.')
        return super().form_valid(form)


class ServicoDeleteView(AdminRequiredMixin, DeleteView):
    model = Servico
    template_name = 'agendamentos/confirm_delete.html'
    success_url = reverse_lazy('agendamentos:servico_list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Serviço removido com sucesso.')
        return super().delete(request, *args, **kwargs)


class HorarioListView(AdminRequiredMixin, ListView):
    model = HorarioDisponivel
    template_name = 'agendamentos/horario_list.html'
    context_object_name = 'horarios'
    paginate_by = 10


class HorarioCreateView(AdminRequiredMixin, CreateView):
    model = HorarioDisponivel
    fields = ('horario', 'ativo')
    template_name = 'agendamentos/horario_form.html'
    success_url = reverse_lazy('agendamentos:horario_list')

    def form_valid(self, form):
        messages.success(self.request, 'Horário criado com sucesso.')
        return super().form_valid(form)


class HorarioUpdateView(AdminRequiredMixin, UpdateView):
    model = HorarioDisponivel
    fields = ('horario', 'ativo')
    template_name = 'agendamentos/horario_form.html'
    success_url = reverse_lazy('agendamentos:horario_list')

    def form_valid(self, form):
        messages.success(self.request, 'Horário atualizado com sucesso.')
        return super().form_valid(form)


class HorarioDeleteView(AdminRequiredMixin, DeleteView):
    model = HorarioDisponivel
    template_name = 'agendamentos/confirm_delete.html'
    success_url = reverse_lazy('agendamentos:horario_list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Horário removido com sucesso.')
        return super().delete(request, *args, **kwargs)


class AgendamentoListClienteView(ClienteRequiredMixin, ListView):
    model = Agendamento
    template_name = 'agendamentos/agendamento_cliente_list.html'
    context_object_name = 'agendamentos'
    paginate_by = 10

    def get_queryset(self):
        return Agendamento.objects.select_related('servico', 'horario_disponivel').filter(cliente=self.request.user)


class AgendamentoCreateView(ClienteRequiredMixin, CreateView):
    model = Agendamento
    form_class = AgendamentoForm
    template_name = 'agendamentos/agendamento_form.html'
    success_url = reverse_lazy('agendamentos:agendamento_cliente_list')

    def form_valid(self, form):
        form.instance.cliente = self.request.user
        messages.success(self.request, 'Agendamento criado com sucesso.')
        return super().form_valid(form)


class AgendamentoUpdateView(ClienteRequiredMixin, UpdateView):
    model = Agendamento
    form_class = AgendamentoForm
    template_name = 'agendamentos/agendamento_form.html'
    success_url = reverse_lazy('agendamentos:agendamento_cliente_list')

    def get_queryset(self):
        return Agendamento.objects.filter(cliente=self.request.user)

    def dispatch(self, request, *args, **kwargs):
        agendamento = self.get_object()
        if agendamento.status != Agendamento.STATUS_PENDENTE:
            messages.error(request, 'Apenas agendamentos pendentes podem ser editados.')
            return redirect('agendamentos:agendamento_cliente_list')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, 'Agendamento atualizado com sucesso.')
        return super().form_valid(form)


class AgendamentoCancelView(ClienteRequiredMixin, DeleteView):
    model = Agendamento
    template_name = 'agendamentos/confirm_delete.html'
    success_url = reverse_lazy('agendamentos:agendamento_cliente_list')

    def get_queryset(self):
        return Agendamento.objects.filter(cliente=self.request.user)

    def post(self, request, *args, **kwargs):
        agendamento = self.get_object()
        if not agendamento.can_cancel():
            messages.error(request, 'Não é possível cancelar dentro da janela mínima de antecedência.')
            return redirect('agendamentos:agendamento_cliente_list')

        # Em vez de remover o registro, cancelamos para manter histórico.
        agendamento.status = Agendamento.STATUS_CANCELADO
        agendamento.save(update_fields=['status', 'atualizado_em'])
        messages.success(request, 'Agendamento cancelado com sucesso.')
        return redirect(self.success_url)


class AgendamentoAdminListView(AdminRequiredMixin, ListView):
    model = Agendamento
    template_name = 'agendamentos/agendamento_admin_list.html'
    context_object_name = 'agendamentos'
    paginate_by = 12

    def get_queryset(self):
        queryset = Agendamento.objects.select_related('cliente', 'servico', 'horario_disponivel')
        data = self.request.GET.get('data')
        busca = self.request.GET.get('q')

        if data:
            queryset = queryset.filter(data=data)

        if busca:
            queryset = queryset.filter(
                Q(cliente__first_name__icontains=busca)
                | Q(cliente__last_name__icontains=busca)
                | Q(cliente__username__icontains=busca)
            )

        return queryset


class AgendamentoStatusUpdateView(AdminRequiredMixin, UpdateView):
    model = Agendamento
    form_class = AlterarStatusAgendamentoForm
    template_name = 'agendamentos/agendamento_status_form.html'

    def get_success_url(self):
        return reverse('agendamentos:agendamento_admin_list')

    def form_valid(self, form):
        messages.success(self.request, 'Status do agendamento atualizado com sucesso.')
        return super().form_valid(form)
