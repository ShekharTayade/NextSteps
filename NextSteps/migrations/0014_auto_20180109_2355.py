# Generated by Django 2.0 on 2018-01-09 18:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('NextSteps', '0013_useraccount'),
    ]

    operations = [
        migrations.RenameField(
            model_name='useraccount',
            old_name='susbcription_amount',
            new_name='subscription_amount',
        ),
    ]
