# Generated by Django 4.2.3 on 2023-07-18 18:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_user_textblock_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='grade',
            field=models.IntegerField(),
        ),
    ]