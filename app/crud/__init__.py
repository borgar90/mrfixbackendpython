# app/crud/__init__.py

# Importer modeller fra toppen så testsuiten finner dem under crud.models
from app import models

# Re-eksporter alle CRUD-funksjonene under crud.* slik at 
# e.g. crud.get_customer, crud.update_customer osv. eksisterer

from .crm import (
    create_crm_note,
    get_notes_for_customer,
)
from .orders import (
    create_order,
    get_order,
    get_orders,
    update_order_status,
    delete_order,
)
from .products import (
    get_product,
    get_products,
    create_product,
    update_product,
    delete_product,
    adjust_product_stock,
    get_product_image,
    get_product_images,
    create_product_image,
    update_product_image,
    delete_product_image,
)
from .customers import (
    get_customer,
    get_customers,
    create_customer,
    update_customer,
    delete_customer,
    get_customer_with_orders,
)
from .users import (
    get_user_by_email,
    create_user,
    get_users,
    update_user,
    delete_user,
    get_user  # expose get_user by id
)
