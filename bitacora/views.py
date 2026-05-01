from datetime import date, datetime
from functools import wraps

from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from .forms import LoginForm, UsuarioForm
from .models import Registro, Usuario


# ─── Máquinas por área ────────────────────────────────────────────────────────

MAQUINAS_EXT = [
    'CHYI YANG A', 'CHYI YANG B', 'CHYI YANG C', 'CHYI YANG D',
    'RULLY', 'HYPLAS', 'LUNG MENG-1', 'LUNG MENG-2',
]

MAQUINAS_IMP = [
    'FLEXO TECH', 'LUNG MENG IMPRESIÓN',
]

MAQUINAS_CON = [
    'ROAN', 'LIBERTY', 'WICKETTER',
    'SING SIANG - 1', 'SING SIANG - 2',
    'CHYI YANG SF', 'LUNG MENG SF', 'HYPLASC',
    'UNFOLDING MACHINE', 'T-SHIRT',
]


# ─── Helpers de sesión ────────────────────────────────────────────────────────

def get_usuario(request):
    uid = request.session.get('usuario_id')
    if uid:
        try:
            return Usuario.objects.get(pk=uid, activo=True)
        except Usuario.DoesNotExist:
            request.session.flush()
    return None


def login_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not get_usuario(request):
            return redirect('bitacora:login')
        return view_func(request, *args, **kwargs)
    return wrapper


def admin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        usuario = get_usuario(request)
        if not usuario:
            return redirect('bitacora:login')
        if not usuario.is_admin:
            messages.error(request, 'No tienes permiso para acceder a esa página.')
            return redirect('bitacora:extrusion')
        return view_func(request, *args, **kwargs)
    return wrapper


def turno_actual():
    hora = timezone.localtime().hour
    if 6 <= hora < 14:
        return 'A'
    if 14 <= hora < 22:
        return 'B'
    return 'C'


def contexto_base(request):
    """Contexto compartido para todas las vistas protegidas."""
    usuario = get_usuario(request)
    return {
        'current_user': usuario,
        'turno_actual': turno_actual(),
        'fecha_hoy': date.today().isoformat(),
        'hora_ahora': timezone.localtime().strftime('%H:%M'),
        'auditores': list(
            Usuario.objects.filter(activo=True, rol__in=['Auditor', 'Administrador'])
            .values_list('nombre', flat=True)
        ),
        'supervisores': list(
            Usuario.objects.filter(activo=True, rol='Supervisor')
            .values_list('nombre', flat=True)
        ),
    }


# ─── Parseo de filas de tabla desde POST ─────────────────────────────────────

def _parse_rows(post, campos):
    """
    Lee filas enviadas como row_0_campo, row_1_campo, ...
    Devuelve lista de dicts.
    """
    rows = []
    i = 0
    while f'row_{i}_{campos[0]}' in post:
        fila = {}
        for campo in campos:
            fila[campo] = post.get(f'row_{i}_{campo}', '').strip()
        rows.append(fila)
        i += 1
    return rows


CAMPOS_EXT = [
    'fecha', 'hora', 'ancho', 'calibre', 'peso', 'color',
    'tratado', 'resistencia', 'bloqueo', 'fundido',
    'transparencia', 'contaminacion', 'identif_mezcla', 'cores',
    'cant_rechazada', 'comentarios',
]

CAMPOS_IMP = [
    'fecha', 'hora',
    'adherencia_tinta', 'inspeccion_visual', 'validacion_corrida',
    'codigo_barras', 'precorte', 'repeticion',
    'libre_arrugas', 'placa_despegada', 'libre_retinte',
    'libre_bloqueo', 'verif_pantone', 'textos_legibles', 'comp_estandar',
    'comentarios',
]

CAMPOS_CON = [
    'fecha', 'hora', 'ancho', 'largo', 'fuelle', 'calibre',
    'sellado', 'troquel', 'perforacion', 'impresion',
    'corte', 'empaque', 'etiqueta', 'codigo', 'fondo', 'lateral',
    'sello_frontal', 'sello_mango',
    'largo_inicial', 'largo_final', 'elongacion',
    'cant_producida', 'cant_rechazada', 'cant_revisada',
    'defecto', 'comentarios',
]


# ─── Autenticación ────────────────────────────────────────────────────────────

def login_view(request):
    if get_usuario(request):
        return redirect('bitacora:extrusion')

    form = LoginForm(request.POST or None)
    error = None

    if request.method == 'POST' and form.is_valid():
        codigo = form.cleaned_data['codigo_empleado'].strip()
        password = form.cleaned_data['password']
        try:
            usuario = Usuario.objects.get(codigo_empleado=codigo, activo=True)
            if usuario.check_password(password):
                request.session['usuario_id'] = usuario.pk
                request.session.set_expiry(86400 * 7)
                return redirect('bitacora:extrusion')
        except Usuario.DoesNotExist:
            pass
        error = 'Código de empleado o contraseña incorrectos.'

    return render(request, 'bitacora/login.html', {'form': form, 'error': error})


