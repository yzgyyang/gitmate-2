# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2017-12-05 20:09
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('gitmate_ack', '0007_mergerequestmodel_last_head'),
    ]

    operations = [
        migrations.AlterField(
            model_name='settings',
            name='repo',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='gitmate_ack_settings', to='gitmate_config.Repository'),
        ),
    ]
