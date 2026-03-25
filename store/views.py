from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Q
from .models import Product, Category, Order, OrderItem
from .forms import ProductForm, CategoryForm, CheckoutForm, RegisterForm, LoginForm


def is_admin(user):
    return user.is_staff


# ─── HOME ──────────────────────────────────────────────────────────────────────

def home(request):
    products = Product.objects.filter(is_active=True)[:8]
    categories = Category.objects.all()
    return render(request, 'store/home.html', {'products': products, 'categories': categories})


# ─── PRODUCTS ──────────────────────────────────────────────────────────────────

def product_list(request):
    products = Product.objects.filter(is_active=True)
    categories = Category.objects.all()

    query = request.GET.get('q', '')
    category_slug = request.GET.get('category', '')

    if query:
        products = products.filter(Q(name__icontains=query) | Q(description__icontains=query))
    if category_slug:
        products = products.filter(category__slug=category_slug)

    return render(request, 'store/product_list.html', {
        'products': products,
        'categories': categories,
        'query': query,
        'selected_category': category_slug,
    })


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    return render(request, 'store/product_detail.html', {'product': product})


@user_passes_test(is_admin)
def product_create(request):
    form = ProductForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        form.save()
        messages.success(request, 'Product created successfully!')
        return redirect('product_list')
    return render(request, 'store/product_form.html', {'form': form, 'title': 'Add Product'})


@user_passes_test(is_admin)
def product_edit(request, slug):
    product = get_object_or_404(Product, slug=slug)
    form = ProductForm(request.POST or None, request.FILES or None, instance=product)
    if form.is_valid():
        form.save()
        messages.success(request, 'Product updated successfully!')
        return redirect('product_list')
    return render(request, 'store/product_form.html', {'form': form, 'title': 'Edit Product', 'product': product})


@user_passes_test(is_admin)
def product_delete(request, slug):
    product = get_object_or_404(Product, slug=slug)
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Product deleted.')
        return redirect('product_list')
    return render(request, 'store/product_confirm_delete.html', {'product': product})


# ─── CATEGORIES ────────────────────────────────────────────────────────────────

@user_passes_test(is_admin)
def category_list(request):
    categories = Category.objects.all()
    return render(request, 'store/category_list.html', {'categories': categories})


@user_passes_test(is_admin)
def category_create(request):
    form = CategoryForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, 'Category created!')
        return redirect('category_list')
    return render(request, 'store/category_form.html', {'form': form, 'title': 'Add Category'})


@user_passes_test(is_admin)
def category_edit(request, slug):
    category = get_object_or_404(Category, slug=slug)
    form = CategoryForm(request.POST or None, instance=category)
    if form.is_valid():
        form.save()
        messages.success(request, 'Category updated!')
        return redirect('category_list')
    return render(request, 'store/category_form.html', {'form': form, 'title': 'Edit Category'})


@user_passes_test(is_admin)
def category_delete(request, slug):
    category = get_object_or_404(Category, slug=slug)
    if request.method == 'POST':
        category.delete()
        messages.success(request, 'Category deleted.')
        return redirect('category_list')
    return render(request, 'store/category_confirm_delete.html', {'category': category})


# ─── CART ──────────────────────────────────────────────────────────────────────

def get_cart(request):
    return request.session.get('cart', {})


def cart_view(request):
    cart = get_cart(request)
    cart_items = []
    total = 0
    for slug, item in cart.items():
        subtotal = item['price'] * item['quantity']
        total += subtotal
        cart_items.append({**item, 'slug': slug, 'subtotal': subtotal})
    return render(request, 'store/cart.html', {'cart_items': cart_items, 'total': total})


def cart_add(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    cart = get_cart(request)
    if slug in cart:
        cart[slug]['quantity'] += 1
    else:
        cart[slug] = {
            'name': product.name,
            'price': float(product.price),
            'quantity': 1,
            'image': product.image.url if product.image else '',
        }
    request.session['cart'] = cart
    messages.success(request, f'"{product.name}" added to cart.')
    return redirect(request.META.get('HTTP_REFERER', 'product_list'))


def cart_remove(request, slug):
    cart = get_cart(request)
    if slug in cart:
        del cart[slug]
        request.session['cart'] = cart
        messages.info(request, 'Item removed from cart.')
    return redirect('cart_view')


def cart_update(request, slug):
    cart = get_cart(request)
    qty = int(request.POST.get('quantity', 1))
    if slug in cart:
        if qty <= 0:
            del cart[slug]
        else:
            cart[slug]['quantity'] = qty
        request.session['cart'] = cart
    return redirect('cart_view')


def cart_clear(request):
    request.session['cart'] = {}
    messages.info(request, 'Cart cleared.')
    return redirect('cart_view')


# ─── CHECKOUT / ORDERS ─────────────────────────────────────────────────────────

@login_required
def checkout(request):
    cart = get_cart(request)
    if not cart:
        messages.warning(request, 'Your cart is empty.')
        return redirect('cart_view')

    total = sum(i['price'] * i['quantity'] for i in cart.values())
    form = CheckoutForm(request.POST or None)

    if form.is_valid():
        order = form.save(commit=False)
        order.user = request.user
        order.total_price = total
        order.save()

        for slug, item in cart.items():
            try:
                product = Product.objects.get(slug=slug)
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=item['quantity'],
                    price=item['price'],
                )
                product.stock = max(0, product.stock - item['quantity'])
                product.save()
            except Product.DoesNotExist:
                pass

        request.session['cart'] = {}
        messages.success(request, f'Order #{order.id} placed successfully!')
        return redirect('order_detail', order_id=order.id)

    return render(request, 'store/checkout.html', {'form': form, 'cart': cart, 'total': total})


@login_required
def order_list(request):
    orders = Order.objects.filter(user=request.user)
    return render(request, 'store/order_list.html', {'orders': orders})


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'store/order_detail.html', {'order': order})


@user_passes_test(is_admin)
def admin_orders(request):
    orders = Order.objects.all()
    return render(request, 'store/admin_orders.html', {'orders': orders})


@user_passes_test(is_admin)
def admin_order_update(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        order.status = request.POST.get('status', order.status)
        order.save()
        messages.success(request, 'Order status updated.')
        return redirect('admin_orders')
    return render(request, 'store/admin_order_update.html', {'order': order})


# ─── AUTH ──────────────────────────────────────────────────────────────────────

def register_view(request):
    form = RegisterForm(request.POST or None)
    if form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, 'Account created! Welcome.')
        return redirect('home')
    return render(request, 'store/auth.html', {'form': form, 'title': 'Register', 'action': 'register'})


def login_view(request):
    form = LoginForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.get_user()
        login(request, user)
        messages.success(request, f'Welcome back, {user.username}!')
        return redirect('home')
    return render(request, 'store/auth.html', {'form': form, 'title': 'Login', 'action': 'login'})


def logout_view(request):
    logout(request)
    messages.info(request, 'Logged out successfully.')
    return redirect('home')
