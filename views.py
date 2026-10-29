
from datetime import date, datetime

from django.shortcuts import render, redirect

from .models import (
    Torneo,
    Usuario,
    Evento,
    Resultado,
    Equipo,
)


# =========================================================
# CATEGORÍAS DE JUGADORES
# =========================================================

def calcular_categoria(fecha_nacimiento):
    hoy = date.today()
    edad = hoy.year - fecha_nacimiento.year

    if (hoy.month, hoy.day) < (
        fecha_nacimiento.month,
        fecha_nacimiento.day
    ):
        edad -= 1

    if edad <= 10:
        return 'Sub-10'
    elif edad <= 12:
        return 'Sub-12'
    elif edad <= 14:
        return 'Sub-14'
    elif edad <= 16:
        return 'Sub-16'
    elif edad <= 18:
        return 'Sub-18'
    else:
        return 'Mayores'


# =========================================================
# INICIO
# =========================================================

def inicio(request):
    return render(request, 'clubapp/inicio.html')


# =========================================================
# SELECCIÓN DE PERFIL
# =========================================================

def seleccionar_perfil(request):
    return render(request, 'clubapp/perfil.html')


def elegir_acceso(request, rol):
    perfiles = {
        'jugador': 'Jugador',
        'entrenador': 'Entrenador',
        'administrador': 'Administrador',
    }

    if rol not in perfiles:
        return redirect('seleccionar_perfil')

    # Guardar el perfil seleccionado.
    request.session['rol_elegido'] = rol

    return render(
        request,
        'clubapp/opciones_acceso.html',
        {
            'rol': rol,
            'nombre_perfil': perfiles[rol],
        }
    )


# =========================================================
# INICIAR SESIÓN
# =========================================================

def iniciar_sesion(request):
    rol_elegido = request.session.get('rol_elegido')

    # Si no se eligió un perfil, volver a seleccionarlo.
    if rol_elegido not in (
        'jugador',
        'entrenador',
        'administrador'
    ):
        return redirect('seleccionar_perfil')

    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        apellido = request.POST.get('apellido', '').strip()
        dni = request.POST.get('dni', '').strip()

        try:
            usuario = Usuario.objects.get(
                nombre__iexact=nombre,
                apellido__iexact=apellido,
                dni=dni
            )
        except Usuario.DoesNotExist:
            return render(
                request,
                'clubapp/inicio_sesion.html',
                {
                    'error': (
                        'Los datos ingresados no coinciden '
                        'con ningún usuario registrado.'
                    ),
                    'rol': rol_elegido,
                }
            )

        # Comprobar que la cuenta coincida con el perfil.
        if usuario.rol != rol_elegido:
            return render(
                request,
                'clubapp/inicio_sesion.html',
                {
                    'error': (
                        'Tu cuenta no corresponde al perfil '
                        'seleccionado. Volvé y elegí el correcto.'
                    ),
                    'rol': rol_elegido,
                }
            )

        # Clave compartida para todos los administradores.
        if usuario.rol == 'administrador':
            clave_administrador = request.POST.get(
                'clave_administrador',
                ''
            ).strip()

            if clave_administrador != '670':
                return render(
                    request,
                    'clubapp/inicio_sesion.html',
                    {
                        'error': (
                            'La contraseña de administrador '
                            'es incorrecta.'
                        ),
                        'rol': rol_elegido,
                    }
                )

        # Crear la sesión después de validar los datos.
        request.session['usuario_id'] = usuario.id
        request.session.pop('rol_elegido', None)

        if usuario.rol == 'jugador':
            return redirect('jugador')
        elif usuario.rol == 'entrenador':
            return redirect('entrenador')
        elif usuario.rol == 'administrador':
            return redirect('administrador')

        return redirect('inicio')

    return render(
        request,
        'clubapp/inicio_sesion.html',
        {'rol': rol_elegido}
    )


# =========================================================
# CERRAR SESIÓN
# =========================================================

def cerrar_sesion(request):
    request.session.flush()
    return redirect('inicio')


# =========================================================
# REGISTRO
# =========================================================

