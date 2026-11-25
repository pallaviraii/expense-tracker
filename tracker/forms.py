from django import forms
from .models import Transaction, Category, Budget


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['type', 'category', 'amount', 'date', 'note']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            self.fields['category'].queryset = Category.objects.filter(user=user)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'New category'}),
        }
class BudgetForm(forms.ModelForm):
    class Meta:
        model = Budget
        fields = ['monthly_limit']
        widgets = {
            'monthly_limit': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 15000'}),
        }