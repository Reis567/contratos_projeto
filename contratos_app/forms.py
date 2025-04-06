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