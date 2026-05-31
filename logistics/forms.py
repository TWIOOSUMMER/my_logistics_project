from django import forms
from .models import GoodsTb, OrderTb, GoodsCategory


class GoodsCategoryForm(forms.ModelForm):
    class Meta:
        model = GoodsCategory
        fields = ['name']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs['class'] = 'form-control'


class GoodsForm(forms.ModelForm):
    class Meta:
        model = GoodsTb
        fields = ['goods_name', 'category', 'weight', 'price', 'stock']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if name == 'category':
                field.widget.attrs['class'] = 'form-select'
            else:
                field.widget.attrs['class'] = 'form-control'

    def clean_weight(self):
        weight = self.cleaned_data.get('weight')
        if weight is not None and weight <= 0:
            raise forms.ValidationError('重量必须大于 0')
        return weight

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price is not None and price <= 0:
            raise forms.ValidationError('单价必须大于 0')
        return price

    def clean_stock(self):
        stock = self.cleaned_data.get('stock')
        if stock is not None and stock < 0:
            raise forms.ValidationError('库存数量不能为负数')
        return stock


class OrderForm(forms.ModelForm):
    class Meta:
        model = OrderTb
        fields = ['order_number', 'customer_name', 'status']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if name == 'status':
                field.widget.attrs['class'] = 'form-select'
            else:
                field.widget.attrs['class'] = 'form-control'