def registro(request):
    rol_elegido = request.session.get('rol_elegido')

    # No permitir registrarse sin elegir primero un perfil.
    if rol_elegido not in (
        'jugador',
        'entrenador',
        'administrador'
    ):
        return redirect('seleccionar_perfil')

    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        apellido = request.POST.get('apellido', '').strip()
        dni = request.POST.get('dni', '').strip()
        fecha_nacimiento = request.POST.get('fecha_nacimiento')

        # El perfil proviene de la sesión, no de un selector HTML.
        rol = rol_elegido

        if not nombre or not apellido or not dni:
            return render(
                request,
                'clubapp/registro.html',
                {
                    'error': 'Completá todos los campos obligatorios.',
                    'rol': rol,
                }
            )

        # Clave requerida al registrarse como administrador.
        if rol == 'administrador':
            clave_administrador = request.POST.get(
                'clave_administrador',
                ''
            ).strip()

            if clave_administrador != '670':
                return render(
                    request,
                    'clubapp/registro.html',
                    {
                        'error': (
                            'La clave de administrador es incorrecta.'
                        ),
                        'rol': rol,
                    }
                )

        # Evitar DNI duplicados.
        if Usuario.objects.filter(dni=dni).exists():
            return render(
                request,
                'clubapp/registro.html',
                {
                    'error': (
                        'Este DNI ya está registrado. '
                        'Probá iniciar sesión.'
                    ),
                    'rol': rol,
                }
            )

        # Validar la fecha de nacimiento.
        try:
            fecha_nacimiento_obj = datetime.strptime(
                fecha_nacimiento or '',
                '%Y-%m-%d'
            ).date()
        except (ValueError, TypeError):
            return render(
                request,
                'clubapp/registro.html',
                {
                    'error': 'La fecha de nacimiento no es válida.',
                    'rol': rol,
                }
            )

        if fecha_nacimiento_obj > date.today():
            return render(
                request,
                'clubapp/registro.html',
                {
                    'error': (
                        'La fecha de nacimiento no puede ser futura.'
                    ),
                    'rol': rol,
                }
            )

        # Calcular la categoría solamente para jugadores.
        categoria = ''

        if rol == 'jugador':
            categoria = calcular_categoria(
                fecha_nacimiento_obj
            )

        # Crear la cuenta.
        usuario = Usuario.objects.create(
            nombre=nombre,
            apellido=apellido,
            dni=dni,
            fecha_nacimiento=fecha_nacimiento_obj,
            rol=rol,
            categoria=categoria
        )

        request.session['usuario_id'] = usuario.id
        request.session.pop('rol_elegido', None)

        # Enviar al panel correspondiente.
        if usuario.rol == 'jugador':
            return redirect('jugador')
        elif usuario.rol == 'entrenador':
            return redirect('entrenador')
        elif usuario.rol == 'administrador':
            return redirect('administrador')

        return redirect('inicio')

    return render(
        request,
        'clubapp/registro.html',
        {'rol': rol_elegido}
    )


# =========================================================
# PANEL DEL JUGADOR
# =========================================================

def jugador(request):
    usuario_id = request.session.get('usuario_id')

    if not usuario_id:
        return redirect('inicio')

    try:
        usuario = Usuario.objects.get(id=usuario_id)
    except Usuario.DoesNotExist:
        request.session.flush()
        return redirect('inicio')

    if usuario.rol != 'jugador':
        return redirect('inicio')

    return render(
        request,
        'clubapp/jugador.html',
        {'usuario': usuario}
    )


# =========================================================
# PANEL DEL ENTRENADOR
# =========================================================

def entrenador(request):
    usuario_id = request.session.get('usuario_id')

    if not usuario_id:
        return redirect('inicio')

    try:
        usuario = Usuario.objects.get(id=usuario_id)
    except Usuario.DoesNotExist:
        request.session.flush()
        return redirect('inicio')

    if usuario.rol != 'entrenador':
        return redirect('inicio')

    equipos_entrenador = (
        Equipo.objects
        .filter(entrenador=usuario)
        .prefetch_related('jugadores')
        .order_by('nombre')
    )

    return render(
        request,
        'clubapp/entrenador.html',
        {
            'usuario': usuario,
            'equipos': equipos_entrenador,
        }
    )


# =========================================================
# PANEL DEL ADMINISTRADOR
# =========================================================

def administrador(request):
    usuario_id = request.session.get('usuario_id')

    if not usuario_id:
        return redirect('inicio')

    try:
        usuario = Usuario.objects.get(id=usuario_id)
    except Usuario.DoesNotExist:
        request.session.flush()
        return redirect('inicio')

    if usuario.rol != 'administrador':
        return redirect('inicio')

    return render(
        request,
        'clubapp/administrador.html',
        {'usuario': usuario}
    )


# =========================================================
# TORNEOS
# =========================================================

def torneos(request):
    lista_torneos = Torneo.objects.all()

    return render(
        request,
        'clubapp/torneos.html',
        {'torneos': lista_torneos}
    )


# =========================================================
# MI PERFIL
# =========================================================

def mi_perfil(request):
    usuario_id = request.session.get('usuario_id')

    if not usuario_id:
        return redirect('inicio')

    try:
        usuario = Usuario.objects.get(id=usuario_id)
    except Usuario.DoesNotExist:
        request.session.flush()
        return redirect('inicio')

    return render(
        request,
        'clubapp/perfil_usuario.html',
        {'usuario': usuario}
    )


# =========================================================
# EDITAR PERFIL
# =========================================================

