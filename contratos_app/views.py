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
    tipo_id = request.session.get('tipo_contrato_id')
    if not tipo_id:
        return redirect('selecionar_tipo_contrato')
    
    tipo_contrato = get_object_or_404(TipoContrato, id=tipo_id)
    
    if request.method == 'POST':
        form = ContratoLocacaoForm(request.POST)
        if form.is_valid():
            try:
                # Criamos o contrato base
                contrato = Contrato.objects.create(tipo=tipo_contrato)
                
                # Associamos os detalhes de locação
                contrato_locacao = form.save(commit=False)
                contrato_locacao.contrato = contrato
                
                # Processar valor por extenso (melhorado)
                valor = contrato_locacao.valor_aluguel
                valor_inteiro = int(valor)
                centavos = int((valor - valor_inteiro) * 100)
                
                valor_extenso = num2words(valor_inteiro, lang='pt_BR')
                
                if centavos > 0:
                    centavos_extenso = num2words(centavos, lang='pt_BR')
                    contrato_locacao.valor_aluguel_extenso = f"{valor_extenso} reais e {centavos_extenso} centavos"
                else:
                    contrato_locacao.valor_aluguel_extenso = f"{valor_extenso} reais"
                
                contrato_locacao.save()
                
                # Limpar a sessão
                if 'tipo_contrato_id' in request.session:
                    del request.session['tipo_contrato_id']
                
                return redirect('visualizar_contrato', contrato_id=contrato.id)
                
            except Exception as e:
                if 'contrato' in locals():
                    contrato.delete()
    else:
        form = ContratoLocacaoForm()
    
    return render(request, 'contratos/criar_contrato_locacao.html', {
        'form': form,
        'tipo_contrato': tipo_contrato
    })

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
    """Função auxiliar para gerar PDF a partir de um template com tratamento de erros melhorado"""
    template = get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO()
    
    # Configuração do pisa com opções mais básicas e compatíveis
    pdf = pisa.pisaDocument(
        BytesIO(html.encode("UTF-8")), 
        result,
        encoding='UTF-8'
    )
    
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    
    # Em caso de erro, imprime detalhes para debug
    print(f"Erro ao gerar PDF: {pdf.err}")
    return None

def fetch_resources(uri, rel):
    """
    Função auxiliar para buscar recursos estáticos como imagens e CSS
    """
    from django.conf import settings
    import os
    
    # Busca o recurso no sistema de arquivos
    path = os.path.join(settings.STATIC_ROOT, uri.replace(settings.STATIC_URL, ""))
    return path

def gerar_pdf(request, contrato_id):
    """View melhorada para gerar PDF do contrato"""
    contrato = get_object_or_404(Contrato, id=contrato_id)
    
    # Determinar qual template e contexto usar com base no tipo de contrato
    template_pdf = None
    contexto = {
        'contrato': contrato, 
        'data_atual': timezone.now().date(),
        'page_size': 'A4',
    }
    
    if hasattr(contrato, 'contrato_locacao'):
        template_pdf = 'contratos/pdf/contrato_locacao.html'
        contrato_locacao = contrato.contrato_locacao
        
        # Calcular a data de fim do contrato
        data_fim = contrato_locacao.data_fim()
        
        # Processar texto por extenso com melhor formatação
        valor = contrato_locacao.valor_aluguel
        valor_inteiro = int(valor)
        centavos = int((valor - valor_inteiro) * 100)
        
        valor_extenso = num2words(valor_inteiro, lang='pt_BR')
        valor_extenso = valor_extenso.replace('e zero', '')  # Formata melhor o texto por extenso
        
        if centavos > 0:
            centavos_extenso = num2words(centavos, lang='pt_BR')
            valor_aluguel_extenso = f"{valor_extenso} reais e {centavos_extenso} centavos"
        else:
            valor_aluguel_extenso = f"{valor_extenso} reais"
        
        # Formatar o primeiro caractere em maiúsculo
        valor_aluguel_extenso = valor_aluguel_extenso[0].upper() + valor_aluguel_extenso[1:]
        
        # Atualizar contexto com os dados específicos do contrato de locação
        contexto.update({
            'contrato_locacao': contrato_locacao,
            'data_fim': data_fim,
            'valor_aluguel_extenso': valor_aluguel_extenso
        })
    
    # Adicione mais condições para outros tipos de contratos
    
    if not template_pdf:
        return HttpResponse("Tipo de contrato não suportado para geração de PDF", status=400)
    
    # Gerar PDF
    pdf = render_to_pdf(template_pdf, contexto)
    
    if pdf:
        # Configurar cabeçalho para download do arquivo
        response = HttpResponse(pdf, content_type='application/pdf')
        
        # Melhorar a nomenclatura do arquivo para evitar problemas com caracteres especiais
        filename = f"contrato_{contrato.id}.pdf"
        if hasattr(contrato, 'contrato_locacao'):
            # Sanitizar o nome do locatário para evitar problemas no nome do arquivo
            nome_sanitizado = ''.join(c for c in contrato.contrato_locacao.nome_locatario 
                                    if c.isalnum() or c in [' ', '_']).strip()
            nome_sanitizado = nome_sanitizado.replace(' ', '_')
            filename = f"contrato_locacao_{nome_sanitizado}.pdf"
        
        # Definir se o arquivo será visualizado no navegador ou baixado
        if request.GET.get('download', False):
            content = f"attachment; filename={filename}"
        else:
            content = f"inline; filename={filename}"
            
        response['Content-Disposition'] = content
        return response
    
    return HttpResponse("Erro ao gerar PDF. Por favor, tente novamente.", status=400)

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