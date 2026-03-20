from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0007_remove_grievance_against_entity_name_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='aadhaar_number',
            field=models.CharField(blank=True, max_length=12, null=True),
        ),
    ]
