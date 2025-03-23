from functools import wraps
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError
from sqlalchemy import exists, select, insert, update
from src.db.invoice_db_model import InvoiceDB, CustomerDB
from src.config.settings import Settings
from src.models.enums import Status
from src.models.invoice import InvoiceRequest

settings = Settings()

url = f'mysql+mysqlconnector://{settings.db_user}:{settings.db_password}@{settings.db_url}'  
engine = create_engine(url, echo=True)

# Create a sessionmaker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Decorator to automatically manage the database session
def with_db_session(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Create session
        db = SessionLocal()
        try:
            return func(*args, db=db, **kwargs)
        finally:
            db.close()
    return wrapper


@with_db_session
def db_health_check(db=None):
    print(f">>>{url}")
    try:
        statement = exists(select(1)).select()
        check  = db.execute(statement).scalar()
        return (200, {"status": "UP"}) if check else (502, {"status": "DOWN"})
    except OperationalError as error:
        # If there is a connection issue or any other operational error, catch it and return an error message
        print(f"DATABASE DOWN ERROR: {error}")
        return (502, {"status": "DOWN"})


@with_db_session 
def get_joined_invoice_customer_by_id(invoice_id: str, db=None):
    """
    Fetch full invoice details by ID, including all invoice and customer fields.
    """
    invoice_customer = db.query(InvoiceDB, CustomerDB).join(
        CustomerDB, CustomerDB.customer_id == InvoiceDB.customer_id
    ).filter(InvoiceDB.id == invoice_id).first() 
    
    return invoice_customer

@with_db_session 
def post_invoice_request(invoice_request: InvoiceRequest, db=None):
    """
    Fetch full invoice details by ID, including all invoice and customer fields.
    """
    statement = insert(InvoiceDB).values(customer_id = invoice_request.customer_id, job_description = invoice_request.job_description, amount = invoice_request.amount)
    result = db.execute(statement)
    invoice = db.query(InvoiceDB, CustomerDB).join(
        CustomerDB, CustomerDB.customer_id == InvoiceDB.customer_id
    ).filter(InvoiceDB.id == result.inserted_primary_key[0]).first() 
    return invoice
    
@with_db_session 
def get_joined_invoice_customer(status: Status, db=None):
    """
    Fetch full invoice details by ID, including all invoice and customer fields.
    """
    if(status):
        invoice_customer = db.query(InvoiceDB, CustomerDB).join(
            CustomerDB, CustomerDB.customer_id == InvoiceDB.customer_id
        ).filter(InvoiceDB.invoice_status == str(status))
    else:
        invoice_customer = db.query(InvoiceDB, CustomerDB).join(
            CustomerDB, CustomerDB.customer_id == InvoiceDB.customer_id
        )
    return invoice_customer

@with_db_session 
def update_invoice_to_paid(invoice_id: str, db=None):
    """
    Fetch full invoice details by ID, including all invoice and customer fields.
    """
    statement = update(InvoiceDB).values(invoice_status = "PAID").where(id = invoice_id)
    db.execute(statement)
    invoice = db.query(InvoiceDB, CustomerDB).join(
        CustomerDB, CustomerDB.customer_id == InvoiceDB.customer_id
    ).filter(InvoiceDB.id == invoice_id).first() 
    return invoice
