from django.db import models
from django.urls import reverse

# Create your models here.
from jazzmin.templatetags.jazzmin import User


class Category(models.Model):
    title = models.CharField(max_length=150, verbose_name='Category name')
    image = models.ImageField(upload_to='categories/', null=True, blank=True, verbose_name='Category image')
    slug = models.SlugField(unique=True, null=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True,
                               related_name='subcategories', verbose_name='Category')

    # Умная ссылка для категории
    def get_absolute_url(self):
        return reverse('category_page', kwargs={'slug': self.slug})

    # Метод для получения картинок катнгории
    def get_image_category(self):
        if self.image:
            return self.image.url
        else:
            return ''

    def __str__(self):
        return self.title

    def __repr__(self):
        return f'Category: pk={self.pk}, title={self.title}'

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'


class Product(models.Model):
    title = models.CharField(max_length=200, verbose_name='Product name')
    price = models.FloatField(verbose_name='Price')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Date of addition')
    quantity = models.IntegerField(default=0, verbose_name='Product quantity')
    description = models.TextField(default='Description will be soon', verbose_name='Product description')
    category = models.ForeignKey(Category, on_delete=models.CASCADE,
                                 verbose_name='Category', related_name='products')
    slug = models.SlugField(unique=True, null=True)
    size = models.IntegerField(default=30, verbose_name='Size')
    color = models.CharField(max_length=30, default='Grey', verbose_name='Color/Material')

    def get_absolute_url(self):
        return reverse('product_detail', kwargs={'slug': self.slug})

    def get_image_product(self):
        if self.images:
            try:
                return self.images.first().image.url
            except:
                return ''
        else:
            return ''

    def __str__(self):
        return self.title

    def __repr__(self):
        return f'Category: pk={self.pk}, title={self.title}, price={self.price}'

    class Meta:
        verbose_name = 'Product'
        verbose_name_plural = 'Products'


class Gallery(models.Model):
    image = models.ImageField(upload_to='products/', verbose_name='Image of products')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')


    class Meta:
        verbose_name = 'Image'
        verbose_name_plural = 'Images'


class Review(models.Model):
    text = models.TextField(verbose_name='Customer feedback')
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Customer')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Product feedback')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Feedback date')

    def __str__(self):
        return self.author.username

    class Meta:
        verbose_name = 'Feedback'
        verbose_name_plural = 'Feedbacks'


#  Моделька Избранного

class FavoriteProduct(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Customer')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Favorite product')

    def __str__(self):
        return self.product.title

    class Meta:
        verbose_name = 'Favorite'
        verbose_name_plural = 'Favorites'


class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='User')
    first_name = models.CharField(max_length=250, default='', verbose_name='Customer name')
    last_name = models.CharField(max_length=250, default='', verbose_name='Customer lastname')

    def __str__(self):
        return self.first_name

    class Meta:
        verbose_name = 'Customer'
        verbose_name_plural = 'Customers'


class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Customer')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Order date')
    is_completed = models.BooleanField(default=False, verbose_name='Complete order')
    shipping = models.BooleanField(default=True, verbose_name='Shipping')

    def __str__(self):
        return str(self.pk)

    class Meta:
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'

    # Метод для получения суммы заказа
    @property
    def get_cart_total_price(self):
        order_product = self.orderproduct_set.all()  # Здесь мы получаем заказанные продукты самого заказа
        total_price = sum([product.get_total_price for product in order_product])
        return total_price

    @property
    def get_cart_total_quantity(self):
        order_product = self.orderproduct_set.all()  # Здесь мы получаем заказанные продукты самого заказа
        total_quantity = sum([product.quantity for product in order_product])
        return total_quantity


class OrderProduct(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, verbose_name='Product')
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, verbose_name='Order')
    quantity = models.IntegerField(default=0, null=True, blank=True, verbose_name='Quantity')
    added_at = models.DateTimeField(auto_now_add=True, verbose_name='Date of addition')

    def __str__(self):
        return self.product.title

    class Meta:
        verbose_name = 'Ordered product'
        verbose_name_plural = 'Ordered products'

    # Метод который вернёт сумму товара в его кол-ве
    @property  # Декоратор нужен что бы можно было вызивать метод в другой модели (класса)
    def get_total_price(self):
        total_price = self.product.price * self.quantity
        return total_price


# Модель доставки
class ShippingAddress(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, verbose_name='Customer')
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, verbose_name='Order')
    address = models.CharField(max_length=300, verbose_name='Address ( street, building, flat num )')
    city = models.ForeignKey('City', on_delete=models.CASCADE, verbose_name='City')
    region = models.CharField(max_length=300, verbose_name='Region')
    phone = models.CharField(max_length=250, verbose_name='Phone number')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Delivery date')

    def __str__(self):
        return self.address

    class Meta:
        verbose_name = 'Delivery address'
        verbose_name_plural = 'Delivery addresses'


class City(models.Model):
    city = models.CharField(max_length=300, verbose_name='City')

    def __str__(self):
        return self.city

    class Meta:
        verbose_name = 'City'
        verbose_name_plural = 'Cities'




#  Модель для сохранения почт
class Mail(models.Model):
    mail = models.EmailField(unique=True, verbose_name='Mail name')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='User')


    def __str__(self):
        return self.mail



    class Meta:
        verbose_name = 'Mail'
        verbose_name_plural = 'Mail address'





