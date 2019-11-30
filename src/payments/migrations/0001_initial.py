"""Initial migrations."""

from django.db import migrations, models


class Migration(migrations.Migration):
    """Django database migration."""

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Account",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=512, unique=True)),
                ("balance", models.DecimalField(decimal_places=2, max_digits=7)),
                (
                    "currency",
                    models.CharField(
                        choices=[("USD", "USA USD"), ("UAH", "Ukraine UAH"), ("RUB", "Russia RUB")], max_length=50
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={"db_table": "account", "managed": False, "ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="Payment",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("amount", models.DecimalField(decimal_places=2, max_digits=7)),
                (
                    "direction",
                    models.CharField(
                        choices=[("outgoing", "outgoing (-)"), ("incoming", "incoming (+)")], max_length=8
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={"db_table": "payment", "managed": False, "ordering": ["-created_at"]},
        ),
    ]
