from datetime import date
from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import render, redirect, get_object_or_404

from .models import Category, CategoryBudget, Transaction


class CategoryBudgetForm(forms.ModelForm):
    class Meta:
        model = CategoryBudget
        fields = ['category', 'monthly_limit']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-select'}),
            'monthly_limit': forms.NumberInput(attrs={'class': 'form-control',
                                                      'placeholder': 'e.g. 3000'}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            self.fields['category'].queryset = Category.objects.filter(user=user)


@login_required
def category_budgets(request):
    if request.method == 'POST':
        form = CategoryBudgetForm(request.POST, user=request.user)
        if form.is_valid():
            # add a new budget, or update it if this category already has one
            CategoryBudget.objects.update_or_create(
                user=request.user,
                category=form.cleaned_data['category'],
                defaults={'monthly_limit': form.cleaned_data['monthly_limit']},
            )
            messages.success(request, 'Category budget saved.')
            return redirect('category_budgets')
    else:
        form = CategoryBudgetForm(user=request.user)

    today = date.today()
    rows = []
    budgets = CategoryBudget.objects.filter(user=request.user).select_related('category')
    for b in budgets:
        spent = Transaction.objects.filter(
            user=request.user, type='expense', category=b.category,
            date__year=today.year, date__month=today.month,
        ).aggregate(t=Sum('amount'))['t'] or 0
        percent = int(spent / b.monthly_limit * 100) if b.monthly_limit else 0
        rows.append({
            'id': b.pk,
            'name': b.category.name,
            'limit': b.monthly_limit,
            'spent': spent,
            'left': b.monthly_limit - spent,
            'over_by': spent - b.monthly_limit,
            'percent': percent,
            'bar': min(percent, 100),
            'over': spent > b.monthly_limit,
        })

    return render(request, 'tracker/category_budgets.html', {'form': form, 'rows': rows})


@login_required
def category_budget_delete(request, pk):
    obj = get_object_or_404(CategoryBudget, pk=pk, user=request.user)
    if request.method == 'POST':
        obj.delete()
        messages.success(request, 'Category budget removed.')
    return redirect('category_budgets')