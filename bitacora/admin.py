from django.contrib import admin
from .models import Registro, Usuario


@admin.register(Registro)
class RegistroAdmin(admin.ModelAdmin):
    list_display = ('area', 'fecha', 'mo', 'maquina', 'auditor', 'supervisor', 'turno', 'num_filas', 'creado_en')
    list_filter = ('area', 'turno', 'fecha')
    search_fields = ('mo', 'maquina', 'auditor', 'supervisor', 'descripcion')
    readonly_fields = ('creado_en', 'modificado_en')
    ordering = ('-creado_en',)


@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'rol', 'codigo_empleado', 'email', 'departamento', 'activo', 'creado_en')
    list_filter = ('rol', 'activo')
    search_fields = ('nombre', 'email', 'codigo_empleado')
    readonly_fields = ('creado_en',)
