from django.db import models


class Usuario(models.Model):

    ROLES = [
        ('jugador', 'Jugador'),
        ('entrenador', 'Entrenador'),
        ('administrador', 'Administrador'),
    ]

    nombre = models.CharField(max_length=100)

    apellido = models.CharField(max_length=100)

    dni = models.CharField(
        max_length=20,
        unique=True,
        null=True,
        blank=True
)

    fecha_nacimiento = models.DateField(
        null=True,
        blank=True
)

    email = models.EmailField(
    blank=True
    )



    telefono = models.CharField(
        max_length=20,
        blank=True
    )

    rol = models.CharField(
        max_length=20,
        choices=ROLES
    )

    foto = models.ImageField(
        upload_to='usuarios/',
        blank=True,
        null=True
    )

    categoria = models.CharField(
        max_length=20,
        blank=True
    )

    def __str__(self):
        return f"{self.nombre} {self.apellido}"
    
class Equipo(models.Model):

    nombre = models.CharField(
        max_length=100
    )

    deporte = models.CharField(
        max_length=100
    )

    categoria = models.CharField(
        max_length=100
    )

    entrenador = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='equipos_entrenados'
    )

    jugadores = models.ManyToManyField(
        Usuario,
        blank=True,
        related_name='equipos'
    )

    def __str__(self):
        return self.nombre


class Torneo(models.Model):
    nombre = models.CharField(max_length=150)
    deporte = models.CharField(max_length=100)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    descripcion = models.TextField()
    reglamento = models.TextField(blank=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre


class Inscripcion(models.Model):
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE
    )
    torneo = models.ForeignKey(
        Torneo,
        on_delete=models.CASCADE
    )
    fecha_inscripcion = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.usuario} - {self.torneo}"


class Evento(models.Model):
    titulo = models.CharField(max_length=150)
    descripcion = models.TextField()
    fecha = models.DateField()
    hora = models.TimeField()
    lugar = models.CharField(max_length=150)

    def __str__(self):
        return self.titulo


class Resultado(models.Model):
    evento = models.ForeignKey(
        Evento,
        on_delete=models.CASCADE
    )
    equipo_local = models.CharField(max_length=100)
    equipo_visitante = models.CharField(max_length=100)
    puntos_local = models.PositiveIntegerField(default=0)
    puntos_visitante = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.equipo_local} vs {self.equipo_visitante}"


class Notificacion(models.Model):
    titulo = models.CharField(max_length=150)
    mensaje = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)
    leida = models.BooleanField(default=False)

    def __str__(self):
        return self.titulo


class Mensaje(models.Model):
    remitente = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='mensajes_enviados'
    )
    destinatario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='mensajes_recibidos'
    )
    contenido = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.remitente} → {self.destinatario}"


class Comunicado(models.Model):
    titulo = models.CharField(max_length=150)
    contenido = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titulo