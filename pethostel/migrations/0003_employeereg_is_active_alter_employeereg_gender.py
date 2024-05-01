# Generated by Django 5.0.3 on 2024-04-23 11:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pethostel', '0002_petregistration'),
    ]

    operations = [
        migrations.AddField(
            model_name='employeereg',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='employeereg',
            name='gender',
            field=models.CharField(choices=[('Male', 'male'), ('Female', 'female')], max_length=8),
        ),
    ]
