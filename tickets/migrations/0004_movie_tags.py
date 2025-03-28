# Generated by Django 5.1.2 on 2025-03-15 10:22

import tickets.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tickets', '0003_remove_movie_tags'),
    ]

    operations = [
        migrations.AddField(
            model_name='movie',
            name='tags',
            field=models.JSONField(blank=True, default=tickets.models.default_empty_list),
        ),
    ]
