# contratos/forms.py
from django import forms
from .models import Contrato, ContratoLocacao, TipoContrato

class ContratoForm(forms.ModelForm):
    class Meta:
        model = Contrato
        fields = ['tipo']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['tipo'].widget = forms.RadioSelect()
        self.fields['tipo'].queryset = TipoContrato.objects.all()
        self.fields['tipo'].empty_label = None

class ContratoLocacaoForm(forms.ModelForm):
    class Meta:
        model = ContratoLocacao
        exclude = ['contrato']
        widgets = {
            'data_inicio': forms.DateInput(attrs={'type': 'date'}),
            'valor_aluguel': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
            'dia_pagamento': forms.NumberInput(attrs={'min': '1', 'max': '31'}),
        }



class ContratoLocacaoForm(forms.ModelForm):
    class Meta:
        model = ContratoLocacao
        exclude = ['contrato', 'valor_aluguel_extenso']
        widgets = {
            'data_inicio': forms.DateInput(attrs={'type': 'date'}),
            'valor_aluguel': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
            'dia_pagamento': forms.NumberInput(attrs={'min': '1', 'max': '31'}),
        }
    
    def clean_cpf_locador(self):
        cpf = self.cleaned_data.get('cpf_locador')
        # Implementar validação de CPF
        if not self.validar_cpf(cpf):
            raise forms.ValidationError("CPF inválido.")
        return cpf
    
    def clean_cpf_locatario(self):
        cpf = self.cleaned_data.get('cpf_locatario')
        # Implementar validação de CPF
        if not self.validar_cpf(cpf):
            raise forms.ValidationError("CPF inválido.")
        return cpf
    
    def validar_cpf(self, cpf):
        # Remover pontuações
        cpf = ''.join(filter(str.isdigit, cpf))
        
        # Verificar se tem 11 dígitos
        if len(cpf) != 11:
            return False
        
        # Verificar se todos os dígitos são iguais
        if cpf == cpf[0] * 11:
            return False
        
        # Implementar algoritmo de validação de CPF aqui
        # Este é um exemplo simplificado
        return True
    
    def clean_dia_pagamento(self):
        dia = self.cleaned_data.get('dia_pagamento')
        if dia < 1 or dia > 31:
            raise forms.ValidationError("O dia de pagamento deve estar entre 1 e 31.")
        return dia