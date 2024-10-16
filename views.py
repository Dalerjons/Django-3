from random import randint

from django.shortcuts import render, redirect
from .models import *
from django.views.generic import ListView, DetailView
from django.contrib.auth import login, logout
from .forms import LoginForm, RegisterForm, ReviewForm, CustomerForm, ShippingForm
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from .utils import CartForAuthenticatedUser, get_cart_data
from shop import settings
import stripe


# Create your views here.

class ProductList(ListView):
    model = Product
    context_object_name = 'categories'
    template_name = 'store/product_list.html'
    extra_context = {
        'title': 'Main page'
    }

    def get_queryset(self):
        categories = Category.objects.filter(parent=None)
        return categories


class CategoryPage(ListView):
    model = Product
    context_object_name = 'products'
    template_name = 'store/category_page.html'  # Указал для какой страницы данная вьюшка
    paginate_by = 3

    # Метод для получения товаров
    def get_queryset(self):
        sort_field = self.request.GET.get('sort')
        type_field = self.request.GET.get('type')

        if type_field:
            products = Product.objects.filter(category__slug=type_field)
            return products

        main_category = Category.objects.get(slug=self.kwargs['slug'])  # По slug получ глав категорию
        subcategories = main_category.subcategories.all()  # Из категории получи подкатегории
        products = Product.objects.filter(category__in=subcategories)  # Получ все продукты подкатегорий
        if sort_field:
            products = products.order_by(sort_field)

        return products

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data()
        main_category = Category.objects.get(slug=self.kwargs['slug'])
        context['category'] = main_category
        context['title'] = f'Категории: {main_category.title} '
        return context


class ProductDetail(DetailView):
    model = Product
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        product = Product.objects.get(slug=self.kwargs['slug'])
        context['title'] = f'{product.category}: {product.title}'

        products = Product.objects.all()
        data = []  # В этот список будут попадать рандомные товары
        for i in range(4):
            random_index = randint(0, len(products) - 1)
            p = products[random_index]
            if p not in data:
                data.append(p)

        context['products'] = data
        context['reviews'] = Review.objects.filter(product=product)
        if self.request.user.is_authenticated:
            context['review_form'] = ReviewForm()

        return context


def user_login(request):
    form = LoginForm(data=request.POST)
    if form.is_valid():
        user = form.get_user()
        login(request, user)
        page = request.META.get('HTTP_REFERER', 'product_list')  # Получаем аддрес страницы запроса
        messages.success(request, '"Successful login to account"')
        return redirect(page)
    else:
        page = request.META.get('HTTP_REFERER', 'product_list')  # Получаем аддрес страницы запроса
        messages.error(request, '"Incorrect login or password"')
        return redirect(page)


def user_logout(request):
    logout(request)
    page = request.META.get('HTTP_REFERER', 'product_list')  # Получаем аддрес страницы запроса
    messages.warning(request, '"You have logged out of your account"')
    return redirect(page)


def register_user(request):
    form = RegisterForm(data=request.POST)
    if form.is_valid():
        user = form.save()
        messages.success(request, '"Registration successful. Please log in to your account"')
    else:
        for field in form.errors:
            messages.error(request, form.errors[field].as_text())

    page = request.META.get('HTTP_REFERER', 'product_list')
    return redirect(page)


def save_review(request, slug):
    form = ReviewForm(data=request.POST)
    if form.is_valid():
        review = form.save(commit=False)
        review.author = request.user
        product = Product.objects.get(slug=slug)  # Получаем продукт
        review.product = product  # Добавили продукт для отзыва
        review.save()
        messages.success(request, 'Ваш отзыв оставлен')
    else:
        pass

    return redirect('product_detail', product.slug)


# Функция для добавления продукта
def save_favorite_product(request, slug):
    if request.user.is_authenticated:
        user = request.user
        product = Product.objects.get(slug=slug)
        favorite_products = FavoriteProduct.objects.filter(user=user)  # Получаем избранные товары пользователя
        if user:
            if product not in [i.product for i in favorite_products]:
                FavoriteProduct.objects.create(user=user, product=product)
                messages.success(request, '"Product added to favorites"')
            else:
                fav_product = FavoriteProduct.objects.get(user=user, product=product)
                fav_product.delete()
                messages.warning(request, '"Product removed from favorites"')

    else:
        messages.error(request, '"Please log in to add to favorites"')

    page = request.META.get('HTTP_REFERER', 'product_list')
    return redirect(page)


