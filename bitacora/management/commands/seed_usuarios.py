from django.core.management.base import BaseCommand
from bitacora.models import Usuario


SEED_DATA = [
    {
        'codigo_empleado': '1',
        'nombre': 'Administrador GTG',
        'rol': 'Administrador',
        'email': 'admin@gtg.local',
        'password': '1234',
    },
    {
        'codigo_empleado': '0814',
        'nombre': 'Reily Nalda Santos Guzmán',
        'rol': 'Supervisor',
        'email': 'rsantos@gtg.com.do',
        'password': '1234',
        'departamento': 'Producción',
    },
    {
        'codigo_empleado': '0852',
        'nombre': 'Eloy José Delgado Álvarez',
        'rol': 'Supervisor',
        'email': 'edelgado@gtg.com.do',
        'password': '1234',
        'departamento': 'Producción',
    },
    {
        'codigo_empleado': '0906',
        'nombre': 'Esther Noemí Taveras Hernández',
        'rol': 'Auditor',
        'email': 'esthertaveras1829@gmail.com',
        'password': '1234',
        'departamento': 'Control de Calidad',
    },
    {
        'codigo_empleado': '1063',
        'nombre': 'Randy Eduardo Vargas Marmolejos',
        'rol': 'Auditor',
        'email': 'randyvargassem04@gmail.com',
        'password': '1234',
        'departamento': 'Control de Calidad',
    },
    {
        'codigo_empleado': '1087',
        'nombre': 'Yulian Jose Victoriano Martinez',
        'rol': 'Auditor',
        'email': 'yulianm23@gmail.com',
        'password': '1234',
        'departamento': 'Control de Calidad',
    },
]


class Command(BaseCommand):
    help = 'Crea los usuarios iniciales del sistema de auditoría de calidad.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset-passwords',
            action='store_true',
            help='Resetea las contraseñas de usuarios existentes al valor del seed.',
        )

    def handle(self, *args, **options):
        created = 0
        updated = 0

        for data in SEED_DATA:
            password = data.pop('password')
            try:
                usuario = Usuario.objects.get(codigo_empleado=data['codigo_empleado'])
                if options['reset_passwords']:
                    usuario.set_password(password)
                    for k, v in data.items():
                        setattr(usuario, k, v)
                    usuario.save()
                    updated += 1
                    self.stdout.write(f'  Actualizado: {usuario.nombre}')
                else:
                    self.stdout.write(f'  Ya existe (sin cambios): {usuario.nombre}')
            except Usuario.DoesNotExist:
                usuario = Usuario(**data)
                usuario.set_password(password)
                usuario.save()
                created += 1
                self.stdout.write(self.style.SUCCESS(f'  Creado: {usuario.nombre}'))

        self.stdout.write(self.style.SUCCESS(
            f'\nSeed completado: {created} creados, {updated} actualizados.'
        ))
        if created > 0 or updated > 0:
            self.stdout.write('Contraseña inicial de todos: 1234  (cámbiala en producción)')
