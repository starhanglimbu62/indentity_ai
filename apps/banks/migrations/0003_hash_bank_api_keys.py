import hashlib

from django.db import migrations, models


def hash_existing_api_keys(apps, schema_editor):
    Bank = apps.get_model("banks", "Bank")
    database = schema_editor.connection.alias
    for bank in Bank.objects.using(database).all().iterator():
        digest = hashlib.sha256(bank.api_key.encode("utf-8")).hexdigest()
        Bank.objects.using(database).filter(pk=bank.pk).update(
            api_key_hash=digest
        )


class Migration(migrations.Migration):
    dependencies = [
        ("banks", "0002_bank_webhook_url_alter_bank_api_key"),
    ]

    operations = [
        migrations.AddField(
            model_name="bank",
            name="api_key_hash",
            field=models.CharField(max_length=64, null=True),
        ),
        migrations.RunPython(
            hash_existing_api_keys,
            reverse_code=migrations.RunPython.noop,
        ),
        migrations.AlterField(
            model_name="bank",
            name="api_key_hash",
            field=models.CharField(max_length=64, unique=True),
        ),
        migrations.RemoveField(
            model_name="bank",
            name="api_key",
        ),
    ]
