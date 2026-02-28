from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

app = FastAPI()

class ProductCreate(BaseModel):
    name: str
    price: float

class Product(ProductCreate):
    id: int

products: List[Product] = []
current_id = 1

@app.get("/products", response_model=List[Product])
def get_products():
    return products


@app.post("/products", response_model=Product, status_code=201)
def create_product(product: ProductCreate):
    global current_id

    new_product = Product(
        id=current_id,
        name=product.name,
        price=product.price
    )

    products.append(new_product)
    current_id += 1

    return new_product


@app.get("/products/{id}", response_model=Product)
def get_product(id: int):
    for product in products:
        if product.id == id:
            return product

    raise HTTPException(status_code=404, detail="Product not found")