def logout_view(request):
    request.session.flush()
    return redirect('bitacora:login')


# ─── Formulario Extrusión ─────────────────────────────────────────────────────

@login_required
def extrusion_view(request):
    ctx = contexto_base(request)
    ctx['area'] = 'ext'
    ctx['area_label'] = 'Extrusión'
    ctx['maquinas'] = MAQUINAS_EXT
    ctx['material_choices'] = Registro.MATERIAL_CHOICES

    if request.method == 'POST':
        filas = _parse_rows(request.POST, CAMPOS_EXT)
        if not filas:
            messages.warning(request, 'Agrega al menos una fila de verificación.')
            return render(request, 'bitacora/extrusion.html', ctx)

        maquina = request.POST.get('maquina', '').strip()
        mo = request.POST.get('mo', '').strip()
        descripcion = request.POST.get('descripcion', '').strip()

        if not maquina:
            messages.warning(request, 'Selecciona una máquina.')
            return render(request, 'bitacora/extrusion.html', ctx)
        if not mo:
            messages.warning(request, 'Ingresa el número de MO.')
            return render(request, 'bitacora/extrusion.html', ctx)
        if not descripcion:
            messages.warning(request, 'Ingresa la descripción del producto.')
            return render(request, 'bitacora/extrusion.html', ctx)

        fecha_str = request.POST.get('fecha', '') or date.today().isoformat()
        hora_str = request.POST.get('hora_inicio', '') or timezone.localtime().strftime('%H:%M')
        try:
            fecha = date.fromisoformat(fecha_str)
        except ValueError:
            fecha = date.today()
        try:
            hora = datetime.strptime(hora_str, '%H:%M').time()
        except ValueError:
            hora = timezone.localtime().time()

        registro = Registro.objects.create(
            area='ext',
            turno=request.POST.get('turno', turno_actual()),
            fecha=fecha,
            hora_inicio=hora,
            maquina=maquina,
            mo=mo,
            item=request.POST.get('item', '').strip(),
            descripcion=descripcion,
            auditor=request.POST.get('auditor', '').strip(),
            supervisor=request.POST.get('supervisor', '').strip(),
            material_tipo=request.POST.get('material_tipo', '').strip(),
            usa_impresion=request.POST.get('usa_impresion') == '1',
            usa_conversion=request.POST.get('usa_conversion') == '1',
            datos_filas=filas,
            creado_por=get_usuario(request),
        )
        messages.success(request, f'Registro de Extrusión guardado correctamente. ID #{registro.pk}')
        return redirect('bitacora:extrusion')

    return render(request, 'bitacora/extrusion.html', ctx)


# ─── Formulario Impresión ─────────────────────────────────────────────────────

@login_required
def impresion_view(request):
    ctx = contexto_base(request)
    ctx['area'] = 'imp'
    ctx['area_label'] = 'Impresión'
    ctx['maquinas'] = MAQUINAS_IMP

    if request.method == 'POST':
        filas = _parse_rows(request.POST, CAMPOS_IMP)
        if not filas:
            messages.warning(request, 'Agrega al menos una fila de verificación.')
            return render(request, 'bitacora/impresion.html', ctx)

        maquina = request.POST.get('maquina', '').strip()
        mo = request.POST.get('mo', '').strip()
        descripcion = request.POST.get('descripcion', '').strip()

        if not maquina:
            messages.warning(request, 'Selecciona una máquina.')
            return render(request, 'bitacora/impresion.html', ctx)
        if not mo:
            messages.warning(request, 'Ingresa el número de MO.')
            return render(request, 'bitacora/impresion.html', ctx)
        if not descripcion:
            messages.warning(request, 'Ingresa la descripción del producto.')
            return render(request, 'bitacora/impresion.html', ctx)

        fecha_str = request.POST.get('fecha', '') or date.today().isoformat()
        hora_str = request.POST.get('hora_inicio', '') or timezone.localtime().strftime('%H:%M')
        try:
            fecha = date.fromisoformat(fecha_str)
        except ValueError:
            fecha = date.today()
        try:
            hora = datetime.strptime(hora_str, '%H:%M').time()
        except ValueError:
            hora = timezone.localtime().time()

        registro = Registro.objects.create(
            area='imp',
            turno=request.POST.get('turno', turno_actual()),
            fecha=fecha,
            hora_inicio=hora,
            maquina=maquina,
            mo=mo,
            item=request.POST.get('item', '').strip(),
            descripcion=descripcion,
            auditor=request.POST.get('auditor', '').strip(),
            supervisor=request.POST.get('supervisor', '').strip(),
            datos_filas=filas,
            creado_por=get_usuario(request),
        )
        messages.success(request, f'Registro de Impresión guardado correctamente. ID #{registro.pk}')
        return redirect('bitacora:impresion')

    return render(request, 'bitacora/impresion.html', ctx)


