# Generated by Django 5.0 on 2024-04-28 08:13

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("MBTI", "0005_useranswer_gender"),
    ]

    operations = [
        migrations.AlterField(
            model_name="useranswer",
            name="gender",
            field=models.CharField(
                choices=[("Male", "ชาย"), ("Female", "หญิง")], max_length=6
            ),
        ),
    ]
