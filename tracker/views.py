from django.shortcuts import render
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.db.models import Sum, Q
from django.db.models.functions import TruncMonth
from datetime import date
from .models import Transaction, Category, Budget
from .forms import TransactionForm, CategoryForm, BudgetForm
from .insights import get_insights


def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            for name in ['Food', 'Travel', 'Rent', 'Shopping', 'Salary', 'Other']:
                Category.objects.create(user=user, name=name)
            login(request, user)
            return redirect('dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'tracker/signup.html', {'form': form})


@login_required
def dashboard(request):
    qs = Transaction.objects.filter(user=request.user)

    total_income = qs.filter(type='income').aggregate(t=Sum('amount'))['t'] or 0
    total_expense = qs.filter(type='expense').aggregate(t=Sum('amount'))['t'] or 0

    by_cat = (qs.filter(type='expense')
                .values('category__name')
                .annotate(total=Sum('amount')))
    cat_labels = [c['category__name'] or 'Uncategorized' for c in by_cat]
    cat_data = [float(c['total']) for c in by_cat]

    monthly = (qs.filter(type='expense')
                 .annotate(m=TruncMonth('date'))
                 .values('m')
                 .annotate(total=Sum('amount'))
                 .order_by('m'))
    month_labels = [x['m'].strftime('%b %Y') for x in monthly]
    month_data = [float(x['total']) for x in monthly]

    # Budget alert (current month)
    today = date.today()
    month_expense = qs.filter(type='expense', date__year=today.year,
                              date__month=today.month).aggregate(t=Sum('amount'))['t'] or 0
    budget = Budget.objects.filter(user=request.user).first()
    budget_limit = budget.monthly_limit if budget else None
    budget_percent = 0
    if budget_limit:
        budget_percent = min(int(month_expense / budget_limit * 100), 100)

    context = {
        'total_income': total_income,
        'total_expense': total_expense,
        'balance': total_income - total_expense,
        'recent': qs[:5],
        'cat_labels': json.dumps(cat_labels),
        'cat_data': json.dumps(cat_data),
        'month_labels': json.dumps(month_labels),
        'month_data': json.dumps(month_data),
        'month_expense': month_expense,
        'budget_limit': budget_limit,
        'budget_percent': budget_percent,
        'over_budget': bool(budget_limit and month_expense > budget_limit),
        'insights': get_insights(qs),
    }
    return render(request, 'tracker/dashboard.html', context)

    context = {
        'total_income': total_income,
        'total_expense': total_expense,
        'balance': total_income - total_expense,
        'recent': qs[:5],
        'cat_labels': json.dumps(cat_labels),
        'cat_data': json.dumps(cat_data),
        'month_labels': json.dumps(month_labels),
        'month_data': json.dumps(month_data),
    }
    return render(request, 'tracker/dashboard.html', context)


@login_required
def transaction_list(request):
    qs = Transaction.objects.filter(user=request.user)

    t_type = request.GET.get('type', '')
    category = request.GET.get('category', '')
    start = request.GET.get('start', '')
    end = request.GET.get('end', '')
    q = request.GET.get('q', '')

    if t_type:
        qs = qs.filter(type=t_type)
    if category:
        qs = qs.filter(category_id=category)
    if start:
        qs = qs.filter(date__gte=start)
    if end:
        qs = qs.filter(date__lte=end)
    if q:
        qs = qs.filter(Q(note__icontains=q) | Q(category__name__icontains=q))

    context = {
        'transactions': qs,
        'categories': Category.objects.filter(user=request.user),
        'filters': request.GET,
    }
    return render(request, 'tracker/transaction_list.html', context)


@login_required
def transaction_add(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST, user=request.user)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.user = request.user
            obj.save()
            messages.success(request, 'Transaction added.')
            return redirect('transaction_list')
    else:
        form = TransactionForm(user=request.user)
    return render(request, 'tracker/transaction_form.html', {'form': form, 'title': 'Add Transaction'})


@login_required
def transaction_edit(request, pk):
    obj = get_object_or_404(Transaction, pk=pk, user=request.user)
    if request.method == 'POST':
        form = TransactionForm(request.POST, instance=obj, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Transaction updated.')
            return redirect('transaction_list')
    else:
        form = TransactionForm(instance=obj, user=request.user)
    return render(request, 'tracker/transaction_form.html', {'form': form, 'title': 'Edit Transaction'})


@login_required
def transaction_delete(request, pk):
    obj = get_object_or_404(Transaction, pk=pk, user=request.user)
    if request.method == 'POST':
        obj.delete()
        messages.success(request, 'Transaction deleted.')
        return redirect('transaction_list')
    return render(request, 'tracker/confirm_delete.html', {'obj': obj})


@login_required
def category_list(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            cat = form.save(commit=False)
            cat.user = request.user
            cat.save()
            return redirect('category_list')
    else:
        form = CategoryForm()
    categories = Category.objects.filter(user=request.user)
    return render(request, 'tracker/categories.html', {'form': form, 'categories': categories})


@login_required
def category_delete(request, pk):
    cat = get_object_or_404(Category, pk=pk, user=request.user)
    if request.method == 'POST':
        cat.delete()
    return redirect('category_list')

@login_required
def set_budget(request):
    budget = Budget.objects.filter(user=request.user).first()
    if request.method == 'POST':
        form = BudgetForm(request.POST, instance=budget)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.user = request.user
            obj.save()
            messages.success(request, 'Budget saved.')
            return redirect('dashboard')
    else:
        form = BudgetForm(instance=budget)
    return render(request, 'tracker/budget_form.html', {'form': form})