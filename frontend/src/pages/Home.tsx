import { Link } from "react-router-dom";

function Home() {
  return (
    <div>
      <h1>Welcome to SampleApp</h1>
      <p style={{ marginBottom: 32 }}>
        A simple React + FastAPI application for testing with AgentiTest.
      </p>
      <div style={{ display: "flex", gap: 16 }}>
        <Link to="/todo">
          <div className="card" style={{ cursor: "pointer", minWidth: 200 }}>
            <h3 style={{ color: "var(--color-primary)", marginBottom: 8 }}>
              Todo List
            </h3>
            <p style={{ fontSize: "0.9rem" }}>
              Manage your tasks with a simple todo list.
            </p>
          </div>
        </Link>
        <Link to="/about" style={{ textDecoration: "none" }}>
          <div className="card" style={{ cursor: "pointer", minWidth: 200 }}>
            <h3 style={{ color: "var(--color-primary)", marginBottom: 8 }}>
              About
            </h3>
            <p style={{ fontSize: "0.9rem" }}>
              Learn more about this application.
            </p>
          </div>
        </Link>
      </div>
    </div>
  );
}

export default Home;
