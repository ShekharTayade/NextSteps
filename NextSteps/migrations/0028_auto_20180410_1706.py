# Generated by Django 2.0 on 2018-04-10 11:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('NextSteps', '0027_auto_20180404_1055'),
    ]

    operations = [
        migrations.CreateModel(
            name='EntranceExamImpDates',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('entrance_exam_code', models.CharField(max_length=50)),
                ('year', models.CharField(max_length=4)),
                ('event', models.CharField(blank=True, default='', max_length=500)),
                ('start_date', models.DateField(blank=True, null=True)),
                ('end_date', models.DateField(blank=True, null=True)),
                ('remarks', models.CharField(blank=True, default='', max_length=2000)),
            ],
        ),
        migrations.CreateModel(
            name='InstituteEntranceExam',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('year', models.CharField(blank=True, default='', max_length=4)),
                ('Country', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='NextSteps.Country')),
                ('Discipline', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='NextSteps.Discipline')),
            ],
        ),
        migrations.CreateModel(
            name='InstituteImpDates',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('event', models.CharField(blank=True, default='', max_length=500)),
                ('start_date', models.DateField(blank=True, null=True)),
                ('end_date', models.DateField(blank=True, null=True)),
                ('remarks', models.CharField(blank=True, default='', max_length=2000)),
                ('Country', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='NextSteps.Country')),
                ('Discipline', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='NextSteps.Discipline')),
                ('Institute', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='NextSteps.Institute')),
                ('Level', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='NextSteps.Level')),
            ],
        ),
        migrations.AddField(
            model_name='entranceexam',
            name='Country',
            field=models.ForeignKey(default='India', on_delete=django.db.models.deletion.PROTECT, to='NextSteps.Country'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='entranceexam',
            name='Discipline',
            field=models.ForeignKey(default='ENGG', on_delete=django.db.models.deletion.PROTECT, to='NextSteps.Discipline'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='entranceexam',
            name='Level',
            field=models.ForeignKey(default='Undergrad', on_delete=django.db.models.deletion.PROTECT, to='NextSteps.Level'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='instituteentranceexam',
            name='EntranceExam',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='NextSteps.EntranceExam'),
        ),
        migrations.AddField(
            model_name='instituteentranceexam',
            name='Institute',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='NextSteps.Institute'),
        ),
        migrations.AddField(
            model_name='instituteentranceexam',
            name='Level',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='NextSteps.Level'),
        ),
    ]