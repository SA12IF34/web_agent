from deepgram.types import ThinkSettingsV1FunctionsItem
from .logic import (
    search_products as handle_search_products,
    get_product as handle_get_product,
    search_order as handle_search_order,
    search_account as handle_search_account,
    # update_order as handle_update_order,
    cancel_order as handle_cancel_order,
    update_account as handle_update_account,
    # reset_password as handle_reset_password,
    delete_account as handle_delete_account,
    create_payment as handle_create_payment,
    refund_payment as handle_refund_payment,
    create_complain as handle_create_complain,
    create_request as handle_create_request,
)

from tavily import TavilyClient
import os 
import json

async def search_products(params):
    try:
        terms = params.get('terms')
        if not terms:
            return 'You must provide the search terms'
        
        result = await handle_search_products(terms)
        
        return result
    
    except Exception as exc:
        print('Error at search_product ', str(exc))
        return 'Could not search for products'

async def get_product(params):
    try:
        product_id = params.get('product_id')
        product_name = params.get('product_name')
        if not product_id and not product_name:
            return 'You must provide the product id at least'
        
        result = await handle_get_product(product_id, product_name)

        return result
    
    except Exception as exc:
        print('Error at get_product ', str(exc))
        return 'Could not get product'

async def search_order(params):
    try:
        order_id = params.get('order_id')
        account_id = params.get('account_id')

        if not order_id and not account_id:
            return "You must provide either the order id or order's account id"
        
        result = await handle_search_order(order_id, account_id)

        return result
    
    except Exception as exc:
        print('Error at search_order ', str(exc))
        return 'Could not search for orders'

async def search_account(params):
    try:
        account_id = params.get('account_id')
        email = params.get('email')
        phone = params.get('phone')

        if not account_id and not email and not phone:
            return 'You must provide account id or email or phone number at least'
        
        result = await handle_search_account(account_id, email, phone)

        return result

    except Exception as exc:
        print('Error at search_account ', str(exc))
        return 'Could not search for accounts'

# async def update_order(params):
#     try:
#         order_id = params.get('order_id')
#     except Exception as exc:
#         print('Error at update_order ', str(exc))
#         return 'Could not update order'

async def cancel_order(params):
    try:
        order_id = params.get('order_id')
        if not order_id:
            return 'You must provide order id'
        
        result = await handle_cancel_order(order_id)

        return result

    except Exception as exc:
        print('Error at cancel_order ', str(exc))
        return 'Could not cancel order'

async def update_account(params):
    try:
        account_id = params.get('account_id')
        if not account_id:
            return 'You must provide account id'
        
        email = params.get('email')
        phone = params.get('phone')
        password = params.get('password')

        if not email and not phone and not password:
            return 'You must provide the value to be updated'
        
        result = await handle_update_account(account_id, email, phone, password)

        return result
    
    except Exception as exc:
        print('Error at update_account ', str(exc))
        return 'Could not update account'

# async def reset_password(params):
#     try:
#         account_id = params.get('account_id')
#         email = params.get('email')
#         if not account_id and not email:
#             return 'You must provide either account id or email'
        
#         new_password = params.get('new_password')
#         if not new_password:
#             return 'You must provide the new password'
        
#         result = await handle_reset_password(account_id, email, new_password)

#         return result

#     except Exception as exc:
#         print('Error at reset_password ', str(exc))
#         return 'Could not reset password'

async def delete_account(params):
    try:
        account_id = params.get('account_id')

        if not account_id:
            return 'You must provide account id'
        
        result = await handle_delete_account(account_id)

        return result

    except Exception as exc:
        print('Error at delete_account ', str(exc))
        return 'Could not delete account'

async def create_payment(params):
    try:
        order_id = params.get('order_id')
        if not order_id:
            return 'You must provide order id'

        result = await handle_create_payment(order_id)

        return result
    
    except Exception as exc:
        print('Error at create_payment ', str(exc))
        return 'Could not create payment'

async def refund_payment(params):
    try:
        payment_id = params.get('payment_id')
        order_id = params.get('order_id')

        if not payment_id and not order_id:
            return 'You must provide either payment or order id'

        result = await handle_refund_payment(payment_id, order_id)

        return result
    
    except Exception as exc:
        print('Error at refund_payment ', str(exc))
        return 'Could not refund payment'

async def get_product_technical_details(params):
    try:
        product_name = params.get('product')
        if not product_name:
            return 'You must provide product name'
        
        client = TavilyClient(os.getenv('TAVILY_API_KEY'))
        response = client.search(f'Specifications of {product_name}', search_depth='advanced', include_answer='basic')

        return response['answer'] if response.get('answer') else json.dumps(response['results'])

    except Exception as exc:
        print('Error at get_product_technical_details ', str(exc))
        return 'Could not get product technical details'

