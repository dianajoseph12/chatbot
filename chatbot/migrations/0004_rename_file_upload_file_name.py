# Generated by Django 5.1.1 on 2024-09-19 08:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('chatbot', '0003_alter_upload_file'),
    ]

    operations = [
        migrations.RenameField(
            model_name='upload',
            old_name='file',
            new_name='file_name',
        ),
    ]
