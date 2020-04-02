# Generated by Django 3.0.2 on 2020-04-02 05:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0014_post_is_unlisted'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='visibility',
            field=models.CharField(choices=[('PUBLIC', 'PUBLIC'), ('FOAF', 'FOAF'), ('FRIENDS', 'FRIENDS'), ('PRIVATE', 'PRIVATE'), ('SERVERONLY', 'SERVERONLY')], default='PUBLIC', max_length=10),
        ),
    ]