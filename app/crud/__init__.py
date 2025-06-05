# app/crud/__init__.py

# Importer modeller fra toppen så testsuiten finner dem under crud.models
from app import models

# Re-eksporter alle CRUD-funksjonene under crud.* slik at 
# e.g. crud.get_customer, crud.update_customer osv. eksisterer

from .customers import (
    get_customer,
    get_customers,
    create_customer,
    update_customer,
    delete_customer,
)
from .products import (
    get_product,
    get_products,
    create_product,
    update_product,
    delete_product,
)
from .orders import (
    create_order,
    get_order,
    get_orders,
    update_order_status,
    delete_order,
)
from .crm import (
    create_crm_note,
    get_notes_for_customer,
)
