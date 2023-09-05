from django import forms
from .models import AddMesa, Categoria, Produto, Pedido


class AddMesaForm(forms.ModelForm):
    class Meta:
        model = AddMesa
        fields = ['numero']


class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields =['categoria']


class ProdutoForm(forms.ModelForm):

    class Meta:
        model = Produto
        fields = [
            'nome_produto',
            'valor',
            'categoria',
        ]


class PedidoForm(forms.ModelForm):

    class Meta:
        model = Pedido
        fields = [
            'produtos',
        ]
