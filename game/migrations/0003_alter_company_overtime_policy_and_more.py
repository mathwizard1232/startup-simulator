# Generated by Django 5.1.2 on 2024-10-09 04:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0002_company_overtime_policy_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='company',
            name='overtime_policy',
            field=models.CharField(choices=[('no_overtime', 'No Overtime'), ('optional', 'Optional Overtime'), ('mandatory', 'Mandatory Overtime')], default='no_overtime', max_length=20),
        ),
        migrations.AlterField(
            model_name='company',
            name='status_report_frequency',
            field=models.CharField(choices=[('daily', 'Daily'), ('weekly', 'Weekly'), ('monthly', 'Monthly')], default='weekly', max_length=20),
        ),
    ]
