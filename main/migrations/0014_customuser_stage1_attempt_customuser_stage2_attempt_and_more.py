# Generated by Django 5.1.2 on 2025-02-22 15:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0013_customuser_stage1_time_customuser_stage2_time_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='stage1_attempt',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='customuser',
            name='stage2_attempt',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='customuser',
            name='stage3_attempt',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='customuser',
            name='stage4_attempt',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='customuser',
            name='stage5_attempt',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='customuser',
            name='stage6_attempt',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='customuser',
            name='stage7_attempt',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='customuser',
            name='stage8_attempt',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
