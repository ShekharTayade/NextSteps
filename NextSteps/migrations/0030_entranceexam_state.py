# Generated by Django 2.0 on 2018-04-11 07:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('NextSteps', '0029_auto_20180411_1146'),
    ]

    operations = [
        migrations.AddField(
            model_name='entranceexam',
            name='state',
            field=models.CharField(blank=True, default='', max_length=50),
        ),
    ]
