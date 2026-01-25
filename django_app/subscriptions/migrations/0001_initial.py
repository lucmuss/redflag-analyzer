# Generated manually for Subscriptions

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Subscription',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tier', models.CharField(choices=[('free', 'Free Tier (3 Analysen)'), ('premium', 'Premium (€20 - Unbegrenzt)')], default='free', max_length=20)),
                ('is_active', models.BooleanField(default=False)),
                ('started_at', models.DateTimeField(blank=True, null=True)),
                ('expires_at', models.DateTimeField(blank=True, null=True)),
                ('stripe_customer_id', models.CharField(blank=True, max_length=255, null=True)),
                ('stripe_subscription_id', models.CharField(blank=True, max_length=255, null=True)),
                ('free_analyses_used', models.IntegerField(default=0)),
                ('free_analyses_limit', models.IntegerField(default=3)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='subscription', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'subscriptions',
            },
        ),
        migrations.CreateModel(
            name='CreditPurchase',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('credits_purchased', models.IntegerField(default=1)),
                ('amount_paid', models.DecimalField(decimal_places=2, max_digits=6)),
                ('stripe_payment_intent_id', models.CharField(blank=True, max_length=255, null=True)),
                ('payment_status', models.CharField(choices=[('pending', 'Pending'), ('completed', 'Completed'), ('failed', 'Failed'), ('refunded', 'Refunded')], default='pending', max_length=20)),
                ('purchased_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='credit_purchases', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'credit_purchases',
                'ordering': ['-purchased_at'],
            },
        ),
        migrations.AddIndex(
            model_name='subscription',
            index=models.Index(fields=['user', 'tier'], name='subscripti_user_id_d8e6a7_idx'),
        ),
        migrations.AddIndex(
            model_name='subscription',
            index=models.Index(fields=['is_active'], name='subscripti_is_acti_f9c4b2_idx'),
        ),
        migrations.AddIndex(
            model_name='creditpurchase',
            index=models.Index(fields=['user', 'payment_status'], name='credit_purc_user_id_a3b2c4_idx'),
        ),
    ]
