# Generated by Django 2.1.7 on 2019-04-15 18:37

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('reg', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Hora',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('inicio', models.DateTimeField()),
                ('fin', models.DateTimeField()),
                ('box', models.IntegerField()),
                ('realizada', models.BooleanField(default=False)),
                ('medico', models.ForeignKey(limit_choices_to={'groups__name': 'Médicos'}, on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
                ('servicio', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='reg.Cotizado')),
            ],
            options={
                'ordering': ['inicio'],
            },
        ),
    ]