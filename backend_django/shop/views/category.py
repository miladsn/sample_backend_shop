# shop/views/category
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render, redirect, get_object_or_404
from django.template.defaultfilters import title
from django.urls import reverse
from django.views.decorators.http import require_POST

from media_files.services import FileManager
from shop.forms import CategoryForm
from shop.models import Category
from shop.views.helpers import  create_module_breadcrumbs


def get_default_breadcrumbs(without_link=False):
    return create_module_breadcrumbs(
        "دسته‌بندی‌ها", "shop:category_list", without_link
    )

@login_required
def category_list(request):
    title="دسته‌بندی‌ها"
    categories = Category.objects.all().order_by("-id")
    breadcrumbs = get_default_breadcrumbs(True)

    return render(
        request,
        "shop/category_list.html",
        {
            "categories": categories,
            "page_title": title,
            "breadcrumbs": breadcrumbs,
        },
    )


@login_required
def category_create(request):
    title = "افزودن دسته‌بندی"
    if request.method == "POST":
        form = CategoryForm(request.POST, request.FILES)

        if form.is_valid():
            category = form.save(commit=False)
            uploaded_image = request.FILES.get('category_image_file')

            if uploaded_image:
                stored_file = FileManager.store(
                    uploaded_file=uploaded_image,
                    path='categories',
                    user=request.user,
                    is_secure=False,
                )
                category.image_id = stored_file.id

            category.save()

            messages.success(
                request,
                "دسته‌بندی با موفقیت ایجاد شد.",
            )

            return redirect("shop:category_list")
    else:
        form = CategoryForm()

    breadcrumbs = get_default_breadcrumbs()
    breadcrumbs.append({"title": title, "url": None})


    return render(
        request,
        "shop/category_form.html",
        {
            "form": form,
            "title": title,
            "is_edit": False,
            "breadcrumbs": breadcrumbs,
        },
    )


@login_required
def category_update(request, pk):
    title = "ویرایش دسته‌بندی"
    category = get_object_or_404(Category, pk=pk)

    if request.method == "POST":
        form = CategoryForm(
            request.POST,
            request.FILES,
            instance=category,
        )

        if form.is_valid():
            category = form.save(commit=False)
            uploaded_image = request.FILES.get('category_image_file')

            if uploaded_image:
                stored_file = FileManager.store(
                    uploaded_file=uploaded_image,
                    path='categories',
                    user=request.user,
                    is_secure=False,
                )
                category.image_id = stored_file.id

            category.save()

            messages.success(
                request,
                "دسته‌بندی با موفقیت ویرایش شد.",
            )

            return redirect("shop:category_list")
    else:
        form = CategoryForm(instance=category)



    breadcrumbs = get_default_breadcrumbs()
    breadcrumbs.append({"title": f"ویرایش ({category.name})", "url": None})

    return render(
        request,
        "shop/category_form.html",
        {
            "form": form,
            "category": category,
            "title": title,
            "is_edit": True,
            "breadcrumbs": breadcrumbs,
        },
    )


@login_required
@require_POST
@permission_required('shop.delete_category', raise_exception=True)
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)

    if request.method == "POST":
        if category.children.exists():
            messages.error(request, "این دسته‌بندی دارای زیرمجموعه است و ابتدا باید زیردسته‌های آن حذف یا منتقل شوند.")
            return redirect("shop:category_list")

        category.delete()

        messages.success(
            request,
            "دسته‌بندی با موفقیت حذف شد.",
        )

    return redirect("shop:category_list")
