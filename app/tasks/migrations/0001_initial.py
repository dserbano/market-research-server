# Generated by Django 3.2.3 on 2021-08-08 23:44

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('from_keywords', models.CharField(max_length=1000)),
                ('language', models.CharField(max_length=1000)),
                ('location', models.CharField(max_length=1000)),
                ('timestamp', models.DateTimeField()),
                ('keywords', models.JSONField()),
                ('businesses', models.JSONField()),
                ('products', models.JSONField()),
                ('search_volume', models.JSONField()),
                ('forecasts_search_volume', models.JSONField()),
                ('clusters_products', models.JSONField()),
            ],
            options={
                'verbose_name': 'Task',
                'verbose_name_plural': 'Tasks',
                'db_table': 'tasks',
            },
        ),
    ]