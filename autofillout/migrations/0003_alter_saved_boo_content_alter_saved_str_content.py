# Generated by Django 4.0.5 on 2022-06-25 05:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('autofillout', '0002_remove_saved_boo_id_remove_saved_list_id_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='saved_boo',
            name='content',
            field=models.BooleanField(null=True),
        ),
        migrations.AlterField(
            model_name='saved_str',
            name='content',
            field=models.CharField(default='', max_length=25),
        ),
    ]
