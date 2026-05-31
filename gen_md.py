import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'logistics_project.settings')
django.setup()
from logistics.models import *

models = [GoodsCategory, GoodsTb, OrderTb, OrderItem, OperationLog]

sep = ' / '

for m in models:
    print('### %s（%s）' % (m._meta.db_table, m._meta.verbose_name))
    print()
    print('| 字段名 | 类型 | 约束 | 描述 |')
    print('|--------|------|------|------|')
    for f in m._meta.fields:
        constraints = []
        if f.primary_key:
            constraints.append('PK')
        if f.unique:
            constraints.append('UK')
        if f.null:
            constraints.append('NULL')
        if f.has_default():
            constraints.append('DEFAULT=%s' % f.default)
        rel = getattr(f, 'related_model', None)
        if rel:
            constraints.append('FK->%s' % rel._meta.db_table)
        if not f.null and not f.primary_key and not f.has_default():
            constraints.append('NOT NULL')
        desc = getattr(f, 'verbose_name', '-')
        c_str = sep.join(constraints) if constraints else '-'
        print('| %s | %s | %s | %s |' % (f.name, f.get_internal_type(), c_str, desc))
    print()
