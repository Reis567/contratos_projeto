from django.contrib import admin
from django.utils.html import format_html
from .models import TipoContrato, Contrato, ContratoLocacao

class ContratoLocacaoInline(admin.StackedInline):
    model = ContratoLocacao
    can_delete = False
    verbose_name_plural = 'Detalhes do Contrato de Locação'
    fieldsets = (
        ('Dados do Locador', {
            'fields': (
                ('nome_locador', 'cpf_locador', 'rg_locador'),
                ('nacionalidade_locador', 'estado_civil_locador', 'profissao_locador'),
                'endereco_locador',
            )
        }),
        ('Dados do Locatário', {
            'fields': (
                ('nome_locatario', 'cpf_locatario', 'rg_locatario'),
                'nacionalidade_locatario',
            )
        }),
        ('Dados do Imóvel', {
            'fields': (
                ('logradouro', 'numero', 'complemento'),
                ('lote', 'quadra', 'casa'),
                ('bairro', 'cidade', 'estado', 'cep'),
            )
        }),
        ('Condições do Contrato', {
            'fields': (
                ('valor_aluguel', 'valor_aluguel_extenso'),
                ('data_inicio', 'dia_pagamento'),
            )
        }),
    )

@admin.register(TipoContrato)
class TipoContratoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'descricao_resumida', 'template_pdf')
    search_fields = ('nome', 'descricao')
    
    def descricao_resumida(self, obj):
        if len(obj.descricao) > 100:
            return f"{obj.descricao[:100]}..."
        return obj.descricao
    
    descricao_resumida.short_description = 'Descrição'

@admin.register(Contrato)
class ContratoAdmin(admin.ModelAdmin):
    list_display = ('id', 'tipo_contrato', 'pessoa_envolvida', 'imovel', 'valor', 'data_criacao_formatada', 'acoes')
    list_filter = ('tipo', 'data_criacao')
    search_fields = ('contrato_locacao__nome_locador', 'contrato_locacao__nome_locatario', 'contrato_locacao__logradouro', 'contrato_locacao__bairro', 'contrato_locacao__cidade')
    date_hierarchy = 'data_criacao'
    inlines = [ContratoLocacaoInline]
    
    def tipo_contrato(self, obj):
        return obj.tipo.nome
    
    def pessoa_envolvida(self, obj):
        if hasattr(obj, 'contrato_locacao'):
            return f"Locatário: {obj.contrato_locacao.nome_locatario}"
        return "N/A"
    
    def imovel(self, obj):
        if hasattr(obj, 'contrato_locacao'):
            cl = obj.contrato_locacao
            return f"{cl.logradouro}, {cl.numero} - {cl.bairro}, {cl.cidade}/{cl.estado}"
        return "N/A"
    
    def valor(self, obj):
        if hasattr(obj, 'contrato_locacao'):
            return f"R$ {obj.contrato_locacao.valor_aluguel}"
        return "N/A"
    
    def data_criacao_formatada(self, obj):
        return obj.data_criacao.strftime("%d/%m/%Y %H:%M")
    
    def acoes(self, obj):
        visualizar_url = f"/admin/contratos_app/contrato/{obj.id}/change/"
        pdf_url = f"/contrato/{obj.id}/pdf/"
        
        return format_html(
            '<a href="{}" class="button" style="margin-right:5px;">Editar</a>'
            '<a href="{}" class="button" target="_blank">PDF</a>',
            visualizar_url, pdf_url
        )
    
    tipo_contrato.short_description = 'Tipo'
    pessoa_envolvida.short_description = 'Pessoa Envolvida'
    imovel.short_description = 'Imóvel'
    valor.short_description = 'Valor'
    data_criacao_formatada.short_description = 'Data de Criação'
    acoes.short_description = 'Ações'

@admin.register(ContratoLocacao)
class ContratoLocacaoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome_locatario', 'nome_locador', 'endereco_completo', 'valor_aluguel', 'data_inicio_formatada', 'data_fim_formatada')
    list_filter = ('cidade', 'estado', 'data_inicio')
    search_fields = ('nome_locador', 'nome_locatario', 'logradouro', 'bairro', 'cidade')
    fieldsets = (
        ('Contrato', {
            'fields': ('contrato',)
        }),
        ('Dados do Locador', {
            'fields': (
                ('nome_locador', 'cpf_locador', 'rg_locador'),
                ('nacionalidade_locador', 'estado_civil_locador', 'profissao_locador'),
                'endereco_locador',
            )
        }),
        ('Dados do Locatário', {
            'fields': (
                ('nome_locatario', 'cpf_locatario', 'rg_locatario'),
                'nacionalidade_locatario',
            )
        }),
        ('Dados do Imóvel', {
            'fields': (
                ('logradouro', 'numero', 'complemento'),
                ('lote', 'quadra', 'casa'),
                ('bairro', 'cidade', 'estado', 'cep'),
            )
        }),
        ('Condições do Contrato', {
            'fields': (
                ('valor_aluguel', 'valor_aluguel_extenso'),
                ('data_inicio', 'dia_pagamento'),
            )
        }),
    )
    
    def endereco_completo(self, obj):
        return f"{obj.logradouro}, {obj.numero} - {obj.bairro}, {obj.cidade}/{obj.estado}"
    
    def data_inicio_formatada(self, obj):
        return obj.data_inicio.strftime("%d/%m/%Y")
    
    def data_fim_formatada(self, obj):
        return obj.data_fim().strftime("%d/%m/%Y")
    
    endereco_completo.short_description = 'Endereço'
    data_inicio_formatada.short_description = 'Início'
    data_fim_formatada.short_description = 'Término'