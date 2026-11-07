# shop/views/product
import json
from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.serializers.json import DjangoJSONEncoder
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST
from django.views.generic import DeleteView, ListView

from media_files.services import FileManager
from shop.forms import ProductForm
from shop.models import Product, ProductAlbum, ProductOptionValue, ProductOptionItem, ProductOptionGroup, \
    ProductAttribute
from shop.views.helpers import create_module_breadcrumbs
from django.db import transaction


def get_default_breadcrumbs(without_link=False):
    return create_module_breadcrumbs(
        "محصولات", "shop:product_list", without_link
    )


class ProductListView(PermissionRequiredMixin, ListView):
    model = Product
    template_name = 'shop/product_list.html'
    context_object_name = 'products'
    permission_required = 'shop.view_product'
    paginate_by = 10

    def get_queryset(self):
        # Tags are displayed in the list table; avoid N+1 queries.
        return super().get_queryset().prefetch_related("tags", "categories")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        breadcrumbs = get_default_breadcrumbs(True)
        context["breadcrumbs"] = breadcrumbs
        return context


@permission_required('shop.add_product', raise_exception=True)
def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            option_error = validate_option_duplicates(request.POST.get('options_data', ''))
            if option_error:
                form.add_error(None, option_error)
            else:
                return create_product_from_form(request, form)
    else:
        form = ProductForm()

    context = {'form': form, **get_product_form_context()}
    return render(request, 'shop/product_form.html', context)


def create_product_from_form(request, form):
    with transaction.atomic():
        product = form.save(commit=False)

        uploaded_image = request.FILES.get('featured_image_file')
        if uploaded_image:
            stored_file = FileManager.store(
                uploaded_file=uploaded_image,
                path='products',
                user=request.user,
                is_secure=False
            )
            product.featured_image_id = stored_file.id

        product.save()
        form.save_m2m()

        raw_attributes = request.POST.get('attributes_json', '[]')
        sync_product_attributes(product, raw_attributes)

        options_data_str = request.POST.get('options_data', '')
        save_product_options(product, options_data_str)

        handle_album_uploads(request, product)

    messages.success(request, 'محصول با موفقیت ایجاد شد.')

    save_action = request.POST.get('save_action', 'exit')
    if save_action == 'stay':
        return redirect('shop:product_update', pk=product.pk)
    return redirect('shop:product_list')

@permission_required('shop.change_product', raise_exception=True)
def product_update(request, pk):
    title = 'ویرایش محصول'
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':

        form = ProductForm(
            request.POST,
            request.FILES,
            instance=product
        )

        if form.is_valid():

            uploaded_image = request.FILES.get(
                'featured_image_file'
            )

            image_file_id = None

            if uploaded_image:
                stored_file = FileManager.store(
                    uploaded_file=uploaded_image,
                    user=request.user,
                    is_secure=False,
                )

                image_file_id = stored_file.id

            product = form.save(commit=False)

            if image_file_id:
                product.featured_image_id = image_file_id

            # در product_create و product_update:
            options_data_str = request.POST.get('options_data', '')
            duplicate_error = validate_option_duplicates(options_data_str)
            if duplicate_error:
                messages.error(request, duplicate_error)
                context = get_product_form_context(product)
                context.update(
                    {'form': form, 'title': title, 'breadcrumbs': get_default_breadcrumbs(), 'is_edit': True})
                return render(request, 'shop/product_form.html', context)
            option_error = validate_locked_product_options(product, options_data_str)
            if option_error:
                messages.error(request, option_error)
                context = get_product_form_context(product)
                context.update(
                    {'form': form, 'title': title, 'breadcrumbs': get_default_breadcrumbs(), 'is_edit': True})
                return render(request, 'shop/product_form.html', context)
            product.save()
            form.save_m2m()

            raw_attributes = request.POST.get('attributes_json', '[]')
            sync_product_attributes(product, raw_attributes)

            save_product_options(product, options_data_str)

            handle_album_uploads(request, product)

            messages.success(
                request,
                'محصول با موفقیت به‌روزرسانی شد.'
            )

            if request.POST.get('save_action') == 'stay':
                return redirect('shop:product_update', pk=product.pk)
            return redirect('shop:product_list')

        messages.error(
            request,
            'اطلاعات فرم صحیح نیست.'
        )
    else:
        form = ProductForm(instance=product)
    breadcrumbs = get_default_breadcrumbs()
    breadcrumbs.append({"title": title, "url": None})
    context = get_product_form_context(product)
    context.update({'form': form, 'title': title, 'breadcrumbs': breadcrumbs, 'is_edit': True})
    return render(request, 'shop/product_form.html', context)


class ProductDeleteView(PermissionRequiredMixin, DeleteView):
    model = Product
    success_url = reverse_lazy('shop:product_list')
    permission_required = 'shop.delete_product'

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'محصول با موفقیت حذف شد.')
        return super().delete(request, *args, **kwargs)


