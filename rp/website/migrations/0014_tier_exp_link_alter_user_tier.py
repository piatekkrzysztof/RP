# Generated by Django 4.2.5 on 2023-09-22 13:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0013_alter_user_tier'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tier',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField()),
                ('thumbnail_s_height', models.IntegerField()),
                ('thumbnail_m_height', models.IntegerField(null=True)),
                ('orginal_link', models.BooleanField(default=False)),
                ('allow_links', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='exp_link',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('duration', models.DurationField()),
                ('image', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='website.image')),
            ],
        ),
        migrations.AlterField(
            model_name='user',
            name='tier',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='website.tier'),
        ),
    ]