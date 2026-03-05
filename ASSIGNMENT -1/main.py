from fastapi import FastAPI

app = FastAPI()
#Q-1:Add 3 products-------
products = [
    {"id":1 ,"name":"Wireless Mouse", "price": 599 , "category":"Electronics", "in_stock": True},
    {"id":2 ,"name":"USB Cable", "price": 149 , "category":"Electronics", "in_stock": True},
    {"id":3 ,"name":"Notebook", "price": 89 , "category":"Stationery", "in_stock": True},
    {"id":4 ,"name":"Pen Set", "price": 49 , "category":"Stationery", "in_stock":False},
    {"id":5 ,"name":"Laptop Stand", "price":2499, "category":"Electronics", "in_stock":True},
    {"id":6 ,"name":"Mechanical Keyboard", "price": 3499 ,"category":"Electronics", "in_stock":True},
    {"id":7 ,"name":"Webcam", "price": 1999 , "category":"Electronics", "in_stock":False}

]
    
    
 # ---Endpoint 0 -Home------------
@app.get('/')
def home():
    return{'message': 'Welcome to our E-Commerce Website'}

# --Endpoint 1 - Return all products -----------
@app.get('/products')
def get_all_products():
    return {'products': products,'total' :len(products)}

#--Endpoint :-Return one product by its ID----
#@app.get('/products/{product_id}')
#def get_product(product_id:int):
 #   for product in products:
 #       if product['id']== product_id:
 #           return {'product':product}
 #       return {'error': 'Product not found'}
    

 #Q-2 :Filter products by category
@app.get("/products/category/{category_name}")
def get_by_category(category_name: str):
    result = [p for p in products if p["category"]== category_name]
    if not result:
        return {"error": "No products found in this category"}
    return {"category":category_name, "products":result,"total":len(result)}   

#Q3 - Get only in-stock products
@app.get("/products/instock")
def get_instock():
    available = [p for p in products if p["in_stock"] == True]
    return {"in_stock_products": available, "count": len(available)}

#Q-4 :Get store summary
@app.get('/store/summary')
def store_summary():
    total = len(products)
    instock = len([p for p in products if p["in_stock"]])
    outstock = total - instock

    categories = list(set([p["category"] for p in products]))
    return {
        "store_name": "My E-commerce Store",
        "total_products": total,
        "in_stock": instock,
        "out_of_stock": outstock,
        "categories": categories
    }

#Q-5 :Search product by keyword
@app.get("/products/search/{keyword}")
def search_products(keyword: str):
    results = [
        p for p in products
        if keyword.lower() in p["name"].lower()
    ]
    if not results:
        return {"message": "No products matched your search"}
    return {"keyword" : keyword,"results" : results, "total_matches":len(results)}

#Bonus -Get Cheapest and most expensive products
@app.get("/products/deals")
def get_deals():
    cheapest = min(products, key=lambda p: p["price"])
    expensive = max(products, key=lambda p: p["price"])
    return {
        "best_deal" : cheapest,
        "premium_pick": expensive,
    }