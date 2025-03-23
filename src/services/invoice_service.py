
from uuid import UUID

from fastapi import HTTPException
from src.models.invoice import InvoiceResponse
from src.models.invoice import MultipleInvoiceResponse
from src.models.model_mappers import map_db_to_invoice_response
from src.db.invoice_manager_db import get_joined_invoice_customer_by_id
from src.db.invoice_manager_db import post_invoice_request
from src.db.invoice_manager_db import get_joined_invoice_customer
from src.db.invoice_manager_db import update_invoice_to_paid
from src.services.fake_pay_service import FakePay
from src.models.enums import Status
from src.models.card import Card
from src.models.invoice import InvoiceRequest

class InvoicingService():
    def __init__(self, settings):
        self.fake_pay = FakePay(settings)
        
    #Get invoice    
    async def get_invoice(self, invoice_id: UUID):
        # Returns InvoiceDB, Customer DB objects joined
        invoice_customer = get_joined_invoice_customer_by_id(invoice_id=str(invoice_id))
        if invoice_customer is None:
            raise HTTPException(status_code=404, detail="No record found with this UUID")
        
        # Map to pydantic model
        invoice_response: InvoiceResponse = map_db_to_invoice_response(invoice_customer[0], invoice_customer[1])
        return 200, invoice_response.model_dump(exclude_none=True, by_alias=True)
    
    #Post Invoice
    async def post_invoice(self, invoice_request: InvoiceRequest, card: Card):
        # Returns InvoiceDB, Customer DB objects joined
        invoice_customer = post_invoice_request(invoice_request)
        if invoice_customer is None:
            raise HTTPException(status_code=404, detail="No record found with this UUID")
        
        invoice_response: InvoiceResponse = map_db_to_invoice_response(invoice_customer[0], invoice_customer[1])
        if card is None:
            return 200, invoice_response.model_dump(exclude_none=True, by_alias=True)
        else:
            return self.fake_pay.pay_invoice(invoice_response.id, card)
    
    #Get all
    async def get_invoices(self, status: Status):
        # Returns InvoiceDB, Customer DB objects joined
        invoice_customer = get_joined_invoice_customer(status)
        if invoice_customer is None:
            raise HTTPException(status_code=404, detail="No records found")
        
        # Map to pydantic model
        invoiceList = InvoiceResponse[0]
        for invoice in invoice_customer:
            invoiceList.append(map_db_to_invoice_response(invoice[0], invoice[1]).model_dump(exclude_none=True, by_alias=True))
        return 200, invoiceList
    
    async def pay_invoice(self, invoice_id:UUID, card:Card):
        #check database
        invoice_customer = get_joined_invoice_customer_by_id(invoice_id=str(invoice_id))
        if invoice_customer is None:
            raise HTTPException(status_code=404, detail="No record found with this UUID")
        #fake pay
        response = self.fake_pay.pay_invoice(invoice_id, card)
        if response.status_code != 200:
            raise HTTPException(status_code=504, detail="problem paying invoice")
        #update database
        invoice_customer = update_invoice_to_paid(invoice_id=str(invoice_id))
        if invoice_customer is None:
            raise HTTPException(status_code=404, detail="Problem updating invoice")
        #return updated invoice
        #mask card number
        card.number = len(card.number[:-4])*"*"+card.number[-4:]
        invoice_response: InvoiceResponse = map_db_to_invoice_response(invoice_customer[0], invoice_customer[1])
        invoice_response.card = card
        return 200, invoice_response.model_dump(exclude_none=True, by_alias=True)