async def create_complain(params):
    try:
        account_id = params.get('account_id')
        description = params.get('description')

        if account_id and description:
            result = await handle_create_complain(account_id, description)

            return result
        
        return 'You must provide account id and complain description'

    except Exception as exc:
        print('Error at create_complain ', str(exc))
        return 'Could not create complaint'

async def create_request(params):
    try:
        account_id = params.get('account_id')
        description = params.get('description')

        if account_id and description:
            result = await handle_create_request(account_id, description)

            return result
        
        return 'You must provide account id and request description'

    except Exception as exc:
        print('Error at create_request ', str(exc))
        return 'Could not create request'


FUNCTIONS = [
    ThinkSettingsV1FunctionsItem(
        name="search_products",
        description="""Search products by term(s).
        Use this function to findout if a product exists.
        When to call this function:
        - When the user asks if you have a specific product or asks about some products
        - Any case where you need to search products
        
        How to use this function:
        - you specify one term or more based on your need as a parameter and call it with those terms
        - if you specify more than one term, separate the terms by commas (e.g. "term one,term two,term three)""",
        parameters={
            "type": "object",
            "properties": {
                "terms": {
                    "type": "string",
                    "description": "The terms which will be used to search products. Can be one term or comma separated terms."
                }
            },
            "required": ["terms"]
        }
    ),
    ThinkSettingsV1FunctionsItem(
        name="get_product",
        description="""Retrieve products detail via product ID.
        When to call this:
        - When you need to know the details of specific product and you know the exact ID the product
        - The user asks you about specifi product and provided the exact product ID
        
        How to use this function:
        - You call it with either the exact product ID
        - A product ID is a six digit code prefixed with "PROD-" 
        - Make sure to include the "PROD-" prefix when provide product ID""",
        parameters={
            "type": "object",
            "properties": {
                "product_id": {
                    "type": "string",
                    "description": """A six digit code prefixed with 'PROD-' (e.g. "PROD-332451")"""
                }
            },
            "required": ["product_id"]
        }
    ),
    ThinkSettingsV1FunctionsItem(
        name="search_order",
        description="""Search order using order ID or account ID.
        When to call this function:
        - You need to know the details of specific order
        - The user asks you about their order
        
        How to use this function:
        - You specify either user's account ID or order ID
        - Account ID is a six digit prefixed with "ACC-" like this "ACC-XXXXXX"
        - Order ID is a six digit prefixed with "ORD-" like this "ORD-" 
        
        Make sure to include the prefixes even if the user did not provide them.""",
        parameters={
            "type": "object",
            "properties": {
                "order_id": {
                    "type": "string",
                    "description": """A six digit id with "ORD-" prefix (e.g. "ORD-652345") """
                },
                "account_id": {
                    "type": "string",
                    "description": """A six digit id with "ACC-" prefix (e.g. "ACC-234321")"""
                }
            }
        }
    ),
    ThinkSettingsV1FunctionsItem(
        name="search_account",
        description="""Search for account via account ID, email or phone number.
        When to call this function:
        - You need to check that the user have an account
        - The user asks you about their account
        
        How to use this function:
        - You use either user's account ID ("ACC-XXXXXX"), email, or phone number to lookup user's account""",
        parameters={
            "type": "object",
            "properties": {
                "account_id": {
                    "type": "string",
                    "description": """A six digit id with "ACC-" prefix (e.g. "ACC-234321"). Make sure to include the "ACC-" prefix"""
                },
                "email": {
                    "type": "string",
                    "description": """User account email. Make sure it is a valid email."""
                },
                "phone": {
                    "type": "string",
                    "description": """User account phone number. Make sure to include country code with '+'"""
                }
            }
        }
    ),
    ThinkSettingsV1FunctionsItem(
        name="cancel_order",
        description="""Cancel and delete order.
        When to call this function:
        - The user requests cancelling the order
        
        How to use this function:
        - You provide the order ID (ORD-XXXXXX) to lookup and cancel the order""",
        parameters={
            "type": "object",
            "properties": {
                "order_id": {
                    "type": "string",
                    "description": """order ID, a six digit prefixed with "ORD-", make sure to include ORD- prefix when calling this function."""
                }
            }
        }
    ),
    ThinkSettingsV1FunctionsItem(
        name="update_account",
        description="""Update account details like email or phone number.
        When to call this function:
        - The user asks to update the email or phone number of their account
        
        How use this function:
        - The user asks you to update their account with the new data
        - You ask them for their account id or current email of phone number
        - You retreive their account details with search_account function
        - You ask them for the new data like email or phone number and double check with the user
        - You call update_account with the account ID and the new data""",
        parameters={
            "type": "object",
            "properties": {
                "account_id": {
                    "type": "string",
                    "description": "Account ID to lookup the account to be updated. A six digit prefixed with ACC-"
                },
                "email": {
                    "type": "string",
                    "description": "User new email."
                },
                "phone": {
                    "type": "string",
                    "description": "User new phone number. Make sure the country code prefixed with '+' is included"
                }
            }
        }
    ),
    ThinkSettingsV1FunctionsItem(
        name="delete_account",
        description="""Delete a user account permanently.
        When to call this function:
        - The user asks to close, remove, or delete their account
        
        How to use this function:
        - You provide the account ID (ACC-XXXXXX) to identify the exact account to delete
        - Make sure the user really wants to delete the account before proceeding""",
        parameters={
            "type": "object",
            "properties": {
                "account_id": {
                    "type": "string",
                    "description": "The account ID to delete. Use the ACC- prefix format."
                }
            },
            "required": ["account_id"]
        }
    ),
    ThinkSettingsV1FunctionsItem(
        name="create_payment",
        description="""Create a payment for an existing order.
        When to call this function:
        - There is an order the user could not checkout

        How to use this function:
        - You provide the order ID (ORD-XXXXXX) so the payment is attached to the correct order
        - Use this only after confirming the intended order""",
        parameters={
            "type": "object",
            "properties": {
                "order_id": {
                    "type": "string",
                    "description": "The order ID for the payment. Use the ORD- prefix format."
                }
            },
            "required": ["order_id"]
        }
    ),
    ThinkSettingsV1FunctionsItem(
        name="refund_payment",
        description="""Refund a payment for an order or payment ID.
        When to call this function:
        - A paid order is cancelled so the user should receive a refund of their payment
        
        How to use this function:
        - You provide either the payment ID or the order ID to locate the payment
        - Use the most specific identifier available to avoid refunding the wrong transaction""",
        parameters={
            "type": "object",
            "properties": {
                "payment_id": {
                    "type": "string",
                    "description": "The payment ID to refund if it is known. A six digit ID prefixed with 'P-'"
                },
                "order_id": {
                    "type": "string",
                    "description": "The order ID to find and refund the linked payment."
                }
            }
        }
    ),
    ThinkSettingsV1FunctionsItem(
        name="get_product_technical_details",
        description="""Retrieve technical details for a product.
        When to call this function:
        - The user asks for specifications, features, or technical information about a product
        
        How to use this function:
        - You provide the product name so the system can gather the relevant details
        - Use this when the user needs deeper product information beyond basic description""",
        parameters={
            "type": "object",
            "properties": {
                "product": {
                    "type": "string",
                    "description": "The product name to look up technical details for."
                }
            },
            "required": ["product"]
        }
    ),
    ThinkSettingsV1FunctionsItem(
        name="create_complain",
        description="""Create a complaint for a customer account.
        When to call this function:
        - The user wants to report an issue or make a complaint about a service or product
        
        How to use this function:
        - You check first if the user has an account
        - You provide the account ID (ACC-XXXXXX) and a clear description of the problem
        - Make sure the complaint details are specific enough for support to act on""",
        parameters={
            "type": "object",
            "properties": {
                "account_id": {
                    "type": "string",
                    "description": "The account ID for the complaint. Use the ACC- prefix format."
                },
                "description": {
                    "type": "string",
                    "description": "A clear description of the complaint or issue."
                }
            },
            "required": ["account_id", "description"]
        }
    ),
    ThinkSettingsV1FunctionsItem(
        name="create_request",
        description="""Create a support request for a customer account.
        When to call this function:
        - The user wants to ask for help or submit a support request
        
        How to use this function:
        - You provide the account ID (ACC-XXXXXX) and a concise description of the request
        - Use this for non-urgent help requests that need follow-up from support""",
        parameters={
            "type": "object",
            "properties": {
                "account_id": {
                    "type": "string",
                    "description": "The account ID for the request. Use the ACC- prefix format."
                },
                "description": {
                    "type": "string",
                    "description": "A brief description of the support request."
                }
            },
            "required": ["account_id", "description"]
        }
    ),
    ThinkSettingsV1FunctionsItem(
        name='end_call',
        description="""End current conversation gracefully and in friendly way.
        When to call this function:
        - The user expressed they want to end (e.g. "Thank you for today", "This was fun", "I have to go", "bye")
        
        How to use this function:
        - When you decide to end the conversation, specify the farewell phrase and call this function with it
        - The farewell phrase will be sent to the user and the conversation will end gracefully
        
        You must call this function when you end the conversation, do not farewell the user, but call this function instead.""",
        parameters={
            "type": "object",
            "properties": {
                "farewell": {
                    "type": "string",
                    "description": """The farewell phrase to be used before ending the call. must be simple and straightforward."""
                }
            },
            "required": ["farewell"]
        }
    )
]

FUNCTIONS_MAP = {
    "search_products": search_products,
    "get_product": get_product,
    "search_order": search_order,
    "search_account": search_account,
    "cancel_order": cancel_order,
    "update_account": update_account,
    "delete_account": delete_account,
    "create_payment": create_payment,
    "refund_payment": refund_payment,
    "get_product_technical_details": get_product_technical_details,
    "create_complain": create_complain,
    "create_request": create_request,
}