def editar_perfil(request):
    usuario_id = request.session.get('usuario_id')

    if not usuario_id:
        return redirect('inicio')

    try:
        usuario = Usuario.objects.get(id=usuario_id)
    except Usuario.DoesNotExist:
        request.session.flush()
        return redirect('inicio')

    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        apellido = request.POST.get('apellido', '').strip()
        dni = request.POST.get('dni', '').strip()
        fecha_nacimiento = request.POST.get('fecha_nacimiento')

        if Usuario.objects.filter(dni=dni).exclude(
            id=usuario.id
        ).exists():
            return render(
                request,
                'clubapp/editar_perfil.html',
                {
                    'usuario': usuario,
                    'error': 'Ese DNI ya pertenece a otro usuario.',
                }
            )

        try:
            fecha_nacimiento_obj = datetime.strptime(
                fecha_nacimiento or '',
                '%Y-%m-%d'
            ).date()
        except (ValueError, TypeError):
            return render(
                request,
                'clubapp/editar_perfil.html',
                {
                    'usuario': usuario,
                    'error': 'La fecha de nacimiento no es válida.',
                }
            )

        if fecha_nacimiento_obj > date.today():
            return render(
                request,
                'clubapp/editar_perfil.html',
                {
                    'usuario': usuario,
                    'error': (
                        'La fecha de nacimiento no puede ser futura.'
                    ),
                }
            )

        usuario.nombre = nombre
        usuario.apellido = apellido
        usuario.dni = dni
        usuario.fecha_nacimiento = fecha_nacimiento_obj

        if usuario.rol == 'jugador':
            usuario.categoria = calcular_categoria(
                fecha_nacimiento_obj
            )

        usuario.save()
        return redirect('mi_perfil')

    return render(
        request,
        'clubapp/editar_perfil.html',
        {'usuario': usuario}
    )


# =========================================================
# CALENDARIO
# =========================================================

def calendario(request):
    usuario_id = request.session.get('usuario_id')

    if not usuario_id:
        return redirect('inicio')

    eventos = Evento.objects.all().order_by('fecha', 'hora')

    return render(
        request,
        'clubapp/calendario.html',
        {'eventos': eventos}
    )


# =========================================================
# NOTIFICACIONES
# =========================================================

def notificaciones(request):
    usuario_id = request.session.get('usuario_id')

    if not usuario_id:
        return redirect('inicio')

    from .models import Notificacion

    lista_notificaciones = (
        Notificacion.objects.all().order_by('-fecha')
    )

    return render(
        request,
        'clubapp/notificaciones.html',
        {'notificaciones': lista_notificaciones}
    )


# =========================================================
# RESULTADOS
# =========================================================

def resultados(request):
    usuario_id = request.session.get('usuario_id')

    if not usuario_id:
        return redirect('inicio')

    lista_resultados = (
        Resultado.objects
        .all()
        .order_by('-evento__fecha', '-evento__hora')
    )

    return render(
        request,
        'clubapp/resultados.html',
        {'resultados': lista_resultados}
    )


# =========================================================
# CHAT
# =========================================================

def chat(request):
    usuario_id = request.session.get('usuario_id')

    if not usuario_id:
        return redirect('inicio')

    try:
        usuario = Usuario.objects.get(id=usuario_id)
    except Usuario.DoesNotExist:
        request.session.flush()
        return redirect('inicio')

    from .models import Mensaje

    usuarios = (
        Usuario.objects
        .exclude(id=usuario.id)
        .order_by('apellido', 'nombre')
    )

    if request.method == 'POST':
        destinatario_id = request.POST.get('destinatario')
        contenido = request.POST.get('contenido', '').strip()

        if destinatario_id and contenido:
            try:
                destinatario = Usuario.objects.get(
                    id=destinatario_id
                )

                Mensaje.objects.create(
                    remitente=usuario,
                    destinatario=destinatario,
                    contenido=contenido
                )
            except Usuario.DoesNotExist:
                pass

            return redirect('chat')

    mensajes_recibidos = (
        Mensaje.objects
        .filter(destinatario=usuario)
        .order_by('-fecha')
    )

    mensajes_enviados = (
        Mensaje.objects
        .filter(remitente=usuario)
        .order_by('-fecha')
    )

    return render(
        request,
        'clubapp/chat.html',
        {
            'usuario': usuario,
            'usuarios': usuarios,
            'mensajes_recibidos': mensajes_recibidos,
            'mensajes_enviados': mensajes_enviados,
        }
    )


# =========================================================
# EQUIPOS
# =========================================================

def equipos(request):
    usuario_id = request.session.get('usuario_id')

    if not usuario_id:
        return redirect('inicio')

    lista_equipos = (
        Equipo.objects
        .prefetch_related('jugadores')
        .select_related('entrenador')
        .order_by('nombre')
    )

    return render(
        request,
        'clubapp/equipos.html',
        {'equipos': lista_equipos}
    )
