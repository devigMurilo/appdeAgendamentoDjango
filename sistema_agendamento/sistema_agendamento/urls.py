from django.contrib import admin
from django.urls import include, path

app_name = 'sistema_agendamento'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('agendamentos.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
]
