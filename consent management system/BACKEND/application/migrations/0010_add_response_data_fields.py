# Generated migration for adding response data fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0009_remove_user_aadhaar_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='consentrequest',
            name='principal_response_data',
            field=models.JSONField(blank=True, default=dict, help_text='Data provided by principal when accepting the request'),
        ),
        migrations.AddField(
            model_name='consent',
            name='provided_data',
            field=models.JSONField(blank=True, default=dict, help_text='Actual data provided by principal (encrypted/secured)'),
        ),
    ]
