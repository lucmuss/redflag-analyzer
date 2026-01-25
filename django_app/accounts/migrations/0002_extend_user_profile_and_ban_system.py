# Generated migration for extended UserProfile and Ban System

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        # Remove old age field, add birthdate
        migrations.RemoveField(
            model_name='userprofile',
            name='age',
        ),
        migrations.AddField(
            model_name='userprofile',
            name='birthdate',
            field=models.DateField(blank=True, help_text='Geburtsdatum für Altersberechnung', null=True),
        ),
        
        # Add ban fields to UserProfile
        migrations.AddField(
            model_name='userprofile',
            name='is_banned',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='banned_reason',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='banned_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        
        # Create BannedIP model
        migrations.CreateModel(
            name='BannedIP',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ip_address', models.GenericIPAddressField(db_index=True, unique=True)),
                ('reason', models.TextField()),
                ('banned_at', models.DateTimeField(auto_now_add=True)),
                ('banned_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='banned_ips', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'banned_ips',
                'ordering': ['-banned_at'],
            },
        ),
        
        # Create BannedEmail model
        migrations.CreateModel(
            name='BannedEmail',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(db_index=True, max_length=254, unique=True)),
                ('reason', models.TextField()),
                ('banned_at', models.DateTimeField(auto_now_add=True)),
                ('banned_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='banned_emails', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'banned_emails',
                'ordering': ['-banned_at'],
            },
        ),
    ]
