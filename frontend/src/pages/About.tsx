function About() {
  return (
    <div>
      <h1>About</h1>
      <div className="card">
        <p style={{ marginBottom: 16 }}>
          This app demonstrates a simple React + FastAPI application.
        </p>
        <p style={{ marginBottom: 16 }}>
          It includes navigation, a todo list with full CRUD operations, and API
          integration.
        </p>
        <div style={{ display: "flex", gap: 12, flexWrap: "wrap" }}>
          {["React", "TypeScript", "Vite", "FastAPI", "Python"].map((tech) => (
            <span
              key={tech}
              style={{
                background: "#f0edfc",
                color: "var(--color-primary)",
                padding: "4px 12px",
                borderRadius: 20,
                fontSize: "0.85rem",
                fontWeight: 600,
              }}
            >
              {tech}
            </span>
          ))}
        </div>
      </div>
    </div>
  );
}

export default About;
