# shop/views/init
from .category import (
    category_create,
    category_delete,
    category_list,
    category_update,
)

from .product import (
    ProductDeleteView,
    ProductListView,
    product_create,
    product_update,
)
