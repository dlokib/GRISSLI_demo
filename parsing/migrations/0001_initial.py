# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-02-22 14:07
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Codec',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=16)),
            ],
        ),
        migrations.CreateModel(
            name='Result',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('datetime', models.IntegerField(default=0)),
                ('title', models.CharField(max_length=64)),
                ('header', models.CharField(max_length=128)),
                ('codec', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='parsing.Codec')),
            ],
        ),
        migrations.CreateModel(
            name='Status',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=16, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timeshift', models.IntegerField(default=0)),
                ('url', models.CharField(max_length=128, unique=True)),
            ],
        ),
        migrations.AddField(
            model_name='result',
            name='status',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='parsing.Status'),
        ),
        migrations.AddField(
            model_name='result',
            name='task',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='parsing.Task'),
        ),
    ]
