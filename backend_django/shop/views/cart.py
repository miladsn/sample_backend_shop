import json
from django.http import JsonResponse, Http404
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404
from shop.models import Product, ProductOptionItem, Cart, CartItem


def get_or_create_cart(request):
    """Returns the shopping cart of the current user (whether logged in or a guest)."""
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
    else:
        if not request.session.session_key:
            request.session.create()
        session_key = request.session.session_key
        cart, _ = Cart.objects.get_or_create(session_key=session_key, user=None)
    return cart


@require_POST
def add_to_cart_view(request):
    """
    Add a product (with optional variant) to the temporary cart.

    Architecture Note (Locking & Concurrency):
    We deliberately avoid pessimistic locking (e.g., select_for_update) here because
    the shopping cart acts as a lightweight, temporary draft/wishlist state.
    Strict stock enforcement and concurrency locks are deferred to the Checkout/Payment
    flow to minimize database overhead during casual browsing.
    """
    try:
        # Support both JSON payloads and standard form-data
        if request.content_type == 'application/json':
            try:
                data = json.loads(request.body)
            except json.JSONDecodeError:
                return JsonResponse({'error': 'Invalid JSON format.'}, status=400)
        else:
            data = request.POST

        product_id = data.get('product_id')
        option_id = data.get('selected_option') or data.get('option_item_id')

        try:
            quantity = int(data.get('quantity', 1))
        except (ValueError, TypeError):
            return JsonResponse({'error': 'Invalid quantity value.'}, status=400)

        if quantity < 1:
            return JsonResponse({'error': 'Quantity must be at least 1.'}, status=400)

        product = get_object_or_404(Product, id=product_id, status=Product.ProductStatus.PUBLISHED)

        option_item = None
        if option_id:
            option_item = get_object_or_404(ProductOptionItem, id=option_id, product=product)

        # Soft stock limit check for better UX (not strictly locked)
        stock_limit = option_item.stock if (option_item and option_item.stock is not None) else product.stock

        cart = get_or_create_cart(request)
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            option_item=option_item,
            defaults={'quantity': 0}
        )

        new_quantity = cart_item.quantity + quantity
        if stock_limit is not None and new_quantity > stock_limit:
            return JsonResponse({
                'error': f'Insufficient stock available (Max available: {stock_limit})'
            }, status=400)

        cart_item.quantity = new_quantity
        cart_item.save()

        return JsonResponse({
            'message': 'Product added to cart successfully.',
            'cart_total_items': cart.total_items_count,
            'quantity': cart_item.quantity
        })

    except Http404:
        return JsonResponse({'error': 'Product or option not found.'}, status=404)
    except Exception:
        # Prevent exposing internal server details to the client
        return JsonResponse({'error': 'An internal server error occurred.'}, status=500)
