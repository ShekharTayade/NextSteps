# Generated by Django 2.0.3 on 2018-09-20 14:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('NextSteps', '0043_auto_20180907_1533'),
    ]

    operations = [
        migrations.AddField(
            model_name='studyhours',
            name='date_updated',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
