# Generated by Django 2.0.3 on 2018-09-26 09:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('NextSteps', '0046_auto_20180924_1418'),
    ]

    operations = [
        migrations.AddField(
            model_name='userdayschedule',
            name='schedule_generated',
            field=models.NullBooleanField(default=False),
        ),
        migrations.AddField(
            model_name='userdayschedule',
            name='schedule_generated_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
