import aiohttp
from uuid import UUID

class FakePay:
    def __init__(self, settings):
        self.client_session = aiohttp.ClientSession()
        self.fakepay_url = settings.fakepay_url

# FAKE PAY callout here
        #async def pay_invoice(self, invoice_id: UUID, card: Card):
            #create request
            #send to server