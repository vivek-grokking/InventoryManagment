from fastapi import FastAPI
from redis_om import get_redis_connection, HashModel
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:3000'],  # for frontend
    allow_methods=['*'],
    allow_headers=['*']
)

redis = get_redis_connection(
    host="redis-13385.c55.eu-central-1-1.ec2.cloud.redislabs.com",
    port=13385,
    password="CIczfU98k7e4hAV2vpH6TleoxAnHIZkQ",
    decode_responses=True
)


class Product(HashModel):
    name: str
    price: float
    quantity: int

    class Meta:
        database = redis


@app.get("/products")
def products():
    return [format(pk) for pk in Product.all_pks()]


def format(pk: str):
    product = Product.get(pk)
    return {
        'pk': product.pk,
        'name': product.name,
        'quantity': product.quantity,
        'price': product.price
    }


@app.post("/products")
def create(product: Product):
    return product.save()


@app.get('/products/{pk}')
def get(pk: str):
    return Product.get(pk)


@app.delete('/products/{pk}')
def delete(pk: str):
    return Product.delete(pk)
