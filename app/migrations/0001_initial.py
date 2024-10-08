# Generated by Django 5.1.1 on 2024-09-27 06:56

import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='StockData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ticker', models.CharField(max_length=15, unique=True)),
                ('open_price', models.DecimalField(decimal_places=2, max_digits=12)),
                ('close_price', models.DecimalField(decimal_places=2, max_digits=12)),
                ('high', models.DecimalField(decimal_places=2, max_digits=12)),
                ('low', models.DecimalField(decimal_places=2, max_digits=12)),
                ('volume', models.BigIntegerField()),
                ('timestamp', models.DateTimeField()),
            ],
            options={
                'ordering': ['-timestamp'],
            },
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('user_id', models.CharField(default=uuid.UUID('3dbaa3bd-ec13-4b7a-b8fa-e49b62ecafe6'), max_length=36, primary_key=True, serialize=False)),
                ('username', models.CharField(max_length=50, unique=True)),
                ('balance', models.DecimalField(decimal_places=2, max_digits=12)),
            ],
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('transaction_id', models.CharField(default=uuid.UUID('9ca89d9e-a888-4572-bcbe-aed21f0065d7'), max_length=36, primary_key=True, serialize=False)),
                ('ticker', models.CharField(max_length=15)),
                ('transaction_type', models.CharField(choices=[('buy', 'Buy'), ('sell', 'Sell')], max_length=4)),
                ('transaction_volume', models.IntegerField()),
                ('transaction_price', models.DecimalField(decimal_places=2, max_digits=12)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transactions', to='app.user')),
            ],
            options={
                'ordering': ['-timestamp'],
            },
        ),
    ]
