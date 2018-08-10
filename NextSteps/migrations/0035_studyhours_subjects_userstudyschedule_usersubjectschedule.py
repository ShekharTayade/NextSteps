# Generated by Django 2.0 on 2018-07-30 04:12

import NextSteps.validators
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('NextSteps', '0034_program_program_group'),
    ]

    operations = [
        migrations.CreateModel(
            name='StudyHours',
            fields=[
                ('id', models.DecimalField(decimal_places=25, max_digits=30, primary_key=True, serialize=False)),
                ('subject', models.CharField(max_length=2000)),
                ('date', models.DateField(blank=True, null=True)),
                ('planned_hours', models.DecimalField(blank=True, decimal_places=2, max_digits=4, null=True, validators=[NextSteps.validators.validate_max24hrs])),
                ('actual_hours', models.DecimalField(blank=True, decimal_places=2, max_digits=4, null=True, validators=[NextSteps.validators.validate_max24hrs])),
                ('User', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Subjects',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subject', models.CharField(max_length=2000)),
                ('Country', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='NextSteps.Country')),
                ('Discipline', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='NextSteps.Discipline')),
                ('Level', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='NextSteps.Level')),
            ],
        ),
        migrations.CreateModel(
            name='UserStudySchedule',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('study_days_per_week', models.PositiveIntegerField(blank=True, null=True, validators=[NextSteps.validators.validate_max7days])),
                ('study_hours_per_day', models.DecimalField(blank=True, decimal_places=2, max_digits=4, null=True, validators=[NextSteps.validators.validate_max24hrs])),
                ('start_date', models.DateField(blank=True, null=True)),
                ('end_date', models.DateField(blank=True, null=True)),
                ('User', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='UserSubjectSchedule',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subject', models.CharField(max_length=2000)),
                ('percentage_weight', models.DecimalField(blank=True, decimal_places=0, max_digits=3, null=True, validators=[NextSteps.validators.validate_max100])),
                ('start_date', models.DateField(blank=True, null=True)),
                ('end_date', models.DateField(blank=True, null=True)),
                ('User', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
