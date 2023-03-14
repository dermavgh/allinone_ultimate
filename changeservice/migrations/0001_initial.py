# Generated by Django 4.1.7 on 2023-03-12 01:43

import changeservice.models
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Saved_boo',
            fields=[
                ('name', models.CharField(max_length=25, primary_key=True, serialize=False)),
                ('content', models.BooleanField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Saved_list',
            fields=[
                ('name', models.CharField(max_length=25, primary_key=True, serialize=False)),
                ('content', changeservice.models.ListField(default=[], null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Saved_str',
            fields=[
                ('name', models.CharField(max_length=25, primary_key=True, serialize=False)),
                ('content', models.CharField(default='', max_length=25, null=True)),
            ],
        ),
    ]