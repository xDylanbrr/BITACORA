from django.db import models
from django.contrib.auth.hashers import make_password, check_password


class Usuario(models.Model):
    ROL_CHOICES = [
        ('Administrador', 'Administrador'),
        ('Auditor', 'Auditor de Calidad'),
        ('Supervisor', 'Supervisor'),
        ('Operador', 'Operador'),
    ]

    nombre = models.CharField(max_length=150)
    rol = models.CharField(max_length=20, choices=ROL_CHOICES, default='Operador')
    email = models.EmailField(unique=True, blank=True, default='')
    codigo_empleado = models.CharField(max_length=20, unique=True, blank=True, null=True)
    departamento = models.CharField(max_length=100, blank=True, default='')
    cedula = models.CharField(max_length=15, blank=True, default='')
    telefono = models.CharField(max_length=15, blank=True, default='')
    password = models.CharField(max_length=128, default='')
    activo = models.BooleanField(default=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Usuario del Sistema'
        verbose_name_plural = 'Usuarios del Sistema'
        ordering = ['nombre']

    def __str__(self):
        return f"{self.nombre} ({self.rol})"

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    @property
    def is_admin(self):
        return self.rol == 'Administrador'

    @property
    def is_supervisor(self):
        return self.rol in ('Administrador', 'Supervisor')


class Registro(models.Model):
    AREA_CHOICES = [
        ('ext', 'Extrusión'),
        ('imp', 'Impresión'),
        ('con', 'Conversión'),
    ]
    TURNO_CHOICES = [
        ('A', 'Turno A  (6:00 AM – 2:00 PM)'),
        ('B', 'Turno B  (2:00 PM – 10:00 PM)'),
        ('C', 'Turno C  (10:00 PM – 6:00 AM)'),
    ]
    MATERIAL_CHOICES = [
        ('pigmentado', 'Pigmentado'),
        ('clear', 'Clear'),
        ('embobinado', 'Embobinado'),
    ]

    area = models.CharField(max_length=10, choices=AREA_CHOICES)
    turno = models.CharField(max_length=1, choices=TURNO_CHOICES, default='A')
    fecha = models.DateField(null=True, blank=True)
    hora_inicio = models.TimeField(null=True, blank=True)
    maquina = models.CharField(max_length=100, blank=True, default='')
    mo = models.CharField(max_length=50, blank=True, default='', verbose_name='MO #')
    item = models.CharField(max_length=20, blank=True, default='', verbose_name='Ítem')
    descripcion = models.CharField(max_length=200, blank=True, default='', verbose_name='Descripción del producto')
    auditor = models.CharField(max_length=100, blank=True, default='')
    supervisor = models.CharField(max_length=100, blank=True, default='')

    # Extrusión: tipo de material
    material_tipo = models.CharField(max_length=20, choices=MATERIAL_CHOICES, blank=True, default='')

    # Conversión: producto T-Shirt
    es_tshirt = models.BooleanField(default=False)

    # Extrusión: procesos siguientes activos
    usa_impresion = models.BooleanField(default=False, verbose_name='Usa Impresión')
    usa_conversion = models.BooleanField(default=False, verbose_name='Usa Conversión')

    # Filas de inspección (almacenadas como JSON)
    datos_filas = models.JSONField(default=list, blank=True)

    creado_en = models.DateTimeField(auto_now_add=True)
    modificado_en = models.DateTimeField(auto_now=True)
    creado_por = models.ForeignKey(
        Usuario, null=True, blank=True, on_delete=models.SET_NULL, related_name='registros'
    )

    class Meta:
        verbose_name = 'Registro de Calidad'
        verbose_name_plural = 'Registros de Calidad'
        ordering = ['-creado_en']

    def __str__(self):
        return f"{self.get_area_display()} | {self.fecha} | MO: {self.mo} | Auditor: {self.auditor}"

    @property
    def num_filas(self):
        return len(self.datos_filas)
