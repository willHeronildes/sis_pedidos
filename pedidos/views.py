from decimal import Decimal

from io import BytesIO

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from datetime import datetime
import escpos
from escpos.printer import Dummy
from django.db.models import Sum



from .forms import AddMesaForm, CategoriaForm, ProdutoForm, PedidoForm
from .models import AddMesa, Categoria, Produto, Pedido


def index(request):
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'pedidos/index.html')


def list_mesa(request):
    mesas = AddMesa.objects.all()
    context = {'mesa': mesas}
    return render(request, 'mesas/list_mesa.html', context)


def add_mesa(request):
    if request.method == 'POST':
        form = AddMesaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('list_mesa')
    else:
        form = AddMesaForm()
    return render(request, 'mesas/add_mesa.html', {"form": form})


def del_mesa(request, mesas_id):
    mesa = AddMesa.objects.get(id=mesas_id)
    mesa.delete()
    return redirect('list_mesa')


def edt_mesa(request, mesas_id):
    mesa = AddMesa.objects.get(id=mesas_id)
    form = AddMesaForm(instance=mesa)

    if request.method == 'POST':
        form = AddMesaForm(request.POST, instance=mesa)
        if form.is_valid():
            form.save()
            return redirect('list_mesa')

    return render(request, 'mesas/edt_mesa.html', {"form": form, 'mesas_id': mesas_id})


def list_categoria(request):
    categorias = Categoria.objects.all()
    context = {'categoria': categorias}
    return render(request, 'categoria/list_categoria.html', context)


def add_categoria(request):
    if request.method == 'POST':
        form = CategoriaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('list_categoria')
    else:
        form = CategoriaForm()
    return render(request, 'categoria/add_categoria.html', {"form": form})


def del_categoria(request, categorias_id):
    categoria = Categoria.objects.get(id=categorias_id)
    categoria.delete()
    return redirect('list_categoria')


def edt_categoria(request, categorias_id):
    categoria = Categoria.objects.get(id=categorias_id)
    form = CategoriaForm(instance=categoria)

    if request.method == 'POST':
        form = CategoriaForm(request.POST, instance=categoria)
        if form.is_valid():
            form.save()
            return redirect('list_categoria')

    return render(request, 'categoria/edt_categoria.html', {"form": form, 'categorias_id': categorias_id})


def list_produtos(request):
    if request.method == 'GET':
        produto_id = request.GET.get('produto_id')
        if produto_id:
            try:
                produto = Produto.objects.get(id=produto_id)
                response_data = {
                    'id': produto.id,
                    'nome_produto': produto.nome_produto,
                    'preco': produto.valor,
                }
                return JsonResponse(response_data)
            except Produto.DoesNotExist:
                return JsonResponse({'error': 'Produto não encontrado.'})

    produtos = Produto.objects.all()
    context = {'produtos': produtos}
    return render(request, 'produtos/list_produtos.html', context)



def add_produto(request):
    if request.method == 'POST':
        form = ProdutoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('list_produtos')
    else:
        form = ProdutoForm()
    return render(request, 'produtos/add_produto.html', {"form": form})


def del_produto(request, produtos_id):
    produto = Produto.objects.get(id=produtos_id)
    produto.delete()
    return redirect('list_produtos')


def edt_produto(request, produtos_id):
    produto = Produto.objects.get(id=produtos_id)
    form = ProdutoForm(instance=produto)

    if request.method == 'POST':
        form = ProdutoForm(request.POST, instance=produto)
        if form.is_valid():
            form.save()
            return redirect('list_produtos')

    return render(request, 'produtos/edt_produto.html', {"form": form, 'produtos_id': produtos_id})



