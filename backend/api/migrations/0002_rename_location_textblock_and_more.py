# Generated by Django 4.2.3 on 2023-07-18 00:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Location',
            new_name='TextBlock',
        ),
        migrations.RenameField(
            model_name='textblock',
            old_name='locationName',
            new_name='text',
        ),
        migrations.DeleteModel(
            name='Item',
        ),
    ]