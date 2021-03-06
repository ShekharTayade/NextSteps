# Generated by Django 2.0 on 2018-04-12 06:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('NextSteps', '0031_remove_instituteadmroutes_program'),
    ]

    operations = [
        migrations.AddField(
            model_name='instituteadmroutes',
            name='Country',
            field=models.ForeignKey(default='India', on_delete=django.db.models.deletion.PROTECT, to='NextSteps.Country'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='institutecutoffs',
            name='Country',
            field=models.ForeignKey(default='India', on_delete=django.db.models.deletion.PROTECT, to='NextSteps.Country'),
            preserve_default=False,
        ),
    ]
