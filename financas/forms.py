from django import forms
from .models import Transacao, Pagamento, Categoria, Subcategoria, Cartao, TransacaoCartao, Banco, Conta

class TransacaoForm(forms.ModelForm):
    categoria = forms.ModelChoiceField(
        queryset=Categoria.objects.all(), 
        required=True, 
        label="Categoria"
    )
    conta = forms.ModelChoiceField(
        queryset=Conta.objects.all(), 
        required=False, 
        label="Conta"
    )
    cartao = forms.ModelChoiceField(
        queryset=Cartao.objects.all(), 
        required=False, 
        label="Cartão"
    )

    class Meta:
        model = Transacao
        fields = ['titulo', 'valor', 'tipo', 'categoria', 'conta', 'cartao', 'data']
      

class PagamentoForm(forms.ModelForm):
    class Meta:
        model = Pagamento
        fields = ['titulo', 'valor', 'data_vencimento', 'frequencia']
        widgets = {
            'data_vencimento': forms.DateInput(attrs={'type': 'date'}),
            'valor': forms.NumberInput(attrs={'step': '0.01'}),
        }

class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nome', 'cor', 'icone']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'campo-formulario', 'placeholder': 'Ex: cofrinho'}),
            'cor': forms.HiddenInput(),
            'icone': forms.HiddenInput(),
        }

class SubcategoriaForm(forms.ModelForm):
    class Meta:
        model = Subcategoria
        fields = ['nome', 'cor', 'icone', 'categoria_pai']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'campo-formulario', 'placeholder': 'Ex: despesas extras'}),
            'cor': forms.HiddenInput(),
            'icone': forms.HiddenInput(),
            'categoria_pai': forms.Select(attrs={'class': 'campo-formulario'}),
        }

class CartaoForm(forms.ModelForm):
    class Meta:
        model = Cartao
        fields = ['banco', 'nome_cartao', 'limite_total', 'data_fechamento', 'data_vencimento']
        widgets = {
            'banco': forms.Select(attrs={'class': 'form-control'}),
            'nome_cartao': forms.TextInput(attrs={'class': 'form-control'}),
            'limite_total': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'data_fechamento': forms.Select(choices=[(i, i) for i in range(1, 32)], attrs={'class': 'form-control'}),
            'data_vencimento': forms.Select(choices=[(i, i) for i in range(1, 32)], attrs={'class': 'form-control'}),
        }


class TransacaoCartaoForm(forms.ModelForm):
    class Meta:
        model = TransacaoCartao
        fields = ['valor', 'descricao', 'data']
        widgets = {
            'valor': forms.DateInput(attrs={'step': '0.01'}),
        }

class BancoForm(forms.ModelForm):
    class Meta:
        model = Banco
        fields = ['nome']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'})
        }

class ContaForm(forms.ModelForm):
    class Meta:
        model = Conta
        fields = ['banco', 'titulo', 'saldo']
        widgets = {
            'banco': forms.Select(attrs={'class': 'form-control'}),
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'saldo': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }