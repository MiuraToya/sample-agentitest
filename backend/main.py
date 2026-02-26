from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage
todos: list[dict] = []
next_id = 1


class TodoCreate(BaseModel):
    title: str


@app.get("/api/todos")
def get_todos():
    return todos


@app.post("/api/todos", status_code=201)
def create_todo(todo: TodoCreate):
    global next_id
    new_todo = {"id": next_id, "title": todo.title}
    todos.append(new_todo)
    next_id += 1
    return new_todo


@app.delete("/api/todos/{todo_id}")
def delete_todo(todo_id: int):
    for i, todo in enumerate(todos):
        if todo["id"] == todo_id:
            return todos.pop(i)
    raise HTTPException(status_code=404, detail="Todo not found")
