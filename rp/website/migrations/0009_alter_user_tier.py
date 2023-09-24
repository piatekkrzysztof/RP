# Generated by Django 4.2.5 on 2023-09-20 11:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0008_alter_user_tier'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='tier',
            field=models.IntegerField(choices=[(1, 'Basic'), (2, 'Premium'), (3, 'Enterprise')], default=0),
        ),
    ]