# ─── Formulario Conversión ────────────────────────────────────────────────────

@login_required
def conversion_view(request):
    ctx = contexto_base(request)
    ctx['area'] = 'con'
    ctx['area_label'] = 'Conversión'
    ctx['maquinas'] = MAQUINAS_CON

    if request.method == 'POST':
        filas = _parse_rows(request.POST, CAMPOS_CON)
        if not filas:
            messages.warning(request, 'Agrega al menos una fila de verificación.')
            return render(request, 'bitacora/conversion.html', ctx)

        maquina = request.POST.get('maquina', '').strip()
        mo = request.POST.get('mo', '').strip()
        descripcion = request.POST.get('descripcion', '').strip()

        if not maquina:
            messages.warning(request, 'Selecciona una máquina.')
            return render(request, 'bitacora/conversion.html', ctx)
        if not mo:
            messages.warning(request, 'Ingresa el número de MO.')
            return render(request, 'bitacora/conversion.html', ctx)
        if not descripcion:
            messages.warning(request, 'Ingresa la descripción del producto.')
            return render(request, 'bitacora/conversion.html', ctx)

        fecha_str = request.POST.get('fecha', '') or date.today().isoformat()
        hora_str = request.POST.get('hora_inicio', '') or timezone.localtime().strftime('%H:%M')
        try:
            fecha = date.fromisoformat(fecha_str)
        except ValueError:
            fecha = date.today()
        try:
            hora = datetime.strptime(hora_str, '%H:%M').time()
        except ValueError:
            hora = timezone.localtime().time()

        registro = Registro.objects.create(
            area='con',
            turno=request.POST.get('turno', turno_actual()),
            fecha=fecha,
            hora_inicio=hora,
            maquina=maquina,
            mo=mo,
            item=request.POST.get('item', '').strip(),
            descripcion=descripcion,
            auditor=request.POST.get('auditor', '').strip(),
            supervisor=request.POST.get('supervisor', '').strip(),
            es_tshirt='es_tshirt' in request.POST,
            datos_filas=filas,
            creado_por=get_usuario(request),
        )
        messages.success(request, f'Registro de Conversión guardado correctamente. ID #{registro.pk}')
        return redirect('bitacora:conversion')

    return render(request, 'bitacora/conversion.html', ctx)


# ─── Historial ────────────────────────────────────────────────────────────────

@login_required
def historial_view(request):
    ctx = contexto_base(request)

    qs = Registro.objects.select_related('creado_por').all()

    area_filter = request.GET.get('area', '')
    desde = request.GET.get('desde', '')
    hasta = request.GET.get('hasta', '')
    busqueda = request.GET.get('q', '').strip()

    if area_filter:
        qs = qs.filter(area=area_filter)
    if desde:
        qs = qs.filter(fecha__gte=desde)
    if hasta:
        qs = qs.filter(fecha__lte=hasta)
    if busqueda:
        from django.db.models import Q
        qs = qs.filter(
            Q(mo__icontains=busqueda) |
            Q(maquina__icontains=busqueda) |
            Q(item__icontains=busqueda) |
            Q(auditor__icontains=busqueda)
        )

    ctx.update({
        'registros': qs,
        'area_filter': area_filter,
        'desde': desde,
        'hasta': hasta,
        'busqueda': busqueda,
        'area_choices': Registro.AREA_CHOICES,
    })
    return render(request, 'bitacora/historial.html', ctx)


@login_required
def eliminar_registro_view(request, pk):
    usuario = get_usuario(request)
    if not usuario.is_supervisor:
        messages.error(request, 'Solo supervisores y administradores pueden eliminar registros.')
        return redirect('bitacora:historial')

    registro = get_object_or_404(Registro, pk=pk)
    if request.method == 'POST':
        registro.delete()
        messages.success(request, f'Registro #{pk} eliminado.')
    return redirect('bitacora:historial')


# ─── Gestión de usuarios ──────────────────────────────────────────────────────

@admin_required
def registrar_view(request):
    ctx = contexto_base(request)
    form = UsuarioForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, f'Usuario "{form.cleaned_data["nombre"]}" registrado correctamente.')
        return redirect('bitacora:usuarios')

    ctx['form'] = form
    return render(request, 'bitacora/registrar.html', ctx)


@admin_required
def usuarios_view(request):
    ctx = contexto_base(request)
    ctx['usuarios'] = Usuario.objects.all().order_by('nombre')
    return render(request, 'bitacora/usuarios.html', ctx)


@admin_required
def toggle_usuario_view(request, pk):
    if request.method == 'POST':
        usuario = get_object_or_404(Usuario, pk=pk)
        usuario.activo = not usuario.activo
        usuario.save()
        estado = 'activado' if usuario.activo else 'desactivado'
        messages.success(request, f'Usuario "{usuario.nombre}" {estado}.')
    return redirect('bitacora:usuarios')