class FavoriteProductView(LoginRequiredMixin, ListView):
    model = FavoriteProduct
    context_object_name = 'products'
    template_name = 'store/favorite.html'
    login_url = 'product_list'

    # Нужно реализовать метод получения товаров избранного самого пользователя
    def get_queryset(self):
        user = self.request.user
        favorite_products = FavoriteProduct.objects.filter(user=user)
        products = [i.product for i in favorite_products]
        return products


# Функция для страницы корзины
def cart(request):
    cart_info = get_cart_data(request)

    context = {
        'title': 'Моя корзина',
        'order': cart_info['order'],
        'products': cart_info['products']
    }

    return render(request, 'store/cart.html', context)


# Функция для добавления товара в корзину
def to_cart(request, product_id, action):
    if request.user.is_authenticated:
        user_cart = CartForAuthenticatedUser(request, product_id, action)
        messages.success(request, '"Check your cart"')
        page = request.META.get('HTTP_REFERER', 'product_list')
        return redirect(page)
    else:
        messages.success(request, '"Please log in to add to the cart"')
        page = request.META.get('HTTP_REFERER', 'product_list')
        return redirect(page)


# Функция для страницы оформления заказа

def checkout(request):
    if request.user.is_authenticated:
        cart_info = get_cart_data(request)

        context = {
            'title': 'Оформления заказа',
            'order': cart_info['order'],
            'items': cart_info['products'],

            'customer_form': CustomerForm(),
            'shipping_form': ShippingForm()

        }
        return render(request, 'store/checkout.html', context)


# Функция для совершения оплаты и сохранения данных пользователя с Адресом доставки
def create_checkout_session(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    if request.method == 'POST':
        user_cart = CartForAuthenticatedUser(request)  # Получ корзину покупателя
        cart_info = user_cart.get_cart_info()  # Из корзины при помощи метода получаем информацию о корзине

        #  Сохранение данных покупателя
        customer_form = CustomerForm(data=request.POST)
        if customer_form.is_valid():
            customer = Customer.objects.get(user=request.user)  # Получили покупателя по пользователю
            customer.first_name = customer_form.cleaned_data['first_name']  # Указали имя покупателя по данным из формы
            customer.last_name = customer_form.cleaned_data['last_name']
            customer.save()

        # Сохранение данных Адреса доставки
        shipping_form = ShippingForm(data=request.POST)
        if shipping_form.is_valid():
            address = shipping_form.save(commit=False)
            address.customer = Customer.objects.get(user=request.user)
            address.order = user_cart.get_cart_info()['order']
            address.save()

        total_price = cart_info['cart_total_price']
        session = stripe.checkout.Session.create(
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': 'Покупка на сайте TOTEMBO'
                    },
                    'unit_amount': int(total_price * 100)
                },
                'quantity': 1

            }],
            mode='payment',
            success_url=request.build_absolute_uri(reverse('success')),
            cancel_url=request.build_absolute_uri(reverse('checkout'))
        )

        return redirect(session.url, 303)


# Функция для страницы успешной оплаты
def success_payment(request):
    user_cart = CartForAuthenticatedUser(request)
    user_cart.clear()  # После успешный оплаты вызвали метод что бы очистить корзину
    messages.success(request, '"Your payment was successful"')
    return render(request, 'store/success.html')


# Вюшка для очищения корзины
def clear_cart(request):
    user_cart = CartForAuthenticatedUser(request)
    order = user_cart.get_cart_info()['order']
    order_products = order.orderproduct_set.all()
    for order_product in order_products:
        quantity = order_product.quantity
        product = order_product.product
        order_product.delete()
        product.quantity += quantity
        product.save()
    return redirect('my_cart')


def save_mail(request):
    if request.user.is_authenticated:
        email = request.POST.get('email')
        user = request.user
        if email:
            try:
                Mail.objects.create(mail=email, user=user)
                messages.success(request, '"Your email has been saved."')
            except:
                messages.warning(request, '"Your email has been saved."')
        page = request.META.get('HTTP_REFERER', 'product_list')
        return redirect(page)


from shop import settings
from django.core.mail import send_mail


def send_mail_to_customer(request):
    if request.user.is_superuser:
        if request.method == 'POST':
            text = request.POST.get('text')
            mail_list = Mail.objects.all()
            for email in mail_list:
                mail = send_mail(
                    subject='We have new arrivals for you',
                    message=text,
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[email],  # Указали кому отправить
                    fail_silently=False
                )
                print(f'The newsletter has been sent to your email. {email}? - {bool(mail)}')
        else:
            pass
        return render(request, 'store/send_mail.html')

    else:
        return redirect('product_list')
