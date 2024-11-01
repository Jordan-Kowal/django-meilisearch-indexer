# Generated by Django 4.2.16 on 2024-11-01 15:56

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []  # type: ignore

    operations = [
        migrations.CreateModel(
            name="User",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("first_name", models.CharField(max_length=255)),
                ("last_name", models.CharField(max_length=255)),
                ("email", models.CharField(max_length=255)),
                ("is_active", models.BooleanField()),
                ("age", models.IntegerField()),
            ],
        ),
    ]