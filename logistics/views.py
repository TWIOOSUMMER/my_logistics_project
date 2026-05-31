import csv
import io
import json
from datetime import datetime, timedelta, time as dt_time
from decimal import Decimal, InvalidOperation
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Count, F, Q, Sum
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from .forms import GoodsForm, OrderForm, GoodsCategoryForm
from .models import GoodsTb, GoodsCategory, OrderTb, OrderItem, OperationLog

PAGE_SIZE = 5
PAGE_SIZES = [5, 10, 20]


def _log(action, model_name, object_name, description=''):
    OperationLog.objects.create(
        action=action,
        model_name=model_name,
        object_name=object_name,
        description=description,
    )


def _total_value(qs):
    result = qs.aggregate(t=Sum(F('price') * F('stock')))
    return result['t'] or 0


def _dashboard():
    return {
        'total_goods': GoodsTb.objects.count(),
        'total_orders': OrderTb.objects.count(),
        'pending_orders': OrderTb.objects.filter(status='pending').count(),
        'total_value': _total_value(GoodsTb.objects.all()),
        'shipping_orders': OrderTb.objects.filter(status='shipping').count(),
        'delivered_orders': OrderTb.objects.filter(status='delivered').count(),
        'cancelled_orders': OrderTb.objects.filter(status='cancelled').count(),
        'low_stock_count': GoodsTb.objects.filter(stock__lte=5).count(),
        'top_customers': (
            OrderTb.objects.values('customer_name')
            .annotate(cnt=Count('id'))
            .order_by('-cnt')[:5]
        ),
        'category_distribution': list(
            GoodsTb.objects.values('category__name')
            .annotate(cnt=Count('id'))
            .order_by('-cnt')
        ),
        'recent_logs': OperationLog.objects.order_by('-created_at')[:8],
        'recent_week_orders': _recent_week_data(),
        'total_revenue': OrderTb.objects.aggregate(s=Sum('total_amount'))['s'] or 0,
    }


def _recent_week_data():
    today = timezone.localdate()
    data = []
    for i in range(6, -1, -1):
        d = today - timedelta(days=i)
        day_start = timezone.make_aware(datetime.combine(d, dt_time.min))
        day_end = timezone.make_aware(datetime.combine(d, dt_time.max))
        cnt = OrderTb.objects.filter(
            created_at__gte=day_start, created_at__lte=day_end
        ).count()
        data.append({'date': d.strftime('%m-%d'), 'count': cnt})
    return data


def _get_page_size(request):
    ps = request.GET.get('page_size', str(PAGE_SIZE))
    try:
        ps = int(ps)
    except (ValueError, TypeError):
        ps = PAGE_SIZE
    if ps not in PAGE_SIZES:
        ps = PAGE_SIZE
    return ps


def _get_sort(request, param_name, default, field_map):
    sort = request.GET.get(param_name, default)
    reverse = sort.startswith('-')
    key = sort[1:] if reverse else sort
    if key not in field_map:
        sort = default
    return sort


