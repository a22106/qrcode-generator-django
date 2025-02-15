# Generated by Django 5.1.5 on 2025-02-05 17:46

from django.db import migrations

def populate_profile(apps, schema_editor):
    Profile = apps.get_model("accounts", "Profile")
    User = apps.get_model("accounts", "User")
    
    for user in User.objects.all():
        # profile's full_name is same as user's username
        Profile.objects.get_or_create(user=user, full_name=user.username)


def reverse_populate(apps, schema_editor):
    pass



    
class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0004_remove_user_email_verification_token_user_otp_and_more"),
    ]

    operations = [
        migrations.RunPython(populate_profile, reverse_populate),
    ]
