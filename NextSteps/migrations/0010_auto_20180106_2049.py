# Generated by Django 2.0 on 2018-01-06 15:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('NextSteps', '0009_contactform'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contactform',
            name='name',
            field=models.CharField(max_length=200),
        ),
        migrations.AlterField(
            model_name='contactform',
            name='phone_number',
            field=models.CharField(blank=True, default='', max_length=30),
        ),
    ]
