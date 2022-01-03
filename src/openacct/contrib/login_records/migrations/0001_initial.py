import openacct.contrib.login_records.models
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="LoginRecord",
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
                ("when", models.DateTimeField()),
                ("host", models.CharField(max_length=64)),
                ("service", models.CharField(max_length=32)),
                ("method", models.CharField(blank=True, max_length=32, null=True)),
                ("user", models.CharField(max_length=32)),
                ("fromhost", models.CharField(max_length=256)),
            ],
        ),
    ]
