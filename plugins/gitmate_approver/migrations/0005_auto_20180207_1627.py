# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2018-02-07 16:27
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gitmate_approver', '0004_auto_20180102_0903'),
    ]

    operations = [
        migrations.AlterField(
            model_name='settings',
            name='status_labels',
            field=models.TextField(default='process/pending_review, process/WIP', help_text='Comma seperated labels to be removed from the merge request once it has been approved. e.g. process/WIP, status/stale, process/pending_review'),
        ),
    ]