def index(request):
    page_size = _get_page_size(request)
    goods_page = request.GET.get('goods_page', 1)
    order_page = request.GET.get('order_page', 1)
    goods_sort = request.GET.get('goods_sort', 'id')
    order_sort = request.GET.get('order_sort', 'id')

    goods_field_map = {'id': 'id', 'goods_name': 'goods_name', 'category': 'category__name',
                       'weight': 'weight', 'price': 'price', 'stock': 'stock'}
    order_field_map = {'id': 'id', 'order_number': 'order_number',
                       'customer_name': 'customer_name', 'created_at': 'created_at',
                       'total_amount': 'total_amount'}

    goods_sort = _get_sort(request, 'goods_sort', 'id', goods_field_map)
    order_sort = _get_sort(request, 'order_sort', 'id', order_field_map)

    goods_qs = GoodsTb.objects.select_related('category').all()
    category_filter = request.GET.get('category', '')
    goods_query = request.GET.get('goods_q', '')
    low_stock = request.GET.get('low_stock', '')

    if category_filter:
        goods_qs = goods_qs.filter(category__name=category_filter)
    if goods_query:
        goods_qs = goods_qs.filter(goods_name__icontains=goods_query)
    if low_stock:
        goods_qs = goods_qs.filter(stock__lte=5)

    order_qs = OrderTb.objects.prefetch_related('items__goods').all()
    status_filter = request.GET.get('status', '')
    order_query = request.GET.get('order_q', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')

    if status_filter:
        order_qs = order_qs.filter(status=status_filter)
    if order_query:
        order_qs = order_qs.filter(Q(order_number__icontains=order_query) | Q(customer_name__icontains=order_query))
    if date_from:
        try:
            d_from = datetime.strptime(date_from, '%Y-%m-%d').date()
            dt_from = timezone.make_aware(datetime.combine(d_from, dt_time.min))
            order_qs = order_qs.filter(created_at__gte=dt_from)
        except ValueError:
            pass
    if date_to:
        try:
            d_to = datetime.strptime(date_to, '%Y-%m-%d').date()
            dt_to = timezone.make_aware(datetime.combine(d_to, dt_time.max))
            order_qs = order_qs.filter(created_at__lte=dt_to)
        except ValueError:
            pass

    goods_qs = goods_qs.order_by(goods_sort)
    order_qs = order_qs.order_by(order_sort)

    categories = GoodsCategory.objects.values_list('name', flat=True).order_by('name')

    context = {
        'goods_list': Paginator(goods_qs, page_size).get_page(goods_page),
        'order_list': Paginator(order_qs, page_size).get_page(order_page),
        'page_size': page_size,
        'page_sizes': PAGE_SIZES,
        'page_size_links': [{'size': sz, 'active': (sz == page_size)} for sz in PAGE_SIZES],
        'goods_sort': goods_sort,
        'order_sort': order_sort,
        'category_filter': category_filter,
        'status_filter': status_filter,
        'date_from': date_from,
        'date_to': date_to,
        'goods_query': goods_query,
        'order_query': order_query,
        'low_stock': low_stock,
        'categories': categories,
        'status_choices': OrderTb.ORDER_STATUS,
        **_dashboard(),
    }
    return render(request, 'logistics/index.html', context)


def category_add(request):
    if request.method == 'POST':
        form = GoodsCategoryForm(request.POST)
        if form.is_valid():
            obj = form.save()
            return JsonResponse({'success': True, 'id': obj.id, 'name': obj.name})
        else:
            return JsonResponse({'success': False, 'error': form.errors.as_json()})
    return JsonResponse({'success': False, 'error': '仅支持POST请求'})


def goods_add(request):
    if request.method == 'POST':
        form = GoodsForm(request.POST)
        if form.is_valid():
            obj = form.save()
            _log('create', '货物', obj.goods_name)
            messages.success(request, '货物添加成功')
            return redirect('index')
    else:
        form = GoodsForm()
    return render(request, 'logistics/goods_form.html', {'form': form, 'title': '添加货物', **_dashboard()})


def goods_edit(request, goods_id):
    goods = get_object_or_404(GoodsTb, id=goods_id)
    if request.method == 'POST':
        form = GoodsForm(request.POST, instance=goods)
        if form.is_valid():
            obj = form.save()
            _log('update', '货物', obj.goods_name, '修改了货物信息')
            messages.success(request, '货物修改成功')
            return redirect('index')
    else:
        form = GoodsForm(instance=goods)
    return render(request, 'logistics/goods_form.html', {
        'form': form, 'title': '编辑货物', **_dashboard(),
    })


def goods_delete(request, goods_id):
    goods = get_object_or_404(GoodsTb, id=goods_id)
    related_orders = OrderItem.objects.filter(goods=goods).values('order').distinct().count()
    if request.method == 'POST':
        name = goods.goods_name
        goods.delete()
        _log('delete', '货物', name, f'删除货物及{related_orders}条关联订单明细')
        messages.success(request, '货物删除成功')
        return redirect('index')
    return render(request, 'logistics/confirm_delete.html', {
        'name': goods.goods_name,
        'cancel_url': 'index',
        'related_count': related_orders,
        **_dashboard(),
    })


def goods_export(request):
    response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
    response['Content-Disposition'] = 'attachment; filename="goods_export.csv"'
    writer = csv.writer(response)
    writer.writerow(['ID', '货物名称', '类别', '重量(kg)', '单价(元)', '库存数量'])
    for g in GoodsTb.objects.select_related('category').all().order_by('id'):
        writer.writerow([g.id, g.goods_name, g.category.name, g.weight, g.price, g.stock])
    return response


def goods_import(request):
    if request.method == 'POST':
        csv_file = request.FILES.get('csv_file')
        if csv_file:
            try:
                decoded = csv_file.read().decode('utf-8-sig')
                reader = csv.reader(io.StringIO(decoded))
                header = next(reader, None)
                count = 0
                errors = []
                for row in reader:
                    if len(row) >= 6:
                        name, cat_name, weight, price, stock = row[0], row[1], row[2], row[3], row[4]
                        cat_name = cat_name.strip() if cat_name.strip() else '未分类'
                        category, _ = GoodsCategory.objects.get_or_create(name=cat_name)
                        try:
                            GoodsTb.objects.create(
                                goods_name=name.strip(),
                                category=category,
                                weight=float(weight) if weight else 0,
                                price=float(price) if price else 0,
                                stock=int(float(stock)) if stock else 0,
                            )
                            count += 1
                        except Exception as e:
                            errors.append(f'{name.strip()}: {e}')
                if errors:
                    messages.warning(request, f'成功导入 {count} 条，{len(errors)} 条失败')
                else:
                    messages.success(request, f'成功导入 {count} 条货物')
                return redirect('index')
            except Exception as e:
                messages.error(request, f'导入失败: {e}')
        else:
            messages.error(request, '请选择 CSV 文件')
    return render(request, 'logistics/goods_import.html', {'title': '批量导入货物', **_dashboard()})


def _goods_json():
    goods_qs = GoodsTb.objects.select_related('category').all().order_by('goods_name')
    return json.dumps([{
        'id': g.id,
        'goods_name': g.goods_name,
        'category_id': g.category_id,
        'category_name': g.category.name,
        'price': str(g.price),
    } for g in goods_qs])


def _categories_json():
    cats = GoodsCategory.objects.all().order_by('name')
    return json.dumps([{'id': c.id, 'name': c.name} for c in cats])


def order_add(request):
    goods_all = GoodsTb.objects.select_related('category').all().order_by('goods_name')
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            goods_ids = request.POST.getlist('goods_ids')
            quantities = request.POST.getlist('quantities')
            unit_prices = request.POST.getlist('unit_prices')
            if not goods_ids or not any(g.strip() for g in goods_ids):
                form.add_error(None, '请至少选择一种货物')
            else:
                order = form.save(commit=False)
                order.total_amount = 0
                order.save()
                total = Decimal('0')
                for i in range(len(goods_ids)):
                    gid = goods_ids[i].strip()
                    if not gid:
                        continue
                    qty = int(quantities[i]) if i < len(quantities) else 1
                    try:
                        uprice = Decimal(unit_prices[i]) if i < len(unit_prices) else Decimal('0')
                    except InvalidOperation:
                        uprice = Decimal('0')
                    goods = get_object_or_404(GoodsTb, id=int(gid))
                    if uprice == 0:
                        uprice = goods.price
                    OrderItem.objects.create(
                        order=order, goods=goods,
                        quantity=qty, unit_price=uprice,
                    )
                    total += qty * uprice
                order.total_amount = total
                order.save(update_fields=['total_amount'])
                _log('create', '订单', order.order_number)
                messages.success(request, '订单添加成功')
                return redirect('index')
    else:
        form = OrderForm()
    return render(request, 'logistics/order_form.html', {
        'form': form, 'title': '添加订单',
        'goods_all': goods_all,
        'goods_json': _goods_json(),
        'categories_json': _categories_json(),
        **_dashboard(),
    })


def order_edit(request, order_id):
    order = get_object_or_404(OrderTb.objects.prefetch_related('items__goods'), id=order_id)
    goods_all = GoodsTb.objects.select_related('category').all().order_by('goods_name')
    if request.method == 'POST':
        form = OrderForm(request.POST, instance=order)
        if form.is_valid():
            goods_ids = request.POST.getlist('goods_ids')
            quantities = request.POST.getlist('quantities')
            unit_prices = request.POST.getlist('unit_prices')
            if not goods_ids or not any(g.strip() for g in goods_ids):
                form.add_error(None, '请至少选择一种货物')
            else:
                obj = form.save(commit=False)
                obj.items.all().delete()
                total = Decimal('0')
                for i in range(len(goods_ids)):
                    gid = goods_ids[i].strip()
                    if not gid:
                        continue
                    qty = int(quantities[i]) if i < len(quantities) else 1
                    try:
                        uprice = Decimal(unit_prices[i]) if i < len(unit_prices) else Decimal('0')
                    except InvalidOperation:
                        uprice = Decimal('0')
                    goods = get_object_or_404(GoodsTb, id=int(gid))
                    if uprice == 0:
                        uprice = goods.price
                    OrderItem.objects.create(
                        order=obj, goods=goods,
                        quantity=qty, unit_price=uprice,
                    )
                    total += qty * uprice
                obj.total_amount = total
                obj.save(update_fields=['total_amount'])
                _log('update', '订单', obj.order_number)
                messages.success(request, '订单修改成功')
                return redirect('index')
    else:
        form = OrderForm(instance=order)
    return render(request, 'logistics/order_form.html', {
        'form': form, 'title': '编辑订单',
        'order': order, 'goods_all': goods_all,
        'goods_json': _goods_json(),
        'categories_json': _categories_json(),
        **_dashboard(),
    })


def order_delete(request, order_id):
    order = get_object_or_404(OrderTb, id=order_id)
    if request.method == 'POST':
        name = order.order_number
        order.delete()
        _log('delete', '订单', name)
        messages.success(request, '订单删除成功')
        return redirect('index')
    return render(request, 'logistics/confirm_delete.html', {
        'name': order.order_number,
        'cancel_url': 'index',
        'related_count': 0,
        **_dashboard(),
    })


def order_status_change(request, order_id):
    order = get_object_or_404(OrderTb, id=order_id)
    if request.method == 'POST':
        new_status = request.POST.get('status', order.status)
        order.status = new_status
        order.save()
        _log('update', '订单', order.order_number,
             f'状态变为 {order.get_status_display()}')
        messages.success(request, '状态已更新')
    referer = request.META.get('HTTP_REFERER', '')
    if referer and '/logistics/order/detail/' not in referer:
        return redirect(referer)
    return redirect('index')


def order_batch_status(request):
    if request.method == 'POST':
        ids = request.POST.getlist('order_ids')
        new_status = request.POST.get('status', '')
        if ids and new_status:
            count = OrderTb.objects.filter(id__in=ids).count()
            OrderTb.objects.filter(id__in=ids).update(status=new_status)
            status_label = dict(OrderTb.ORDER_STATUS).get(new_status, new_status)
            messages.success(request, f'已将 {count} 条订单标记为「{status_label}」')
            _log('update', '订单', f'批量{count}条', f'批量标记为{status_label}')
    return redirect('index')


def order_detail(request, order_id):
    order = get_object_or_404(OrderTb.objects.prefetch_related('items__goods'), id=order_id)
    return render(request, 'logistics/order_detail.html', {
        'order': order, 'title': '订单详情', **_dashboard(),
    })


def order_print(request, order_id):
    order = get_object_or_404(OrderTb.objects.prefetch_related('items__goods'), id=order_id)
    return render(request, 'logistics/order_print.html', {'order': order})


def order_export(request):
    response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
    response['Content-Disposition'] = 'attachment; filename="order_export.csv"'
    writer = csv.writer(response)
    writer.writerow(['ID', '订单编号', '客户名称', '货物明细', '数量合计', '金额', '状态', '创建时间'])
    for o in OrderTb.objects.prefetch_related('items__goods').all().order_by('id'):
        item_names = ' / '.join(
            f'{it.goods.goods_name} x{it.quantity}'
            for it in o.items.all()
        )
        writer.writerow([
            o.id, o.order_number, o.customer_name,
            item_names,
            sum(it.quantity for it in o.items.all()),
            o.total_amount,
            o.get_status_display(),
            o.created_at.strftime('%Y-%m-%d %H:%M'),
        ])
    return response
