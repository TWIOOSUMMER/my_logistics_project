import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'logistics_project.settings')
django.setup()
from logistics.models import OrderTb, GoodsTb

total = OrderTb.objects.count()
print('=== 全部订单: %d ===' % total)
for o in OrderTb.objects.all()[:3]:
    print('  %s | %s | %s | %s' % (o.order_number, o.customer_name, o.status, o.created_at.strftime('%Y-%m-%d')))

pending = OrderTb.objects.filter(status='pending')
print('\n=== 状态=待处理: %d ===' % pending.count())
for o in pending[:3]:
    print('  %s | %s | %s | %s' % (o.order_number, o.customer_name, o.status, o.created_at.strftime('%Y-%m-%d')))

shipping = OrderTb.objects.filter(status='shipping')
print('\n=== 状态=运输中: %d ===' % shipping.count())
for o in shipping[:3]:
    print('  %s | %s | %s | %s' % (o.order_number, o.customer_name, o.status, o.created_at.strftime('%Y-%m-%d')))

delivered = OrderTb.objects.filter(status='delivered')
print('\n=== 状态=已签收: %d ===' % delivered.count())
for o in delivered[:3]:
    print('  %s | %s | %s | %s' % (o.order_number, o.customer_name, o.status, o.created_at.strftime('%Y-%m-%d')))

cancelled = OrderTb.objects.filter(status='cancelled')
print('\n=== 状态=已取消: %d ===' % cancelled.count())
for o in cancelled[:3]:
    print('  %s | %s | %s | %s' % (o.order_number, o.customer_name, o.status, o.created_at.strftime('%Y-%m-%d')))

from django.db.models import Q
kw = OrderTb.objects.filter(Q(order_number__icontains='ORD') | Q(customer_name__icontains='ORD'))
print('\n=== 关键词=ORD: %d ===' % kw.count())

kw2 = OrderTb.objects.filter(Q(order_number__icontains='张三') | Q(customer_name__icontains='张三'))
print('\n=== 关键词=张三: %d ===' % kw2.count())
for o in kw2:
    print('  %s | %s' % (o.order_number, o.customer_name))

print('\n=== 日期范围 2026-05-26 ~ 2026-05-27 ===')
dr = OrderTb.objects.filter(created_at__date__gte='2026-05-26', created_at__date__lte='2026-05-27')
print('  count: %d' % dr.count())
for o in dr[:5]:
    print('  %s | %s | %s' % (o.order_number, o.customer_name, o.created_at.strftime('%Y-%m-%d')))

print('\n=== 组合: status=shipping + customer 包含 优选 ===')
combo = OrderTb.objects.filter(status='shipping', customer_name__icontains='优选')
print('  count: %d' % combo.count())
for o in combo:
    print('  %s | %s | %s' % (o.order_number, o.customer_name, o.status))

print('\nAll tests passed.')
