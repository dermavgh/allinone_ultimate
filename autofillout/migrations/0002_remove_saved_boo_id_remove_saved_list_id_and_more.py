# Generated by Django 4.0.5 on 2022-06-25 05:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('autofillout', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='saved_boo',
            name='id',
        ),
        migrations.RemoveField(
            model_name='saved_list',
            name='id',
        ),
        migrations.RemoveField(
            model_name='saved_str',
            name='id',
        ),
        migrations.AlterField(
            model_name='saved_boo',
            name='name',
            field=models.CharField(max_length=25, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='saved_list',
            name='name',
            field=models.CharField(max_length=25, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='saved_str',
            name='name',
            field=models.CharField(max_length=25, primary_key=True, serialize=False),
        ),
    ]
