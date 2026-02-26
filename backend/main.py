import os

import boto3
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
from pydantic import BaseModel

# --- DynamoDB setup ---
TABLE_NAME = os.getenv("DYNAMODB_TABLE", "sample-agentitest-todos")
REGION = os.getenv("AWS_REGION_NAME", "ap-northeast-1")

dynamodb = boto3.resource("dynamodb", region_name=REGION)
table = dynamodb.Table(TABLE_NAME)


def _ensure_counter():
    """Initialize the atomic counter item if it doesn't exist."""
    try:
        table.put_item(
            Item={"id": 0, "counter_value": 0, "title": "__counter__"},
            ConditionExpression="attribute_not_exists(id)",
        )
    except dynamodb.meta.client.exceptions.ConditionalCheckFailedException:
        pass


def _next_id() -> int:
    """Atomically increment and return the next todo ID."""
    response = table.update_item(
        Key={"id": 0},
        UpdateExpression="ADD counter_value :inc",
        ExpressionAttributeValues={":inc": 1},
        ReturnValues="UPDATED_NEW",
    )
    return int(response["Attributes"]["counter_value"])


# --- FastAPI app ---
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class TodoCreate(BaseModel):
    title: str


@app.on_event("startup")
def startup():
    _ensure_counter()


@app.get("/api/todos")
def get_todos():
    response = table.scan()
    items = response.get("Items", [])
    todos = [
        {"id": int(item["id"]), "title": item["title"]}
        for item in items
        if item["id"] != 0
    ]
    todos.sort(key=lambda x: x["id"])
    return todos


@app.post("/api/todos", status_code=201)
def create_todo(todo: TodoCreate):
    new_id = _next_id()
    table.put_item(Item={"id": new_id, "title": todo.title})
    return {"id": new_id, "title": todo.title}


@app.delete("/api/todos/{todo_id}")
def delete_todo(todo_id: int):
    response = table.delete_item(
        Key={"id": todo_id},
        ReturnValues="ALL_OLD",
    )
    old_item = response.get("Attributes")
    if not old_item or old_item.get("id") == 0:
        raise HTTPException(status_code=404, detail="Todo not found")
    return {"id": int(old_item["id"]), "title": old_item["title"]}


# Lambda handler
handler = Mangum(app)
