# Generated by Django 2.0.3 on 2018-09-21 05:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('NextSteps', '0044_studyhours_date_updated'),
    ]

    operations = [
        migrations.AddField(
            model_name='useraccount',
            name='payment_txn_amount',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True),
        ),
        migrations.AddField(
            model_name='useraccount',
            name='payment_txn_email',
            field=models.CharField(blank=True, default='', max_length=250),
        ),
        migrations.AddField(
            model_name='useraccount',
            name='payment_txn_id',
            field=models.CharField(blank=True, default='', max_length=250),
        ),
        migrations.AddField(
            model_name='useraccount',
            name='payment_txn_key',
            field=models.CharField(blank=True, default='', max_length=250),
        ),
        migrations.AddField(
            model_name='useraccount',
            name='payment_txn_posted_hash',
            field=models.CharField(blank=True, default='', max_length=250),
        ),
        migrations.AddField(
            model_name='useraccount',
            name='payment_txn_productinfo',
            field=models.CharField(blank=True, default='', max_length=250),
        ),
        migrations.AddField(
            model_name='useraccount',
            name='payment_txn_salt',
            field=models.CharField(blank=True, default='', max_length=250),
        ),
        migrations.AddField(
            model_name='useraccount',
            name='payment_txn_status',
            field=models.CharField(blank=True, default='', max_length=10),
        ),
    ]