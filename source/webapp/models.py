from django.conf import settings
from django.db import models


CATEGORY_CHOICES = (
    ('other', 'Другое'),
    ('food', 'Еда'),
    ('clothes', 'Одежда'),
    ('household', 'Товары для дома'),
)


class Product(models.Model):
    name = models.CharField(max_length=200, verbose_name='Товар')
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default=CATEGORY_CHOICES[0][0],
                                verbose_name='Категория')
    photo = models.ImageField(upload_to='product_images', null=True, blank=True, verbose_name='Фото')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена')
    in_order = models.BooleanField(verbose_name='В наличии', default=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
        permissions = [
            ('can_have_piece_of_pizza', 'Может съесть кусочек пиццы'),
        ]


ORDER_STATUS_DELIVERED = 'delivered'
ORDER_STATUS_CANCELED = 'canceled'
ORDER_STATUS_CHOICES = (
    ('new', 'Новый'),
    ('payed', 'Оплачен'),
    ('processing', 'Обработка'),
    (ORDER_STATUS_DELIVERED, 'Доставлен'),
    (ORDER_STATUS_CANCELED, 'Отменён')
)


class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL,
                             verbose_name='Пользователь', related_name='orders')
    first_name = models.CharField(max_length=100, verbose_name='Имя', null=True, blank=True)
    last_name = models.CharField(max_length=100, verbose_name='Фамилия', null=True, blank=True)
    email = models.EmailField(max_length=50, verbose_name='Email', null=True, blank=True)
    phone = models.CharField(max_length=20, verbose_name='Телефон')
    products = models.ManyToManyField(Product, through='OrderProduct', through_fields=('order', 'product'),
                                      verbose_name='Товары', related_name='orders')
    status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default=ORDER_STATUS_CHOICES[0][0],
                              verbose_name='Статус')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата изменения')

    def __str__(self):
        return "{} ({})".format(self.created_at.strftime('%Y-%m-%d %H:%M:%S'), self.get_status_display())

    def get_total(self):
        total = 0
        for order_product in self.order_products.all():
            total += order_product.get_total()
        return total

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        permissions = [('deliver_order', 'Может доставить заказ')]


class OrderProduct(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, verbose_name='Заказ', related_name='order_products')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Товар', related_name='order_products')
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Количество')

    def __str__(self):
        return "{} - {}".format(self.product, self.order)

    def get_total(self):
        return self.amount * self.product.price

    class Meta:
        verbose_name = 'Товар в заказе'
        verbose_name_plural = 'Товары в заказах'