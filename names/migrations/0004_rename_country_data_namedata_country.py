# Generated by Django 4.2 on 2025-04-08 11:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('names', '0003_alter_namedata_name'),
    ]

    operations = [
        migrations.RenameField(
            model_name='namedata',
            old_name='country_data',
            new_name='country',
        ),
    ]
