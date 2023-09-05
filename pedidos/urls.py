from django.urls import  path
from pedidos.views import index, list_mesa, add_mesa, del_mesa, edt_mesa, list_produtos, list_categoria, \
    add_categoria, del_categoria, edt_categoria, add_produto, del_produto, edt_produto, home, pedido_mesa, \
    realizar_pedido, del_pedido, gerar_pdf_pedido_comanda

urlpatterns = [
    path('index', index, name='index'),
    path('list_mesa', list_mesa, name='list_mesa'),
    path('add_mesa', add_mesa, name='add_mesa'),
    path('del_mesa/<int:mesas_id>', del_mesa, name='del_mesa'),
    path('edt_mesa/<int:mesas_id>', edt_mesa, name='edt_mesa'),
    path('list_categoria', list_categoria, name='list_categoria'),
    path('add_categoria', add_categoria, name='add_categoria'),
    path('del_categoria/<int:categorias_id>', del_categoria, name='del_categoria'),
    path('edt_categoria/<int:categorias_id>', edt_categoria, name='edt_categoria'),
    path('list_produtos/', list_produtos, name='list_produtos'),
    path('add_produto', add_produto, name='add_produto'),
    path('del_produto/<int:produtos_id>', del_produto, name='del_produto'),
    path('edt_produto/<int:produtos_id>', edt_produto, name='edt_produto'),
    path('home', home, name='home'),
    path('pedido_mesa/<int:numero_mesa>/', pedido_mesa, name='pedido_mesa'),
    path('realizar_pedido/<int:numero_mesa>/', realizar_pedido, name='realizar_pedido'),
    path('del_pedido/<int:pedido_id>', del_pedido, name='del_pedido'),
    path('gerar_pdf_pedido_comanda/<int:pedido_id>/', gerar_pdf_pedido_comanda, name='gerar_pdf_pedido_comanda')

]


