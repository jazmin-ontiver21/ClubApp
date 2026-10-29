from django.contrib import admin
from .models import (
    Usuario,
    Equipo,
    Torneo,
    Inscripcion,
    Evento,
    Resultado,
    Notificacion,
    Mensaje,
    Comunicado
)

admin.site.register(Usuario)
admin.site.register(Equipo)
admin.site.register(Torneo)
admin.site.register(Inscripcion)
admin.site.register(Evento)
admin.site.register(Resultado)
admin.site.register(Notificacion)
admin.site.register(Mensaje)
admin.site.register(Comunicado)