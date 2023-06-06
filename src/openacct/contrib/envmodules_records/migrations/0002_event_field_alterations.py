# Generated by Django 3.2.7 on 2023-06-06 15:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('envmodules_records', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='envmoduleseventrecord',
            name='mode',
            field=models.CharField(choices=[('load', 'Load'), ('unload', 'Unload')], max_length=8),
        ),
        migrations.AlterField(
            model_name='envmoduleseventrecord',
            name='module',
            field=models.CharField(max_length=1024),
        ),
    ]
