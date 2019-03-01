# Generated by Django 2.1.7 on 2019-02-21 18:05

from django.conf import settings
import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('db', '0018_auto_20190212_2302'),
    ]

    operations = [
        migrations.CreateModel(
            name='CI',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('config', django.contrib.postgres.fields.jsonb.JSONField(blank=True, help_text='The ci config schema.', null=True)),
                ('code_reference', models.ForeignKey(blank=True, help_text="The ci's last code ref used.", null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='db.CodeReference')),
                ('project', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='ci', to='db.Project')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AlterField(
            model_name='experimentgroupstatus',
            name='status',
            field=models.CharField(blank=True, choices=[('created', 'created'), ('running', 'running'), ('done', 'done'), ('failed', 'failed'), ('stopping', 'stopping'), ('stopped', 'stopped')], default='created', max_length=64, null=True),
        ),
    ]