def pedido_mesa(request, numero_mesa):
    context = {}
    pedido_ativo = Pedido.objects.get_or_create(mesa_id=numero_mesa, ativo=True)[0]
    context['pedido_ativo'] = pedido_ativo
    produtos_mesa = Produto.objects.filter(pedido=pedido_ativo.id)
    context['produtos_mesa'] = produtos_mesa

    # Calcular o valor total somando os preços dos produtos
    valor_total = sum(produto.valor for produto in produtos_mesa)
    context['valor_total'] = valor_total


    categorias = Categoria.objects.all()
    context['categorias'] = categorias

    if request.GET.get('categoria'):
        if request.method == 'GET':
            context['produtos'] = Produto.objects.filter(categoria__categoria__icontains=request.GET.get('categoria'))

    # Estou obtendo todos os ids de mesas que estão ativas
    mesas_com_pedidos_ativos = list(Pedido.objects.filter(ativo=True).values_list('mesa__id', flat=True))

    # Aqui eu armazeno em uma lista para pode acessar na view home
    request.session['mesas_com_pedidos_ativos'] = mesas_com_pedidos_ativos

    if request.method == 'POST':
        desconto = Decimal(request.POST.get('desconto', 0))
        pedido_ativo.desconto = desconto
        pedido_ativo.save()

        valor_final = valor_total - desconto
        valor_percentual = valor_final * Decimal('0.1')
        valor_final2 = valor_final + valor_percentual
        context['valor_final'] = valor_final
        context['valor_percentual'] = valor_percentual
        context['valor_final2'] = valor_final2

    return render(request, 'pedidos/pedido_mesa.html', context)



def home(request):
    mesas = AddMesa.objects.all()

    # Acesso a lista de mesas ativas
    mesas_com_pedidos_ativos = request.session.get('mesas_com_pedidos_ativos', [])

    context = {'mesas': mesas, 'mesas_com_pedidos_ativos': mesas_com_pedidos_ativos}
    return render(request, 'pedidos/home.html', context)



def realizar_pedido(request, pedido_id):
    context = {}
    pedido_ativo = Pedido.objects.get(id=pedido_id)
    if request.method == 'POST':
        form = PedidoForm(request.POST)
        if form.is_valid():
            produtos_selecionados = form.cleaned_data['produtos']
            for produto in produtos_selecionados:
                pedido_ativo.produtos.add(produto)
                pedido_ativo.save()
    return redirect('pedido_mesa', numero_mesa=pedido_ativo.mesa.id)


def finalizar_mesa(request, pedido_id):
    pedido_ativo = get_object_or_404(Pedido, id=pedido_id)

    # Removendo o ID da mesa da lista mesas_com_pedidos_ativos na sessão
    mesa_id = pedido_ativo.mesa.id
    mesas_com_pedidos_ativos = request.session.get('mesas_com_pedidos_ativos', [])
    if mesa_id in mesas_com_pedidos_ativos:
        mesas_com_pedidos_ativos.remove(mesa_id)
        request.session['mesas_com_pedidos_ativos'] = mesas_com_pedidos_ativos

    pedido_ativo.ativo = False
    pedido_ativo.save()
    return redirect('home')


def del_pedido(request, produto_id, pedido_id):
    pedido_ativo = Pedido.objects.get(id=pedido_id)
    produto = Produto.objects.get(id=produto_id)
    pedido_ativo.produtos.remove(produto)

    return redirect('pedido_mesa', numero_mesa=pedido_ativo.mesa.id)


def imprimir_comanda(request, pedido_id, mesa_id):
    # Recupere os dados do pedido com base no pedido_id
    pedido = get_object_or_404(Pedido, id=pedido_id)
    itens_pedido = pedido.produtos.all()

    # Crie o conteúdo do arquivo de texto
    comanda_text = f"Comanda da Mesa #{mesa_id}\n\n"

    for index, produto in enumerate(itens_pedido, start=1):
        comanda_text += f"Item #{index}:\n"
        comanda_text += f"Produto: {produto.nome_produto}\n"
        comanda_text += f"Categoria: {produto.categoria}\n"
        comanda_text += f"-------------------------\n"

    comanda_text += "\n\f"

    # Crie a resposta HTTP com o tipo de conteúdo adequado para TXT
    response = HttpResponse(comanda_text, content_type='text/plain')

    # Configurar o cabeçalho para fazer o download do arquivo TXT
    response['Content-Disposition'] = f'inline; filename="comanda_pedido_{pedido_id}.txt"'

    return response


