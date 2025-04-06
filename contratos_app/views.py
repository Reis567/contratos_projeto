# contratos/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.template.loader import get_template
from django.utils import timezone
from .models import Contrato, ContratoLocacao, TipoContrato
from .forms import ContratoForm, ContratoLocacaoForm
from num2words import num2words
from xhtml2pdf import pisa
from io import BytesIO

def home(request):
    """Página inicial com lista de contratos"""
    contratos = Contrato.objects.all().order_by('-data_criacao')
    return render(request, 'home.html', {'contratos': contratos})

# Modificação em contratos/views.py

def selecionar_tipo_contrato(request):
    """View para selecionar o tipo de contrato a ser criado"""
    if request.method == 'POST':
        form = ContratoForm(request.POST)
        if form.is_valid():
            # Em vez de salvar o contrato, guardamos o tipo escolhido na sessão
            tipo_id = form.cleaned_data['tipo'].id
            request.session['tipo_contrato_id'] = tipo_id
            
            # Redirecionar para o formulário específico com base no tipo de contrato
            if tipo_id == 1:  # Assumindo que o ID 1 é para Contrato de Locação
                return redirect('criar_contrato_locacao')
            # Adicione mais redirecionamentos conforme novos tipos forem adicionados
            
    else:
        form = ContratoForm()
    
    return render(request, 'contratos/selecionar_tipo.html', {'form': form})

def criar_contrato_locacao(request):
    """View para criar um contrato de locação"""
    # Verificar se o tipo foi selecionado
    tipo_id = request.session.get('tipo_contrato_id')
    if not tipo_id:
        return redirect('selecionar_tipo_contrato')
    
    if request.method == 'POST':
        form = ContratoLocacaoForm(request.POST)
        if form.is_valid():
            # Primeiro criamos o contrato base
            tipo_contrato = get_object_or_404(TipoContrato, id=tipo_id)
            contrato = Contrato.objects.create(tipo=tipo_contrato)
            
            # Depois associamos os detalhes de locação
            contrato_locacao = form.save(commit=False)
            contrato_locacao.contrato = contrato
            
            # Processar valor por extenso
            valor = contrato_locacao.valor_aluguel
            contrato_locacao.valor_aluguel_extenso = num2words(float(valor), lang='pt_BR')
            
            contrato_locacao.save()
            
            # Limpar a sessão
            if 'tipo_contrato_id' in request.session:
                del request.session['tipo_contrato_id']
                
            return redirect('visualizar_contrato', contrato_id=contrato.id)
    else:
        form = ContratoLocacaoForm()
    
    return render(request, 'contratos/criar_contrato_locacao.html', {'form': form})
def visualizar_contrato(request, contrato_id):
    """View para visualizar um contrato"""
    contrato = get_object_or_404(Contrato, id=contrato_id)
    
    # Determinar qual tipo de contrato estamos lidando
    template_name = 'contratos/visualizar_contrato_base.html'
    contexto_extra = {}
    
    if hasattr(contrato, 'contrato_locacao'):
        template_name = 'contratos/visualizar_contrato_locacao.html'
        contexto_extra = {'contrato_locacao': contrato.contrato_locacao}
    
    # Adicione mais condições para outros tipos de contratos
    
    return render(request, template_name, {'contrato': contrato, **contexto_extra})

def render_to_pdf(template_src, context_dict={}):
    """Função auxiliar para gerar PDF a partir de um template"""
    template = get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None

def gerar_pdf(request, contrato_id):
    """View para gerar PDF do contrato"""
    contrato = get_object_or_404(Contrato, id=contrato_id)
    
    # Determinar qual template e contexto usar com base no tipo de contrato
    template_pdf = None
    contexto = {'contrato': contrato, 'data_atual': timezone.now().date()}
    
    if hasattr(contrato, 'contrato_locacao'):
        template_pdf = 'contratos/pdf/contrato_locacao.html'
        contexto['contrato_locacao'] = contrato.contrato_locacao
        contexto['data_fim'] = contrato.contrato_locacao.data_fim()
    
    # Adicione mais condições para outros tipos de contratos
    
    if not template_pdf:
        return HttpResponse("Tipo de contrato não suportado para geração de PDF", status=400)
    
    # Gerar PDF
    pdf = render_to_pdf(template_pdf, contexto)
    
    if pdf:
        # Configurar cabeçalho para download do arquivo
        response = HttpResponse(pdf, content_type='application/pdf')
        filename = f"contrato_{contrato.id}.pdf"
        if hasattr(contrato, 'contrato_locacao'):
            filename = f"contrato_locacao_{contrato.contrato_locacao.nome_locatario.replace(' ', '_')}.pdf"
        
        content = f"attachment; filename={filename}"
        response['Content-Disposition'] = content
        return response
    
    return HttpResponse("Erro ao gerar PDF", status=400)

def editar_contrato(request, contrato_id):
    """View para editar um contrato existente"""
    contrato = get_object_or_404(Contrato, id=contrato_id)
    
    # Determinar qual tipo de contrato estamos editando
    if hasattr(contrato, 'contrato_locacao'):
        return editar_contrato_locacao(request, contrato)
    
    # Adicione mais condições para outros tipos de contratos
    
    return HttpResponse("Tipo de contrato não suportado para edição", status=400)

def editar_contrato_locacao(request, contrato):
    """Função auxiliar para editar contrato de locação"""
    contrato_locacao = contrato.contrato_locacao
    
    if request.method == 'POST':
        form = ContratoLocacaoForm(request.POST, instance=contrato_locacao)
        if form.is_valid():
            contrato_atualizado = form.save(commit=False)
            valor = contrato_atualizado.valor_aluguel
            contrato_atualizado.valor_aluguel_extenso = num2words(float(valor), lang='pt_BR')
            contrato_atualizado.save()
            return redirect('visualizar_contrato', contrato_id=contrato.id)
    else:
        form = ContratoLocacaoForm(instance=contrato_locacao)
    
    return render(request, 'contratos/editar_contrato_locacao.html', {'form': form, 'contrato': contrato})