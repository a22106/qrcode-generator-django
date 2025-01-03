# Generated by Django 4.2.16 on 2024-11-06 14:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="SiteSettings",
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
                        default="QR Code Generator - PiusDev",
                        max_length=255,
                        verbose_name="Title",
                    ),
                ),
                (
                    "description",
                    models.TextField(
                        default="Generate various types of QR codes easily and quickly.",
                        verbose_name="Description",
                    ),
                ),
                (
                    "keywords",
                    models.TextField(
                        default="QR Code, Generator, PiusDev",
                        max_length=255,
                        verbose_name="Keywords",
                    ),
                ),
            ],
            options={
                "verbose_name": "Site Settings",
                "verbose_name_plural": "Site Settings",
            },
        ),
        migrations.DeleteModel(
            name="Configuration",
        ),
    ]
