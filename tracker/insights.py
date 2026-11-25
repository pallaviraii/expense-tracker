from datetime import date
from django.db.models import Sum


def get_insights(qs):
    today = date.today()
    if today.month == 1:
        last_year, last_month = today.year - 1, 12
    else:
        last_year, last_month = today.year, today.month - 1

    this_exp = qs.filter(type='expense', date__year=today.year, date__month=today.month)
    last_exp = qs.filter(type='expense', date__year=last_year, date__month=last_month)

    this_total = this_exp.aggregate(t=Sum('amount'))['t'] or 0
    last_total = last_exp.aggregate(t=Sum('amount'))['t'] or 0

    if this_total == 0 and last_total == 0:
        return [{'icon': '💡', 'level': 'info',
                 'text': 'Add some expenses to see personalised insights.'}]

    insights = []

    # 1. This month vs last month
    if last_total > 0:
        change = (this_total - last_total) / last_total * 100
        if change > 0:
            insights.append({'icon': '📈', 'level': 'warning',
                             'text': f'You have spent {change:.0f}% more than last month (₹{this_total:.0f} vs ₹{last_total:.0f}).'})
        elif change < 0:
            insights.append({'icon': '📉', 'level': 'success',
                             'text': f'Great! You have spent {abs(change):.0f}% less than last month.'})
        else:
            insights.append({'icon': '⚖️', 'level': 'info',
                             'text': 'Your spending is exactly the same as last month.'})
    else:
        insights.append({'icon': 'ℹ️', 'level': 'info',
                         'text': 'No expenses recorded last month, so there is nothing to compare yet.'})

    # 2. Top spending category this month
    cat_rows = this_exp.values('category__name').annotate(total=Sum('amount'))
    this_cat = {r['category__name'] or 'Uncategorized': r['total'] for r in cat_rows}
    if this_cat and this_total > 0:
        top_name = max(this_cat, key=this_cat.get)
        share = this_cat[top_name] / this_total * 100
        insights.append({'icon': '🏆', 'level': 'info',
                         'text': f'Your top spending category is {top_name} ({share:.0f}% of this month\'s expenses).'})

    # 3. Category with the biggest increase
    last_rows = last_exp.values('category__name').annotate(total=Sum('amount'))
    last_cat = {r['category__name'] or 'Uncategorized': r['total'] for r in last_rows}
    best_name, best_pct = None, 0
    for name, amount in this_cat.items():
        prev = last_cat.get(name, 0)
        if prev > 0:
            pct = (amount - prev) / prev * 100
            if pct > best_pct:
                best_name, best_pct = name, pct
    if best_name and best_pct >= 10:
        insights.append({'icon': '⚠️', 'level': 'danger',
                         'text': f'Your {best_name} spending is up {best_pct:.0f}% compared to last month.'})

    # 4. Savings rate this month
    income = qs.filter(type='income', date__year=today.year,
                       date__month=today.month).aggregate(t=Sum('amount'))['t'] or 0
    if income > 0:
        rate = (income - this_total) / income * 100
        if rate >= 20:
            insights.append({'icon': '💰', 'level': 'success',
                             'text': f'You are saving {rate:.0f}% of your income this month. Keep it up!'})
        elif rate >= 0:
            insights.append({'icon': '💰', 'level': 'warning',
                             'text': f'You are saving only {rate:.0f}% of your income. Try to reach 20%.'})
        else:
            insights.append({'icon': '🚨', 'level': 'danger',
                             'text': 'You have spent more than you earned this month.'})

    # 5. Daily average
    avg = this_total / today.day
    insights.append({'icon': '📅', 'level': 'info',
                     'text': f'You spend about ₹{avg:.0f} per day this month.'})

    return insights