def handle_album_uploads(request, product):
    album_files = request.FILES.getlist('album_files')
    if album_files:
        current_max_order = product.album_items.count()
        for index, uploaded_file in enumerate(album_files, start=current_max_order):
            stored_file = FileManager.store(
                uploaded_file=uploaded_file,
                path=f"products/{product.id}/album",
                user=request.user,
                is_secure=False
            )
            media_type = (
                ProductAlbum.MediaType.VIDEO
                if stored_file.group == 'video'
                else ProductAlbum.MediaType.IMAGE
            )
            ProductAlbum.objects.create(
                product=product,
                file_id=stored_file.id,
                media_type=media_type,
                display_order=index
            )


@require_POST
@permission_required('shop.change_product', raise_exception=True)
def product_album_delete(request, pk):
    item = get_object_or_404(ProductAlbum, pk=pk)
    product_pk = item.product_id

    # If you need to completely remove the File entity from the Media Center:
    # if item.file:
    #     item.file.delete()
    item.file.delete()
    item.delete()

    messages.success(request, 'آیتم با موفقیت از آلبوم حذف شد.')
    return redirect('shop:product_update', pk=product_pk)


def save_product_options(product, options_json_str):
    """
    پردازش و ذخیره آپشن‌های محصول از روی رشته JSON
    ساختار داده به صورت درختی (والد - فرزند) پشتیبانی می‌شود.
    """
    if not options_json_str:
        return

    try:
        options_data = json.loads(options_json_str)
    except (json.JSONDecodeError, TypeError):
        return

    with transaction.atomic():
        retained_ids = []
        for item_data in options_data:
            val_id = item_data.get('value_id')
            if not val_id:
                continue
            val_obj = ProductOptionValue.objects.filter(pk=val_id).first()
            if not val_obj:
                continue

            parent_item, _ = ProductOptionItem.objects.update_or_create(
                product=product, option_value=val_obj, parent=None,
                defaults={'price': item_data.get('price') or None,
                          'stock': item_data.get('stock') or 0},
            )
            retained_ids.append(parent_item.pk)
            for child_data in item_data.get('children', []):
                child_value = ProductOptionValue.objects.filter(
                    pk=child_data.get('value_id')
                ).first()
                if not child_value or child_value.group_id == val_obj.group_id:
                    continue
                child, _ = ProductOptionItem.objects.update_or_create(
                    product=product, option_value=child_value, parent=parent_item,
                    defaults={'price': child_data.get('price') or None,
                              'stock': child_data.get('stock') or 0},
                )
                retained_ids.append(child.pk)

        # Keep existing rows for unchanged options so cart references remain valid.
        product.option_items.exclude(pk__in=retained_ids).delete()


def validate_locked_product_options(product, options_json_str):
    """In editing, the parent/child group cannot be changed; only deletion is permitted."""
    try:
        data = json.loads(options_json_str or '[]')
    except (json.JSONDecodeError, TypeError):
        return 'ساختار آپشن‌ها نامعتبر است.'
    current = ProductOptionItem.objects.filter(product=product).select_related('option_value')
    parents = [i for i in current if i.parent_id is None]
    parent_groups = {i.option_value.group_id for i in parents}
    existing_child_groups = {i.option_value.group_id for i in current if i.parent_id is not None}
    existing_parent_group = next(iter(parent_groups), None)
    submitted_parent_groups = {int(p.get('group_id', 0)) for p in data if p.get('group_id')}
    parent_value_ids = [int(p.get('value_id')) for p in data if p.get('value_id')]
    if len(parent_value_ids) != len(set(parent_value_ids)):
        return 'یک مقدار اصلی نمی‌تواند دوبار ثبت شود.'
    if len(submitted_parent_groups) > 1:
        return 'همه گزینه‌های اصلی باید از یک گروه باشند.'
    # An empty array means the user has removed all options; this state is permitted.
    if submitted_parent_groups and existing_parent_group is not None and submitted_parent_groups != {
        existing_parent_group}:
        return 'گروه اصلی در ویرایش قابل تغییر نیست؛ ابتدا آپشن‌های قبلی را حذف کنید.'

    submitted_child_groups = set()
    for parent in data:
        parent_group_id = int(parent.get('group_id', 0))
        child_value_ids = [int(c.get('value_id')) for c in parent.get('children', []) if c.get('value_id')]
        if len(child_value_ids) != len(set(child_value_ids)):
            return 'یک مقدار فرعی نمی‌تواند برای یک گزینه دوبار ثبت شود.'
        for child in parent.get('children', []):
            child_group_id = int(child.get('group_id', 0))
            if child_group_id == parent_group_id:
                return 'گروه فرعی باید با گروه اصلی متفاوت باشد.'
            submitted_child_groups.add(child_group_id)
    if len(submitted_child_groups) > 1:
        return 'همه گزینه‌های فرعی باید از یک گروه باشند.'
    if existing_child_groups and submitted_child_groups and not submitted_child_groups.issubset(existing_child_groups):
        return 'گروه فرعی در ویرایش قابل تغییر نیست؛ ابتدا آپشن‌های قبلی را حذف کنید.'
    return None


