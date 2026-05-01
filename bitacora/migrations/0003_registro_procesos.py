from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bitacora', '0002_reestructuracion_django'),
    ]

    operations = [
        migrations.AddField(
            model_name='registro',
            name='usa_impresion',
            field=models.BooleanField(default=False, verbose_name='Usa Impresión'),
        ),
        migrations.AddField(
            model_name='registro',
            name='usa_conversion',
            field=models.BooleanField(default=False, verbose_name='Usa Conversión'),
        ),
    ]
