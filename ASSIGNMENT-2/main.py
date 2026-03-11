from fastapi import FastAPI, Query
from pydantic import BaseModel, Field
from typing import Optional, List

app = FastAPI()

class OrderRequest(BaseModel):
    customer_name: str = Field(..., min_length=2, max_length=100)
    product_id: int = Field(..., gt=0)
    quantity: int = Field(..., gt=0, le=100)
    delivery_address: str = Field(..., min_length=10)

products = [
    {'id':1,'name':'Wireless Mouse','price':499,'category':'Electronics','in_stock':True},
    {'id':2,'name':'Notebook','price':99,'category':'Stationery','in_stock':True},
    {'id':3,'name':'USB Hub','price':799,'category':'Electronics','in_stock':False},
    {'id':4,'name':'Pen Set','price':49,'category':'Stationery','in_stock':True},
]

orders = []
order_counter = 1
feedback=[]


def find_product(product_id:int):
    for p in products:
        if p['id'] == product_id:
            return p
    return None


def calculate_total(product, quantity):
    return product['price'] * quantity


def filter_products_logic(category=None, min_price=None, max_price=None, in_stock=None):
    result = products
    if category:
        result = [p for p in result if p['category'] == category]
    if min_price:
        result = [p for p in result if p['price'] >= min_price]
    if max_price:
        result = [p for p in result if p['price'] <= max_price]
    if in_stock is not None:
        result = [p for p in result if p['in_stock'] == in_stock]
    return result


@app.get("/")
def home():
    return {"message":"Welcome to our E-commerce API"}


@app.get("/products")
def get_products():
    return {"products":products}


@app.get("/products/filter")
def filter_products(category:str=None, min_price:int=None, max_price:int=None, in_stock:bool=None):
    result = filter_products_logic(category,min_price,max_price,in_stock)
    return {"filtered_products":result}


@app.get("/products/compare")
def compare_products(product_id_1:int, product_id_2:int):
    p1 = find_product(product_id_1)
    p2 = find_product(product_id_2)

    if not p1:
        return {"error":"Product 1 not found"}
    if not p2:
        return {"error":"Product 2 not found"}

    cheaper = p1 if p1['price'] < p2['price'] else p2

    return {
        "product_1":p1,
        "product_2":p2,
        "better_value":cheaper['name']
    }

#Q-4 : - Product Summary

@app.get("/products/summary")
def product_summary():
    # 1. Safety check for empty data
    if not products:
        return {
            "total_products": 0,
            "in_stock_count": 0,
            "out_of_stock_count": 0,
            "most_expensive": None,
            "cheapest": None,
            "categories": []
        }

    # 2. Count Stock (One pass for efficiency)
    in_stock_list = [p for p in products if p.get("in_stock")]
    in_stock_count = len(in_stock_list)
    out_of_stock_count = len(products) - in_stock_count

    # 3. Find Extremes (Most Expensive & Cheapest)
    expensive = max(products, key=lambda p: p["price"])
    cheapest = min(products, key=lambda p: p["price"])

    # 4. Get Unique Categories
    categories = list(set(p["category"] for p in products))

    # 5. Return precise structure requested
    return {
        "total_products": len(products),
        "in_stock_count": in_stock_count,
        "out_of_stock_count": out_of_stock_count,
        "most_expensive": {
            "name": expensive["name"],
            "price": expensive["price"]
        },
        "cheapest": {
            "name": cheapest["name"],
            "price": cheapest["price"]
        },
        "categories": categories
    }

@app.get("/products/{product_id}")
def get_product(product_id:int):
    product = find_product(product_id)
    if not product:
        return {"error":"Product not found"}
    return {"product":product}


@app.post("/orders")
def place_order(order_data:OrderRequest):
    global order_counter

    product = find_product(order_data.product_id)

    if not product:
        return {"error":"Product not found"}

    if not product['in_stock']:
        return {"error":"Product out of stock"}

    total = calculate_total(product,order_data.quantity)

    order = {
        "order_id":order_counter,
        "customer_name":order_data.customer_name,
        "product":product['name'],
        "quantity":order_data.quantity,
        "delivery_address":order_data.delivery_address,
        "total_price":total,
        "status": "pendong"
    }

    orders.append(order)
    order_counter += 1

    return {"message":"Order placed","order":order}


@app.get("/orders")
def get_orders():
    return {"orders":orders}

#............ASSIGNMENT-2 ..........
#Q:1 Filter Products
@app.get("/products/filter")
def filter_products(
    category: str = None,
    max_price: int = None,
    min_price : int = Query(None,description = "Minimum price")
):
    
    result = products
    if category:
        result = [p for p in result if p["category"]==category]

    if max_price:
        result = [p for p in result if p["price"] <=max_price]

    if min_price:
        result = [p for p in result if p["price"] >= min_price]   

    return result     

#Q-2 Product price

@app.get("/products/{product_id}/price")
def get_product_price(product_id: int):
    for product in products :
        if product["id"] == product_id:
            return {
                "name": product["name"],
                "price" : product["price"]
            }
    return{"error": "Product not found"}

#Q-3
class CustomerFeedback(BaseModel):
    customer_name: str = Field(..., min_length=2)
    product_id: int = Field(..., gt=0)
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = Field(None, max_length=300)


feedback_list =[]

@app.post("/feedback")
def submit_feedback(data: CustomerFeedback):

    feedback_list.append(data,dict())

    return {
    "message": "Feedback submitted successfully", 
    "feedback": data.dict(), 
    "total_feedback": len(feedback_list)  
}
    
#Q-5 Bulk order

class OrderItem(BaseModel):
    product_id: int = Field(..., gt=0)
    quantity: int = Field(..., gt=0, le=50)

# 🛡️ Model for the bulk order
class BulkOrder(BaseModel):
    company_name: str = Field(..., min_length=2)
    contact_email: str = Field(..., min_length=5)
    items: List[OrderItem] = Field(..., min_items=1) # Ensure at least 1 item

@app.post("/orders/bulk")
def place_bulk_order(order: BulkOrder):
    global order_counter
    confirmed = []
    failed = []
    grand_total = 0

    
    for item in order.items:
        product = next((p for p in products if p["id"] == item.product_id), None)
        if not product:
            failed.append({
                "product_id": item.product_id, 
                "reason": "Product not found"
            })
        elif not product["in_stock"]:
            # ⚠️ Handle out of stock while continuing the loop
            failed.append({
                "product_id": item.product_id, 
                "reason": f"{product['name']} is out of stock"
            })
        else:
            # Calculate total for valid items
            subtotal = product["price"] * item.quantity
            grand_total += subtotal
            confirmed.append({
                "product": product["name"],
                "qty": item.quantity,
                "subtotal": subtotal
            })


    new_bulk_order = {
        "order_id": order_counter,
        "company": order.company_name,
        "confirmed": confirmed,
        "failed": failed,
        "grand_total": grand_total,
        "status": "pending" # Important for your PATCH endpoint!
    }
    orders.append(new_bulk_order) # This makes count go up!
    order_counter += 1
    return new_bulk_order


#BONUS 
@app.patch("/orders/{order_id}/confirm")
def confirm_order(order_id: int):
    for order in orders:
        if order.get("order_id") == order_id:
            order["status"] = "confirmed"
            return {
                "message": f"Order {order_id} confirmed", "order": order
            }
    return {"error": "Order not found"}
