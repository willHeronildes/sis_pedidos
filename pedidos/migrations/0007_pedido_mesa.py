# Generated by Django 4.2.1 on 2023-07-21 12:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('pedidos', '0006_remove_pedido_pedido_pedido_produtos'),
    ]

    operations = [
        migrations.AddField(
            model_name='pedido',
            name='mesa',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='pedidos.addmesa'),
        ),
    ]
