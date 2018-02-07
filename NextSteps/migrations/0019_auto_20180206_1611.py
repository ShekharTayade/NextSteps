# Generated by Django 2.0 on 2018-02-06 10:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('NextSteps', '0018_auto_20180205_1940'),
    ]

    operations = [
        migrations.RenameField(
            model_name='userappdetails',
            old_name='percetage_of_diability',
            new_name='percetage_of_disability',
        ),
        migrations.RemoveField(
            model_name='userappdetails',
            name='adhaar_number',
        ),
        migrations.AddField(
            model_name='userappdetails',
            name='aadhaar_number',
            field=models.CharField(blank=True, default='', max_length=12),
        ),
        migrations.AlterField(
            model_name='userappdetails',
            name='class_10th_percentage_cgpa',
            field=models.CharField(blank=True, default='', max_length=25),
        ),
        migrations.AlterField(
            model_name='userappdetails',
            name='class_12th_percentage_cgpa',
            field=models.CharField(blank=True, default='', max_length=25),
        ),
        migrations.AlterField(
            model_name='userappdetails',
            name='gender',
            field=models.CharField(choices=[('MALE', 'Male'), ('FEMALE', 'Female')], default='MALE', max_length=6),
        ),
        migrations.AlterField(
            model_name='userappdetails',
            name='pin_code',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
    ]
