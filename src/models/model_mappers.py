from src.models.invoice import InvoiceResponse
from src.db.invoice_db_model import CustomerDB, InvoiceDB
from src.models.card import Card


def map_db_to_invoice_response(invoice: InvoiceDB, customer: CustomerDB, card: Card):
    customer_dict = customer.to_dict()
    # Need to remove id to avoid duplicate kwarg population
    customer_dict.pop("customer_id")
    response = InvoiceResponse(
        # Dump feilds as kwargs
        **customer_dict,
        **invoice.to_dict(),
        **card.to_dict(),
    )
    return response
