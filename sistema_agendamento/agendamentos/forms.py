from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone

from .models import Agendamento, Perfil


class RegistroUsuarioForm(UserCreationForm):
    email = forms.EmailField(required=True)
    tipo_usuario = forms.ChoiceField(choices=Perfil.TIPO_CHOICES)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'tipo_usuario', 'password1', 'password2')

    def save(self, commit=True):
        usuario = super().save(commit=False)
        usuario.email = self.cleaned_data['email']
        tipo_usuario = self.cleaned_data['tipo_usuario']
        if tipo_usuario == Perfil.TIPO_ADMIN:
            usuario.is_staff = True
        if commit:
            usuario.save()
            usuario.perfil.tipo_usuario = tipo_usuario
            usuario.perfil.save(update_fields=['tipo_usuario'])
        return usuario


class AgendamentoForm(forms.ModelForm):
    class Meta:
        model = Agendamento
        fields = ('servico', 'data', 'horario_disponivel', 'observacao')
        widgets = {
            'data': forms.DateInput(attrs={'type': 'date'}),
            'observacao': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['data'].widget.attrs['min'] = timezone.localdate().isoformat()
        self.fields['horario_disponivel'].queryset = self.fields['horario_disponivel'].queryset.filter(ativo=True)
        self.fields['servico'].queryset = self.fields['servico'].queryset.filter(ativo=True)

    def clean_data(self):
        data = self.cleaned_data.get('data')
        if data and data < timezone.localdate():
            raise ValidationError('Não é permitido selecionar datas passadas.')
        if data and data.weekday() == 6:
            raise ValidationError('A barbearia não funciona aos domingos.')
        return data  # ← retorna data, não cleaned_data

    def clean(self):
        cleaned_data = super().clean()
        data = cleaned_data.get('data')
        horario = cleaned_data.get('horario_disponivel')
        if data and horario:
            conflito = Agendamento.objects.filter(
                data=data,
                horario_disponivel=horario,
            ).exclude(status=Agendamento.STATUS_CANCELADO)
            if self.instance.pk:
                conflito = conflito.exclude(pk=self.instance.pk)
            if conflito.exists():
                self.add_error(
                    'horario_disponivel',
                    'Este horário já está ocupado para a data selecionada.'
                )
        return cleaned_data  # ← retorna cleaned_data, não data


class AlterarStatusAgendamentoForm(forms.ModelForm):
    class Meta:
        model = Agendamento
        fields = ('status',)
