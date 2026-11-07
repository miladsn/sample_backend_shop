from shop.models import Category


def category_tree_ids(slugs):
    category_ids = set(Category.objects.filter(slug__in=slugs, is_active=True).values_list('id', flat=True))
    parent_ids = category_ids.copy()
    while parent_ids:
        child_ids = set(Category.objects.filter(
            parent_id__in=parent_ids, is_active=True,
        ).exclude(pk__in=category_ids).values_list('id', flat=True))
        category_ids.update(child_ids)
        parent_ids = child_ids
    return category_ids
