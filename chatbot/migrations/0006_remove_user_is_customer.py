# Generated by Django 5.1.1 on 2024-09-20 10:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('chatbot', '0005_alter_upload_file_name'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='is_customer',
        ),
    ]
