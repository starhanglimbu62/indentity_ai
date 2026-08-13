from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AuditEvent',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('event_type', models.CharField(choices=[('DOCUMENT_UPLOADED', 'Document uploaded'), ('OCR_STARTED', 'OCR started'), ('OCR_COMPLETED', 'OCR completed'), ('IDENTITY_CHECK_STARTED', 'Identity check started'), ('IDENTITY_CHECK_COMPLETED', 'Identity check completed'), ('IDENTITY_VERIFICATION_FAILED', 'Identity verification failed'), ('CREDENTIAL_CREATED', 'Credential created'), ('DOCUMENT_DELETED', 'Document deleted')], max_length=60)),
                ('entity_type', models.CharField(blank=True, default='', max_length=50)),
                ('entity_id', models.UUIDField(blank=True, null=True)),
                ('metadata', models.JSONField(blank=True, default=dict)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='audit_events', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
