from django.db.models import Count, Prefetch, Q

from shop.models import Category


def get_storefront_categories():
    active_grandchildren = Category.objects.filter(
        is_active=True,
    ).order_by("name")

    active_children = (
        Category.objects
        .filter(is_active=True)
        .annotate(
            active_children_count=Count(
                "children",
                filter=Q(children__is_active=True),
            )
        )
        .prefetch_related(
            Prefetch("children", queryset=active_grandchildren)
        )
        .order_by("name")
    )

    return (
        Category.objects
        .filter(is_active=True, parent__isnull=True)
        .select_related("image")
        .annotate(
            active_children_count=Count(
                "children",
                filter=Q(children__is_active=True),
            )
        )
        .prefetch_related(
            Prefetch("children", queryset=active_children)
        )
        .order_by("name")
    )