def imprimir_conta(request, pedido_id, mesa_id):
    # Recupere os dados do pedido com base no pedido_id
    pedido = get_object_or_404(Pedido, id=pedido_id)
    itens_pedido = pedido.produtos.all()

    # Crie o conteúdo do arquivo de texto
    comanda_text = f"HERONILDES RESTAURANTE LTDA"
    comanda_text = f"Comanda da Mesa #{mesa_id}\n\n"

    for index, produto in enumerate(itens_pedido, start=1):
        comanda_text += f"Item #{index}:\n"
        comanda_text += f"Produto: {produto.nome_produto}\n"
        comanda_text += f"Categoria: {produto.categoria}\n"
        comanda_text += f"-------------------------\n"
    comanda_text += "\n"
    comanda_text += "\x1D\x56\x00"

        # Crie a resposta HTTP com o tipo de conteúdo adequado para TXT
    response = HttpResponse(comanda_text, content_type='text/plain')

    # Configurar o cabeçalho para fazer o download do arquivo TXT
    response['Content-Disposition'] = f'inline; filename="comanda_pedido_{pedido_id}.txt"'

    return response


from decimal import Decimal
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from datetime import datetime


def imprimir_conta(request, pedido_id, mesa_id):
    # Recupere os dados do pedido com base no pedido_id
    pedido = get_object_or_404(Pedido, id=pedido_id)
    itens_pedido = pedido.produtos.all()

    # Informações do restaurante
    restaurante_info = """
HERONILDES RESTAURANTE LTDA
Rodolfo Garcia, 2020 Lagoa Nova
Natal-RN
Telefone: 8421301913
CNPJ: 44864862000138
-------------------------------------------------------
"""

    # Informações do cupom fiscal
    cupom_info = f"""
Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

                    CUPOM NAO FISCAL 
-------------------------------------------------------
{"DESCRICAO":<30}{"Valor":<10}
"""

    # Itens do pedido
    for index, produto in enumerate(itens_pedido, start=1):
        cupom_info += f"{produto.nome_produto:<30} R$ {produto.valor:.2f}\n"

    # Cálculos do subtotal, desconto, gorjeta e total
    subtotal = sum(produto.valor for produto in itens_pedido)
    desconto_cupom = pedido.desconto  # Adicione aqui o valor do desconto do cupom
    subtotal_com_desconto = subtotal - desconto_cupom
    gorjeta_sugerida = subtotal_com_desconto * Decimal('0.1')
    total = subtotal_com_desconto + gorjeta_sugerida

    # Adiciona informações de subtotal, desconto, gorjeta e total ao cupom
    cupom_info += f"""



                            SubTotal: R$ {subtotal:.2f}
                            Desconto Cupom: R$ {desconto_cupom:.2f}
                            Sub Total c/ desconto: R$ {subtotal_com_desconto:.2f}
                            Gorjeta Sugerida: R$ {gorjeta_sugerida:.2f}
                            Total: R$ {total:.2f}
"""

    # Agradecimento
    agradecimento = """
Obrigado, Volte sempre!
"""

    # Combine todas as informações
    comanda_text = restaurante_info + cupom_info + agradecimento

    # Crie a resposta HTTP com o tipo de conteúdo adequado para TXT
    response = HttpResponse(comanda_text, content_type='text/plain')

    # Configurar o cabeçalho para fazer o download do arquivo TXT
    response['Content-Disposition'] = f'inline; filename="conta_pedido_{pedido_id}.txt"'

    return response
















