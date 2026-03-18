from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel

app = FastAPI()


# PRODUCTS DATABASE


products = [
    {"id": 1, "name": "Wireless Mouse", "price": 499, "category": "Electronics", "in_stock": True},
    {"id": 2, "name": "Notebook", "price": 99, "category": "Stationery", "in_stock": True},
    {"id": 3, "name": "USB Hub", "price": 799, "category": "Electronics", "in_stock": False},
    {"id": 4, "name": "Pen Set", "price": 49, "category": "Stationery", "in_stock": True}
]


orders = []

# ORDER MODEL

class Order(BaseModel):
    customer_name: str
    product_id: int
    quantity: int


# PLACE ORDER 


@app.post("/orders")
def place_order(data: Order):

    product = next((p for p in products if p["id"] == data.product_id), None)

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if not product["in_stock"]:
        raise HTTPException(status_code=400, detail="Product out of stock")

    total_price = product["price"] * data.quantity

    order = {
        "order_id": len(orders) + 1,
        "customer_name": data.customer_name,
        "product": product["name"],
        "quantity": data.quantity,
        "total_price": total_price
    }

    orders.append(order)

    return {
        "message": "Order placed successfully",
        "order": order
    }


# VIEW PRODUCTS


@app.get("/products")
def get_products():
    return {"products": products}


# Q1 — SEARCH PRODUCTS


@app.get("/products/search")
def search_products(keyword: str = Query(...)):

    results = [
        p for p in products
        if keyword.lower() in p["name"].lower()
    ]

    if not results:
        return {"message": f"No products found for: {keyword}"}

    return {
        "keyword": keyword,
        "total_found": len(results),
        "products": results
    }


# Q2 — SORT PRODUCTS


@app.get("/products/sort")
def sort_products(
    sort_by: str = Query("price"),
    order: str = Query("asc")
):

    if sort_by not in ["price", "name"]:
        raise HTTPException(
            status_code=400,
            detail="sort_by must be 'price' or 'name'"
        )

    reverse = (order == "desc")

    sorted_products = sorted(
        products,
        key=lambda p: p[sort_by],
        reverse=reverse
    )

    return {
        "sort_by": sort_by,
        "order": order,
        "products": sorted_products
    }


# Q3 — PAGINATION


@app.get("/products/page")
def paginate_products(
    page: int = Query(1, ge=1),
    limit: int = Query(2, ge=1)
):

    start = (page - 1) * limit

    return {
        "page": page,
        "limit": limit,
        "total_products": len(products),
        "total_pages": -(-len(products) // limit),
        "products": products[start:start + limit]
    }


# Q4 — SEARCH ORDERS


@app.get("/orders/search")
def search_orders(customer_name: str = Query(...)):

    results = [
        o for o in orders
        if customer_name.lower() in o["customer_name"].lower()
    ]

    if not results:
        return {"message": f"No orders found for: {customer_name}"}

    return {
        "customer_name": customer_name,
        "total_found": len(results),
        "orders": results
    }


# Q5 — SORT BY CATEGORY AND PRICE


@app.get("/products/sort-by-category")
def sort_by_category():

    result = sorted(
        products,
        key=lambda p: (p["category"], p["price"])
    )

    return {
        "products": result,
        "total": len(result)
    }


# Q6 —  BROWSE


@app.get("/products/browse")
def browse_products(
    keyword: str = Query(None),
    sort_by: str = Query("price"),
    order: str = Query("asc"),
    page: int = Query(1, ge=1),
    limit: int = Query(4, ge=1, le=20)
):

    # SEARCH
    result = products
    if keyword:
        result = [
            p for p in result
            if keyword.lower() in p["name"].lower()
        ]

    # SORT
    if sort_by not in ["price", "name"]:
        raise HTTPException(
            status_code=400,
            detail="sort_by must be 'price' or 'name'"
        )

    result = sorted(
        result,
        key=lambda p: p[sort_by],
        reverse=(order == "desc")
    )

    # PAGINATION
    total = len(result)
    start = (page - 1) * limit
    paged = result[start:start + limit]

    return {
        "keyword": keyword,
        "sort_by": sort_by,
        "order": order,
        "page": page,
        "limit": limit,
        "total_found": total,
        "total_pages": -(-total // limit),
        "products": paged
    }


# BONUS — PAGINATE ORDERS


@app.get("/orders/page")
def get_orders_paged(
    page: int = Query(1, ge=1),
    limit: int = Query(3, ge=1, le=20)
):

    start = (page - 1) * limit

    return {
        "page": page,
        "limit": limit,
        "total_orders": len(orders),
        "total_pages": -(-len(orders) // limit),
        "orders": orders[start:start + limit]
    }


# GET PRODUCT BY ID


@app.get("/products/{product_id}")
def get_product(product_id: int):

    product = next((p for p in products if p["id"] == product_id), None)

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    return product
