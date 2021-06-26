# Generated by Django 3.0.5 on 2021-06-25 21:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='review',
            name='score',
            field=models.PositiveSmallIntegerField(),
        ),
        migrations.AlterField(
            model_name='titles',
            name='genre',
            field=models.ManyToManyField(blank=True, related_name='titles', to='api.Genres'),
        ),
    ]
