# Generated by Django 4.0.5 on 2022-07-04 07:31

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='do_not_delete',
            fields=[
                ('name', models.CharField(max_length=25, primary_key=True, serialize=False)),
                ('content', models.CharField(default='', max_length=25, null=True)),
            ],
        ),
    ]
