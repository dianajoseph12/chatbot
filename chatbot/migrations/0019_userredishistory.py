# Generated by Django 5.1.1 on 2024-09-25 04:31

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chatbot', '0018_alter_upload_file_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserRedisHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('redis_key', models.CharField(default='cfc52d89-a4be-45f1-9874-1f62032676ba', max_length=255, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='redis_histories', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
