# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-03-31 21:47
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('merlin_api', '0003_simoutputconnector'),
    ]

    operations = [
        migrations.AddField(
            model_name='endpoint',
            name='sim_output',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='merlin_api.SimOutputConnector'),
        ),
        migrations.AlterField(
            model_name='endpoint',
            name='input',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='merlin_api.InputConnector'),
        ),
    ]
