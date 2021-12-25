import openacct.contrib.token_auth.models
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="AuthToken",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("last_used", models.DateTimeField(blank=True, null=True)),
                ("expires", models.DateTimeField(blank=True, null=True)),
                ("name", models.CharField(max_length=32)),
                (
                    "token",
                    models.CharField(
                        default=openacct.contrib.token_auth.models.generate_token,
                        max_length=128,
                        unique=True,
                    ),
                ),
            ],
        ),
    ]
