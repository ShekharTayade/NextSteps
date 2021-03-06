# Generated by Django 2.0 on 2018-01-05 16:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('NextSteps', '0007_auto_20180105_1533'),
    ]

    operations = [
        migrations.CreateModel(
            name='InstituteProgramImpDates',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('event', models.CharField(blank=True, default='', max_length=500)),
                ('date', models.CharField(blank=True, default='', max_length=500)),
                ('Discipline', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='NextSteps.Discipline')),
                ('Institute', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='NextSteps.Institute')),
                ('Level', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='NextSteps.Level')),
                ('Program', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='NextSteps.Program')),
            ],
        ),
    ]
