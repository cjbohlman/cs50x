# Generated by Django 3.1 on 2020-08-09 18:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('flights', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='airport',
            name='country',
            field=models.CharField(default='', max_length=64),
        ),
    ]