# Generated by Django 4.2.7 on 2024-05-03 16:23

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("app_users", "0002_alter_profile_profile_picture"),
    ]

    operations = [
        migrations.AlterField(
            model_name="profile",
            name="profile_picture",
            field=models.ImageField(
                default="profile_pics/ProfileBase.png", upload_to="profile_pics/"
            ),
        ),
    ]
