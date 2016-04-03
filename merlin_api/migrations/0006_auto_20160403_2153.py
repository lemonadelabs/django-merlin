# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-04-03 21:53
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('merlin_api', '0005_entity_is_source'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attribute',
            name='sim',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attributes', to='merlin_api.Simulation'),
        ),
        migrations.AlterField(
            model_name='entity',
            name='parent',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='merlin_api.Entity'),
        ),
        migrations.AlterField(
            model_name='entity',
            name='sim',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='entities', to='merlin_api.Simulation'),
        ),
        migrations.AlterField(
            model_name='inputconnector',
            name='parent',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='inputs', to='merlin_api.Entity'),
        ),
        migrations.AlterField(
            model_name='output',
            name='sim',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='outputs', to='merlin_api.Simulation'),
        ),
        migrations.AlterField(
            model_name='outputconnector',
            name='parent',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='outputs', to='merlin_api.Entity'),
        ),
        migrations.AlterField(
            model_name='simoutputconnector',
            name='parent',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='inputs', to='merlin_api.Output'),
        ),
        migrations.AlterField(
            model_name='unittype',
            name='sim',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='unittypes', to='merlin_api.Simulation'),
        ),
    ]