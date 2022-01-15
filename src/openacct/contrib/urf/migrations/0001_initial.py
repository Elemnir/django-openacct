from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def load_default_email_template(apps, schema_editor):
    EmailTemplate = apps.get_model('user_requests', 'EmailTemplate')
    EmailTemplate.objects.create(pk=1, name='Default', default_from=settings.EMAIL_HOST_USER, 
        subject='Your Request has been Processed',
        body='Your request:\n\n\t{{ request.id }}: {{ request.description }}\n\nhas been approved and processed.'
    )


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='EmailTemplate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('name', models.CharField(max_length=64)),
                ('default_from', models.CharField(max_length=64)),
                ('subject', models.CharField(max_length=64)),
                ('body', models.TextField()),
            ],
        ),
        migrations.RunPython(load_default_email_template),
        migrations.CreateModel(
            name='Request',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('submitted', models.DateTimeField(auto_now_add=True)),
                ('requester', models.CharField(max_length=32)),
                ('confirmed', models.BooleanField(blank=True, default=False)),
                ('autoprocess', models.BooleanField(blank=True, default=True)),
                ('autonotify', models.BooleanField(blank=True, default=True)),
                ('description', models.CharField(blank=True, default='', max_length=512)),
                ('status', models.CharField(blank=True, choices=[('NEW', 'NEW'), ('PENDING', 'PENDING'), ('APPROVED', 'APPROVED'), ('DECLINED', 'DECLINED'), ('PROCESSING', 'PROCESSING'), ('PROCESSED', 'PROCESSED'), ('FAILED', 'FAILED'), ('CANCELLED', 'CANCELLED')], default='NEW', max_length=16)),
                ('notification', models.ForeignKey(blank=True, default=1, null=True, on_delete=django.db.models.deletion.SET_DEFAULT, to='urf.emailtemplate')),
            ],
        ),
        migrations.CreateModel(
            name='RequestLogEntry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('logged', models.DateTimeField(auto_now_add=True)),
                ('text', models.CharField(max_length=128)),
                ('request', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='urf.request')),
            ],
        ),
    ]
