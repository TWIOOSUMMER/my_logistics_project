from django.db import models


class GoodsCategory(models.Model):
    name = models.CharField(max_length=30, unique=True, verbose_name='类别名称')

    class Meta:
        app_label = 'logistics'
        db_table = 'goods_category'
        verbose_name = '货物类别'
        verbose_name_plural = '货物类别'

    def __str__(self):
        return self.name


class GoodsTb(models.Model):
    goods_name = models.CharField(max_length=50, verbose_name='货物名称')
    category = models.ForeignKey(GoodsCategory, on_delete=models.PROTECT, verbose_name='货物类别')
    weight = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='重量(kg)')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='单价(元)')
    stock = models.IntegerField(default=0, verbose_name='库存数量')

    class Meta:
        app_label = 'logistics'
        db_table = 'goods_tb01'
        verbose_name = '货物信息'
        verbose_name_plural = '货物信息'

    def __str__(self):
        return self.goods_name


class OrderTb(models.Model):
    ORDER_STATUS = [
        ('pending', '待处理'),
        ('shipping', '运输中'),
        ('delivered', '已签收'),
        ('cancelled', '已取消'),
    ]

    order_number = models.CharField(max_length=30, unique=True, verbose_name='订单编号')
    customer_name = models.CharField(max_length=30, verbose_name='客户名称')
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, verbose_name='订单金额')
    status = models.CharField(max_length=20, choices=ORDER_STATUS, default='pending', verbose_name='订单状态')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        app_label = 'logistics'
        db_table = 'order_tb01'
        verbose_name = '订单信息'
        verbose_name_plural = '订单信息'

    def __str__(self):
        return self.order_number

    def recalc_total(self):
        total = self.items.aggregate(s=models.Sum(models.F('quantity') * models.F('unit_price')))['s'] or 0
        self.total_amount = total
        self.save(update_fields=['total_amount'])


class OrderItem(models.Model):
    order = models.ForeignKey(OrderTb, on_delete=models.CASCADE, related_name='items', verbose_name='所属订单')
    goods = models.ForeignKey(GoodsTb, on_delete=models.PROTECT, verbose_name='货物')
    quantity = models.IntegerField(default=1, verbose_name='数量')
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='单价(元)')

    class Meta:
        app_label = 'logistics'
        db_table = 'order_item'
        verbose_name = '订单明细'
        verbose_name_plural = '订单明细'

    @property
    def subtotal(self):
        return self.quantity * self.unit_price

    def __str__(self):
        return f'{self.order.order_number} - {self.goods.goods_name} x{self.quantity}'


class OperationLog(models.Model):
    ACTION_CHOICES = [
        ('create', '新增'),
        ('update', '修改'),
        ('delete', '删除'),
    ]

    action = models.CharField(max_length=10, choices=ACTION_CHOICES, verbose_name='操作类型')
    model_name = models.CharField(max_length=30, verbose_name='操作对象')
    object_name = models.CharField(max_length=100, verbose_name='对象名称')
    description = models.CharField(max_length=200, verbose_name='操作描述')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='操作时间')

    class Meta:
        app_label = 'logistics'
        db_table = 'operation_log'
        verbose_name = '操作日志'
        verbose_name_plural = '操作日志'

    def __str__(self):
        return f'{self.get_action_display()} - {self.object_name}'
