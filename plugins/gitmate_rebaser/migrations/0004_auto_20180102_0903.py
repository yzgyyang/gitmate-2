# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2018-01-02 09:03
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gitmate_rebaser', '0003_auto_20171212_1405'),
    ]

    operations = [
        migrations.AlterField(
            model_name='settings',
            name='enable_fastforward',
            field=models.BooleanField(default=False, help_text='Fast forward default branch (git merge --ff-only)'),
        ),
        migrations.AlterField(
            model_name='settings',
            name='enable_merge',
            field=models.BooleanField(default=False, help_text='Merge to default branch (git merge --no-ff).'),
        ),
        migrations.AlterField(
            model_name='settings',
            name='enable_rebase',
            field=models.BooleanField(default=True, help_text='Rebase on default branch (git rebase).'),
        ),
    ]
