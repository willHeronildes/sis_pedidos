from io import BytesIO

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse

from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Spacer

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


def home(request):
    mesas = AddMesa.objects.all()
    context = {'mesas': mesas}
    return render(request, 'pedidos/home.html', context)


def pedido_mesa(request, numero_mesa):
    try:
        mesa = AddMesa.objects.get(id=numero_mesa)
    except AddMesa.DoesNotExist:
        # Lide com a mesa inexistente
        return redirect('pagina_de_erro')

    categorias = Categoria.objects.all()
    pedidos = Pedido.objects.filter(mesa=mesa)  # Filtrar pedidos pela mesa

    produtos_pedidos = {}  # Dicionário para armazenar produtos por pedido
    for pedido in pedidos:
        produtos_pedidos[pedido.id] = pedido.produtos.all()

    context = {
        'categorias': categorias,
        'pedidos': pedidos,
        'mesa': mesa,  # Passar a mesa para o template
        'produtos_pedidos': produtos_pedidos,  # Passar os produtos por pedido para o template
    }

    if request.GET.get('categoria'):
        if request.method == 'GET':
            context['produtos'] = Produto.objects.filter(categoria__categoria__icontains=request.GET.get('categoria'))

    return render(request, 'pedidos/pedido_mesa.html', context)



def realizar_pedido(request, numero_mesa):
    try:
        mesa = AddMesa.objects.get(id=numero_mesa)
    except AddMesa.DoesNotExist:

        return redirect('pagina_de_erro')

    if request.method == 'POST':
        form = PedidoForm(request.POST)
        if form.is_valid():
            produtos_selecionados = form.cleaned_data['produtos']
            for produto in produtos_selecionados:
                pedido = Pedido.objects.create(mesa=mesa)
                pedido.produtos.add(produto)

            return redirect('pedido_mesa', numero_mesa=mesa.id)
    else:
        form = PedidoForm()

    return render(request, 'pedidos/pedido_mesa.html', {'form': form, 'mesa': mesa})

def del_pedido(request, pedido_id):
    pedido = Pedido.objects.get(id=pedido_id)
    pedido.delete()

    return redirect('pedido_mesa', numero_mesa=pedido.mesa.id)


def gerar_pdf_pedido_comanda(request, pedido_id):
    pedido = Pedido.objects.get(id=pedido_id)

    # Crie uma resposta HTTP com o tipo de conteúdo adequado para PDF
    response = HttpResponse(content_type='application/pdf')

    # Configurar o cabeçalho para indicar que o PDF deve ser exibido no navegador
    response['Content-Disposition'] = 'inline; filename="seu_arquivo.pdf"'

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []

    itens_pedido = pedido.produtos.all()

    data = [
        ["Produto", "Categoria"],
    ]

    for produto in itens_pedido:
        data.append([
            produto.nome_produto,
            produto.categoria if produto.categoria else "Sem categoria",
        ])

    table = Table(data, colWidths=[10 * cm, 5 * cm])
    table.setStyle(TableStyle([
        # ... (estilos da tabela)
    ]))
    elements.append(table)
    elements.append(Spacer(1, 20))

    doc.build(elements)
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)

    return response