def validate_option_duplicates(options_json_str):
    """Validate the submitted option tree before changing product data."""
    try:
        data = json.loads(options_json_str or '[]')
        if not isinstance(data, list):
            raise ValueError
        parent_ids = set()
        submitted_values = []
        for parent in data:
            if not isinstance(parent, dict):
                raise ValueError
            parent_id = int(parent['value_id'])
            parent_group = int(parent['group_id'])
            submitted_values.append((parent_id, parent_group))
            if parent_id in parent_ids:
                return 'یک مقدار اصلی نمی‌تواند دوبار ثبت شود.'
            parent_ids.add(parent_id)
            children = parent.get('children', [])
            if not isinstance(children, list):
                raise ValueError
            child_ids = set()
            for child in children:
                if not isinstance(child, dict):
                    raise ValueError
                child_id = int(child['value_id'])
                child_group = int(child['group_id'])
                if child_group == parent_group:
                    return 'گروه فرعی باید با گروه اصلی متفاوت باشد.'
                submitted_values.append((child_id, child_group))
                if child_id in child_ids:
                    return 'یک مقدار فرعی نمی‌تواند برای یک گزینه دوبار ثبت شود.'
                child_ids.add(child_id)
            for item in [parent, *children]:
                stock = int(item.get('stock') or 0)
                price = item.get('price')
                if stock < 0 or (price not in (None, '') and (not Decimal(str(price)).is_finite() or Decimal(str(price)) < 0)):
                    raise ValueError
        actual_groups = dict(ProductOptionValue.objects.filter(
            pk__in=[value_id for value_id, _ in submitted_values]
        ).values_list('pk', 'group_id'))
        if any(actual_groups.get(value_id) != group_id for value_id, group_id in submitted_values):
            return 'مقدار یا گروه آپشن نامعتبر است.'
    except (ValueError, TypeError, KeyError, InvalidOperation):
        return 'ساختار آپشن‌ها نامعتبر است.'
    return None


def get_product_form_context(product=None):
    """
   Helper method for preparing the shared context for the product form (including options and technical specifications)
    """
    # This data structure should match the current option.py and product_options.js models
    # Be coordinated. Previously, there were old names like ``options'' and
    # `product_options` was used.
    groups = ProductOptionGroup.objects.prefetch_related('values').all()
    option_groups_json = json.dumps([
        {
            'id': group.id,
            'title': group.title,
            'type': group.group_type,
            'values': [
                {
                    'id': value.id,
                    'title': value.title,
                    'value': value.value_data,
                }
                for value in group.values.all()
            ],
        }
        for group in groups
    ], ensure_ascii=False, cls=DjangoJSONEncoder)

    existing_options_json = "[]"
    existing_attributes = []  # Empty list for product creation mode

    if product and product.pk:
        # Retrieving the product's selected options via the actual `Product.option_items` relationship
        parent_items = (
            product.option_items
            .filter(parent__isnull=True)
            .select_related('option_value')
            .prefetch_related('children__option_value')
        )
        existing_options = []
        for parent in parent_items:
            existing_options.append({
                'group_id': parent.option_value.group_id,
                'value_id': parent.option_value_id,
                'value_title': parent.option_value.title,
                'price': float(parent.price) if parent.price is not None else None,
                'stock': parent.stock,
                'children': [
                    {
                        'group_id': child.option_value.group_id,
                        'value_id': child.option_value_id,
                        'value_title': child.option_value.title,
                        'price': float(child.price) if child.price is not None else None,
                        'stock': child.stock,
                    }
                    for child in parent.children.all()
                ],
            })
        existing_options_json = json.dumps(
            existing_options,
            ensure_ascii=False,
            cls=DjangoJSONEncoder,
        )

        # Retrieving the product's existing technical specifications from the database
        existing_attributes = list(product.attributes.all())

    return {
        'option_groups_json': option_groups_json,
        'existing_options_json': existing_options_json,
        'existing_attributes': existing_attributes,  # Passing to the template
    }


def sync_product_attributes(product, raw_json):
    """
    Jason reads the received specifications and stores them as
    separate rows in the `ProductAttribute` table.
    """
    if not raw_json:
        return

    try:
        attributes_data = json.loads(raw_json)
    except (ValueError, TypeError):
        return

    # We ensure that the data is definitely a list
    if not isinstance(attributes_data, list):
        return

    new_attributes = []

    for index, item in enumerate(attributes_data):
        if not isinstance(item, dict):
            continue

        key = item.get('key')
        value = item.get('value')

        if not key or not value:
            continue

        key = str(key).strip()
        value = str(value).strip()

        if not key or not value:
            continue

        display_order = item.get('display_order', index)

        new_attributes.append(
            ProductAttribute(
                product=product,
                key=key,
                value=value,
                display_order=display_order
            )
        )

    with transaction.atomic():
        # Removing previous product specifications for synchronization
        product.attributes.all().delete()

        # Bulk insertion of new rows
        if new_attributes:
            ProductAttribute.objects.bulk_create(new_attributes)
