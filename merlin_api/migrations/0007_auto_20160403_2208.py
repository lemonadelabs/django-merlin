# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-04-03 22:08
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('merlin_api', '0006_auto_20160403_2153'),
    ]

    operations = [
        migrations.AlterField(
            model_name='endpoint',
            name='parent',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='endpoints', to='merlin_api.OutputConnector'),
        ),
        migrations.AlterField(
            model_name='process',
            name='parent',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='processes', to='merlin_api.Entity'),
        ),
        migrations.AlterField(
            model_name='processproperty',
            name='process',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='properties', to='merlin_api.Process'),
        ),
    ]
