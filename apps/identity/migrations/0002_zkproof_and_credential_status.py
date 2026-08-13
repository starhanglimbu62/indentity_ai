from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('identity', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='verifiablecredential',
            name='status',
            field=models.CharField(default='ACTIVE', max_length=20, choices=[('ACTIVE', 'Active'), ('EXPIRED', 'Expired'), ('REVOKED', 'Revoked')]),
        ),
        migrations.CreateModel(
            name='ZKProof',
            fields=[
                ('id', models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)),
                ('verification_request_id', models.UUIDField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('expires_at', models.DateTimeField(blank=True, null=True)),
                ('status', models.CharField(default='REQUESTED', max_length=20)),
                ('proof_digest', models.CharField(blank=True, null=True, max_length=128)),
            ],
        ),
        migrations.AddIndex(
            model_name='zkproof',
            index=models.Index(fields=['verification_request_id'], name='identity_zk_verreq_idx'),
        ),
    ]
