from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('bitacora', '0001_initial'),
    ]

    operations = [
        # ── Usuario: campo password ───────────────────────────────────────────
        migrations.AddField(
            model_name='usuario',
            name='password',
            field=models.CharField(default='', max_length=128),
        ),

        # ── Usuario: email ahora puede estar vacío ────────────────────────────
        migrations.AlterField(
            model_name='usuario',
            name='email',
            field=models.EmailField(blank=True, default='', max_length=254, unique=True),
        ),

        # ── Registro: eliminar campos obsoletos ───────────────────────────────
        migrations.RemoveField(
            model_name='registro',
            name='frontend_id',
        ),
        migrations.RemoveField(
            model_name='registro',
            name='hora_fin',
        ),
        migrations.RemoveField(
            model_name='registro',
            name='filas',
        ),
        migrations.RemoveField(
            model_name='registro',
            name='guardado_at',
        ),

        # ── Registro: campos nuevos ───────────────────────────────────────────
        migrations.AddField(
            model_name='registro',
            name='supervisor',
            field=models.CharField(blank=True, default='', max_length=100),
        ),
        migrations.AddField(
            model_name='registro',
            name='material_tipo',
            field=models.CharField(
                blank=True,
                choices=[
                    ('pigmentado', 'Pigmentado'),
                    ('clear', 'Clear'),
                    ('embobinado', 'Embobinado'),
                ],
                default='',
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name='registro',
            name='es_tshirt',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='registro',
            name='datos_filas',
            field=models.JSONField(blank=True, default=list),
        ),
        migrations.AddField(
            model_name='registro',
            name='creado_por',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='registros',
                to='bitacora.usuario',
            ),
        ),

        # ── Registro: actualizar TURNO choices y ordering ─────────────────────
        migrations.AlterField(
            model_name='registro',
            name='turno',
            field=models.CharField(
                choices=[
                    ('A', 'Turno A  (6:00 AM – 2:00 PM)'),
                    ('B', 'Turno B  (2:00 PM – 10:00 PM)'),
                    ('C', 'Turno C  (10:00 PM – 6:00 AM)'),
                ],
                default='A',
                max_length=1,
            ),
        ),
        migrations.AlterModelOptions(
            name='registro',
            options={
                'ordering': ['-creado_en'],
                'verbose_name': 'Registro de Calidad',
                'verbose_name_plural': 'Registros de Calidad',
            },
        ),
    ]
