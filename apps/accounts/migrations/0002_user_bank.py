from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0001_initial"),
        ("banks", "0003_hash_bank_api_keys"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="bank",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="operators",
                to="banks.bank",
            ),
        ),
    ]
