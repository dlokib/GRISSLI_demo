# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-02-22 17:12
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('parsing', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='result',
            name='codec',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='parsing.Codec'),
        ),
        migrations.AlterField(
            model_name='result',
            name='status',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='parsing.Status'),
        ),
    ]