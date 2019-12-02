from collections import deque

from django.http import HttpResponseRedirect
from django.shortcuts import redirect, get_object_or_404, render
from django.urls import reverse_lazy, reverse
from django.utils.timezone import now
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, TemplateView, UpdateView, DeleteView

from webapp.forms import ManualOrderForm, OrderProductForm, ProductsFormset, BasketOrderCreateForm
from webapp.mixins import StatsMixin
from webapp.models import Product, OrderProduct, Order, ORDER_STATUS_CHOICES, ORDER_STATUS_CANCELED, \
    ORDER_STATUS_DELIVERED
from datetime import datetime
from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin
from django.contrib import messages


class IndexView(StatsMixin, ListView):
    model = Product
    template_name = 'index.html'

    def get_queryset(self):
        return Product.objects.filter(in_order=True)


class ProductView(StatsMixin, DetailView):
    model = Product
    template_name = 'product/detail.html'


class ProductCreateView(PermissionRequiredMixin, StatsMixin, CreateView):
    model = Product
    template_name = 'product/create.html'
    fields = ('name', 'category', 'price', 'photo', 'in_order')
    permission_required = 'webapp.add_product', 'webapp.can_have_piece_of_pizza'
    permission_denied_message = '403 Доступ запрещён!'

    def get_success_url(self):
        return reverse('webapp:product_detail', kwargs={'pk': self.object.pk})


class ProductUpdateView(LoginRequiredMixin, StatsMixin, UpdateView):
    model = Product
    template_name = 'product/update.html'
    fields = ('name', 'category', 'price', 'photo', 'in_order')
    context_object_name = 'product'

    def get_success_url(self):
        return reverse('webapp:product_detail', kwargs={'pk': self.object.pk})


class ProductDeleteView(LoginRequiredMixin, StatsMixin, DeleteView):
    model = Product
    template_name = 'product/delete.html'
    success_url = reverse_lazy('webapp:index')
    context_object_name = 'product'

    def delete(self, request, *args, **kwargs):
        product = self.object = self.get_object()
        product.in_order = False
        product.save()
        return HttpResponseRedirect(self.get_success_url())


class BasketChangeView(StatsMixin, View):
    def get(self, request, *args, **kwargs):
        products = request.session.get('products', [])

        pk = request.GET.get('pk')
        action = request.GET.get('action')
        next_url = request.GET.get('next', reverse('webapp:index'))

        if action == 'add':
            product = get_object_or_404(Product, pk=pk)
            if product.in_order:
                products.append(pk)
        else:
            for product_pk in products:
                if product_pk == pk:
                    products.remove(product_pk)
                    break

        request.session['products'] = products
        request.session['products_count'] = len(products)

        return redirect(next_url)


class BasketView(StatsMixin, CreateView):
    model = Order
    form_class = BasketOrderCreateForm
    template_name = 'product/basket.html'
    success_url = reverse_lazy('webapp:index')

    def get_context_data(self, **kwargs):
        basket, basket_total = self._prepare_basket()
        kwargs['basket'] = basket
        kwargs['basket_total'] = basket_total
        return super().get_context_data(**kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        if self._basket_empty():
            form.add_error(None, 'В корзине отсутствуют товары!')
            return self.form_invalid(form)
        response = super().form_valid(form)
        self._save_order_products()
        self._clean_basket()
        messages.success(self.request, 'Заказ оформлен!')
        return response

    def _prepare_basket(self):
        totals = self._get_totals()
        basket = []
        basket_total = 0
        for pk, qty in totals.items():
            product = Product.objects.get(pk=int(pk))
            total = product.price * qty
            basket_total += total
            basket.append({'product': product, 'qty': qty, 'total': total})
        return basket, basket_total

    def _get_totals(self):
        products = self.request.session.get('products', [])
        totals = {}
        for product_pk in products:
            if product_pk not in totals:
                totals[product_pk] = 0
            totals[product_pk] += 1
        return totals

    def _basket_empty(self):
        products = self.request.session.get('products', [])
        return len(products) == 0

    def _save_order_products(self):
        totals = self._get_totals()
        for pk, qty in totals.items():
            OrderProduct.objects.create(product_id=pk, order=self.object, amount=qty)

    def _clean_basket(self):
        if 'products' in self.request.session:
            self.request.session.pop('products')
        if 'products_count' in self.request.session:
            self.request.session.pop('products_count')


class OrderListView(LoginRequiredMixin, ListView):
    template_name = 'order/list.html'
    context_object_name = 'orders'
    model = Order

    def get_queryset(self):
        if self.request.user.has_perm('webapp.view_order'):
            return Order.objects.all().order_by('-created_at')
        return self.request.user.orders.all().order_by('-created_at')


class OrderDetailView(LoginRequiredMixin, DetailView):
    template_name = 'order/detail.html'
    model = Order

    def get_queryset(self):
        if self.request.user.has_perm('webapp.view_order'):
            return Order.objects.all()
        return self.request.user.orders.all()


class OrderCreateView(PermissionRequiredMixin, CreateView):
    model = Order
    form_class = ManualOrderForm
    template_name = 'order/create.html'
    permission_required = 'webapp.add_order'

    def get_context_data(self, **kwargs):
        if 'formset' not in kwargs:
            kwargs['formset'] = ProductsFormset()
        kwargs['product_list'] = Product.objects.filter(in_order=True)
        return super().get_context_data(**kwargs)

    def post(self, request, *args, **kwargs):
        self.object = None
        form = self.get_form()
        formset = ProductsFormset(data=request.POST)
        if form.is_valid() and formset.is_valid():
            return self.form_valid(form, formset)
        return self.form_invalid(form, formset)

    def form_valid(self, form, formset):
        self.object = form.save()
        formset.instance = self.object
        formset.save()
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form, formset):
        return self.render_to_response(self.get_context_data(form=form, formset=formset))

    def get_success_url(self):
        return reverse('webapp:order_detail', kwargs={'pk': self.object.pk})


