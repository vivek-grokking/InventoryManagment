from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.background import BackgroundTasks
from redis_om import get_redis_connection, HashModel
from starlette.requests import Request
import requests
import time

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:3000'],  # for frontend
    allow_methods=['*'],
    allow_headers=['*']
)

# this can be a different database than the one used for inventory microservice
redis = get_redis_connection(
    host="redis-13385.c55.eu-central-1-1.ec2.cloud.redislabs.com",
    port=13385,
    password="CIczfU98k7e4hAV2vpH6TleoxAnHIZkQ",
    decode_responses=True
)


class Order(HashModel):
    product_id: str
    price: float
    fee: float
    total: float
    quantity: int
    status: str  # pending, completed, refunded

    class Meta:
        database = redis


@app.get("/orders/{pk}")
def get(pk: str):
    return Order.get(pk)


@app.post("/orders")
async def create(request: Request, background_tasks: BackgroundTasks):
    body = await request.json()  # id and quantity
    id = body["id"]
    req = requests.get('http://localhost:8001/products/%s' % body['id'])
    product = req.json()

    order = Order(
        product_id=body['id'],
        price=product['price'],
        fee=product['price'] * 0.2,
        total=product['price'] * 1.2,
        quantity=body['quantity'],
        status='pending'
    )
    order.save()
    background_tasks.add_task(order_completed, order)
    return order


def order_completed(order: Order):
    time.sleep(3)  # mocking order processing
    order.status = "completed"
    order.save()

    # sent event to redis-stream
    # * will do the auto-generation of event-id
    redis.xadd('order_completed', order.dict(), '*')
