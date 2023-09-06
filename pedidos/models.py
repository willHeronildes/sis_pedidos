from django.db import models

class AddMesa(models.Model):
    numero = models.CharField(max_length=70)

    def __str__(self):
        return self.numero

class Categoria(models.Model):
    categoria = models.CharField(max_length=70)

    def __str__(self):
        return self.categoria

class Produto(models.Model):
    nome_produto = models.CharField(max_length=70)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, null=True)


    def __str__(self):
        return self.nome_produto

class Pedido(models.Model):
    mesa = models.ForeignKey(AddMesa, on_delete=models.CASCADE, null=True)
    produtos = models.ManyToManyField(Produto)
    ativo = models.BooleanField(default=False)

    def __str__(self):
        produtos = self.produtos.all()
        return ', '.join([f"{produto.nome_produto} - R$ {produto.valor}" for produto in produtos])