class OrderUpdateView(PermissionRequiredMixin, UpdateView):
    model = Order
    form_class = ManualOrderForm
    template_name = 'order/update.html'
    context_object_name = 'order'
    permission_required = 'webapp.change_order'

    def get_context_data(self, **kwargs):
        if 'formset' not in kwargs:
            kwargs['formset'] = ProductsFormset(instance=self.object)
        return super().get_context_data(**kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        formset = ProductsFormset(instance=self.object, data=request.POST)
        if form.is_valid() and formset.is_valid():
            return self.form_valid(form, formset)
        return self.form_invalid(form, formset)

    def form_valid(self, form, formset):
        self.object = form.save()
        formset.save()
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form, formset):
        return self.render_to_response(self.get_context_data(form=form, formset=formset))

    def get_success_url(self):
        return reverse('webapp:order_detail', kwargs={'pk': self.object.pk})


class OrderDeliverView(PermissionRequiredMixin, View):
    permission_required = 'webapp.deliver_order'

    def get(self, request, *args, **kwargs):
        order = get_object_or_404(Order, pk=kwargs.get('pk'))
        order.status = ORDER_STATUS_DELIVERED
        order.save()
        return redirect('webapp:order_list')


class OrderCancelView(PermissionRequiredMixin, View):
    permission_required = 'webapp.delete_order'

    def get(self, request, *args, **kwargs):
        order = get_object_or_404(Order, pk=kwargs.get('pk'))
        order.status = ORDER_STATUS_CANCELED
        order.save()
        return redirect('webapp:order_list')


class OrderProductCreateView(PermissionRequiredMixin, CreateView):
    model = OrderProduct
    form_class = OrderProductForm
    template_name = 'order_product/create.html'
    permission_required = 'webapp.create_orderproduct'

    def get_context_data(self, **kwargs):
        kwargs['order'] = self.get_order()
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        form.instance.order = self.get_order()
        return super().form_valid(form)

    def get_order(self):
        return get_object_or_404(Order, pk=self.kwargs.get('pk'))

    def get_success_url(self):
        return reverse('webapp:order_detail', kwargs={'pk': self.object.order.pk})


class OrderProductUpdateView(PermissionRequiredMixin, UpdateView):
    model = OrderProduct
    form_class = OrderProductForm
    context_object_name = 'order_product'
    template_name = 'order_product/update.html'
    permission_required = 'webapp.change_orderproduct'

    def get_success_url(self):
        return reverse('webapp:order_detail', kwargs={'pk': self.object.order.pk})


class OrderProductDeleteView(PermissionRequiredMixin, DeleteView):
    model = OrderProduct
    template_name = 'order_product/delete.html'
    context_object_name = 'order_product'
    permission_required = 'webapp.delete_orderproduct'

    def get_success_url(self):
        return reverse('webapp:order_detail', kwargs={'pk': self.object.order.pk})