# Generated by Django 4.2.3 on 2023-07-26 02:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0009_textblock_is_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='textblock',
            name='grade',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
    ]