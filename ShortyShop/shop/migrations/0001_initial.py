# Generated by Django 5.1.1 on 2025-02-01 07:27

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='Nombre del Producto')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Descripción')),
                ('price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Precio')),
                ('stock', models.PositiveIntegerField(default=0, verbose_name='Stock Disponible')),
                ('image', models.ImageField(blank=True, null=True, upload_to='products/', verbose_name='Imagen del Producto')),
                ('category', models.CharField(choices=[('Zapatillas', 'Zapatillas'), ('Ropa', 'Ropa'), ('Accesorios', 'Accesorios')], default='Zapatillas', max_length=50, verbose_name='Categoría')),
                ('gender', models.CharField(choices=[('Hombre', 'Hombre'), ('Mujer', 'Mujer'), ('Niños', 'Niños'), ('Unisex', 'Unisex')], default='Unisex', max_length=50, verbose_name='Género')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Producto',
                'verbose_name_plural': 'Productos',
            },
        ),
        migrations.CreateModel(
            name='Cart',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='CartItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField(default=1)),
                ('cart', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='shop.cart')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shop.product')),
            ],
        ),
    ]
