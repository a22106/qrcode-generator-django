# Generated by Django 4.2.16 on 2024-11-06 13:20

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Configuration",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "title",
                    models.CharField(
                        default="QR Code Generator - PiusDev", max_length=255
                    ),
                ),
                (
                    "description",
                    models.TextField(
                        default="Generate various types of QR codes easily and quickly."
                    ),
                ),
                ("keywords", models.TextField(default="QR Code, Generator, PiusDev")),
            ],
        ),
    ]
