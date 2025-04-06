# contratos/models.py
from django.db import models
from datetime import timedelta

class TipoContrato(models.Model):
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True)
    template_pdf = models.CharField(max_length=100)  # Nome do template para gerar o PDF
    
    def __str__(self):
        return self.nome

class Contrato(models.Model):
    tipo = models.ForeignKey(TipoContrato, on_delete=models.CASCADE)
    data_criacao = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        if hasattr(self, 'contrato_locacao'):
            return f"Contrato de Locação: {self.contrato_locacao.nome_locatario}"
        return f"Contrato #{self.id}"

class ContratoLocacao(models.Model):
    contrato = models.OneToOneField(Contrato, on_delete=models.CASCADE, related_name='contrato_locacao')
    
    # Dados do Locador
    nome_locador = models.CharField(max_length=100)
    nacionalidade_locador = models.CharField(max_length=50)
    estado_civil_locador = models.CharField(max_length=50)
    profissao_locador = models.CharField(max_length=50)
    rg_locador = models.CharField(max_length=20)
    cpf_locador = models.CharField(max_length=14)
    endereco_locador = models.CharField(max_length=200)
    
    # Dados do Locatário
    nome_locatario = models.CharField(max_length=100)
    nacionalidade_locatario = models.CharField(max_length=50)
    rg_locatario = models.CharField(max_length=20)
    cpf_locatario = models.CharField(max_length=14)
    
    # Dados do Imóvel
    logradouro = models.CharField(max_length=100)
    numero = models.CharField(max_length=10)
    complemento = models.CharField(max_length=100)
    lote = models.CharField(max_length=50)
    quadra = models.CharField(max_length=50, blank=True)
    casa = models.CharField(max_length=50, blank=True)
    bairro = models.CharField(max_length=100)
    cidade = models.CharField(max_length=100)
    estado = models.CharField(max_length=2, default="RJ")
    cep = models.CharField(max_length=10)
    
    # Condições do Contrato
    valor_aluguel = models.DecimalField(max_digits=10, decimal_places=2)
    valor_aluguel_extenso = models.CharField(max_length=100)
    data_inicio = models.DateField()
    dia_pagamento = models.IntegerField()
    
    def __str__(self):
        return f"Contrato de Locação: {self.nome_locatario} - {self.logradouro}"
    
    def data_fim(self):
        # Automaticamente calcula a data de término (12 meses após início)
        return self.data_inicio + timedelta(days=365)
    
    def data_primeiro_pagamento(self):
        # Calcula a data do primeiro pagamento
        return self.data_inicio.replace(day=self.dia_pagamento)

# Aqui você pode adicionar mais modelos de contratos no futuro, como:
# class ContratoVenda(models.Model):
#     contrato = models.OneToOneField(Contrato, on_delete=models.CASCADE, related_name='contrato_venda')
#     ...