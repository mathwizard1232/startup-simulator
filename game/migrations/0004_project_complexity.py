# Generated by Django 5.1.2 on 2024-10-09 18:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0003_alter_company_overtime_policy_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='complexity',
            field=models.IntegerField(default=1),
        ),
    ]
