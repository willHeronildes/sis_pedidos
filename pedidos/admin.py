from django.contrib import admin

from .models import AddMesa, Categoria, Produto, Pedido

admin.site.register(AddMesa)
admin.site.register(Categoria)
admin.site.register(Produto)
admin.site.register(Pedido)
