# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-08-09 06:07
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('gitmate_config', '0009_auto_20170622_1147'),
        ('gitmate_ack', '0005_auto_20170716_1155'),
    ]

    operations = [
        migrations.CreateModel(
            name='MergeRequestModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.IntegerField()),
                ('acks', django.contrib.postgres.fields.jsonb.JSONField(default={})),
                ('repo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ack_mrs', to='gitmate_config.Repository')),
            ],
        ),
    ]
