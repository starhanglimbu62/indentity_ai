from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('verification', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='verificationrequest',
            name='challenge',
            field=models.CharField(max_length=128, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='verificationrequest',
            name='challenge_expires_at',
            field=models.DateTimeField(null=True, blank=True),
        ),
    ]
