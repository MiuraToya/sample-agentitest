import { useEffect, useState } from "react";
import { useAuth } from "../auth/AuthContext";

type Todo = {
  id: number;
  title: string;
};

const API_URL = `${import.meta.env.VITE_API_URL ?? ""}/api/todos`;

function TodoPage() {
  const { auth } = useAuth();
  const [todos, setTodos] = useState<Todo[]>([]);
  const [title, setTitle] = useState("");

  const headers = (): Record<string, string> => {
    const h: Record<string, string> = { "Content-Type": "application/json" };
    if (auth.status === "authenticated") {
      h["Authorization"] = `Bearer ${auth.idToken}`;
    }
    return h;
  };

  const fetchTodos = async () => {
    const res = await fetch(API_URL, { headers: headers() });
    setTodos(await res.json());
  };

  useEffect(() => {
    fetchTodos();
  }, []);

  const addTodo = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim()) return;
    await fetch(API_URL, {
      method: "POST",
      headers: headers(),
      body: JSON.stringify({ title }),
    });
    setTitle("");
    fetchTodos();
  };

  const deleteTodo = async (id: number) => {
    await fetch(`${API_URL}/${id}`, { method: "DELETE", headers: headers() });
    fetchTodos();
  };

  return (
    <div>
      <h1>Todo List</h1>
      <div className="card">
        <form
          onSubmit={addTodo}
          style={{ display: "flex", gap: 12, marginBottom: 24 }}
        >
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="Enter a new todo"
          />
          <button type="submit" className="btn btn-primary" style={{ flexShrink: 0 }}>
            Add
          </button>
        </form>

        {todos.length === 0 ? (
          <p style={{ textAlign: "center", padding: 24 }}>
            No todos yet. Add one above!
          </p>
        ) : (
          <ul style={{ listStyle: "none" }}>
            {todos.map((todo) => (
              <li
                key={todo.id}
                style={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                  padding: "12px 0",
                  borderBottom: "1px solid var(--color-border)",
                }}
              >
                <span style={{ fontWeight: 500 }}>{todo.title}</span>
                <button
                  className="btn btn-danger"
                  onClick={() => deleteTodo(todo.id)}
                >
                  Delete
                </button>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}

export default TodoPage;
