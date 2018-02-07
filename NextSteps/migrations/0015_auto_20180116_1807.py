# Generated by Django 2.0 on 2018-01-16 12:37

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('NextSteps', '0014_auto_20180109_2355'),
    ]

    operations = [
        migrations.CreateModel(
            name='InstituteAdmRoutes',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('adm_route', models.CharField(max_length=500)),
                ('Description', models.CharField(blank=True, default='', max_length=5000)),
                ('Discipline', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='NextSteps.Discipline')),
                ('Institute', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='NextSteps.Institute')),
                ('Level', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='NextSteps.Level')),
                ('Program', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='NextSteps.Program')),
            ],
        ),
        migrations.CreateModel(
            name='StudentCategory',
            fields=[
                ('category', models.CharField(max_length=50, primary_key=True, serialize=False)),
                ('description', models.CharField(blank=True, max_length=100, null=True, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='StudentCategoryUserPref',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('StudentCategory', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='NextSteps.StudentCategory')),
                ('User', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.RemoveField(
            model_name='instituteprogramseats',
            name='SeatQuota',
        ),
        migrations.AddField(
            model_name='instituteprogramimpdates',
            name='event_order',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='instituteprogramseats',
            name='quota',
            field=models.CharField(blank=True, default='', max_length=50),
        ),
        migrations.AlterField(
            model_name='institutecutoffs',
            name='quota',
            field=models.CharField(blank=True, default='', max_length=50),
        ),
        migrations.AlterField(
            model_name='institutejeeranks',
            name='quota',
            field=models.CharField(blank=True, default='', max_length=50),
        ),
        migrations.AlterField(
            model_name='institutesurveyranking',
            name='rank',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='institutecutoffs',
            name='StudentCategory',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='NextSteps.StudentCategory'),
        ),
        migrations.AddField(
            model_name='institutejeeranks',
            name='StudentCategory',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='NextSteps.StudentCategory'),
        ),
        migrations.AddField(
            model_name='instituteprogramseats',
            name='StudentCategory',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='NextSteps.StudentCategory'),
        ),
    ]
