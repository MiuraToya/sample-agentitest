import { useState } from "react";
import { useAuth } from "../auth/AuthContext";
import { useNavigate } from "react-router-dom";

type Mode = "signIn" | "signUp" | "confirm";

function LoginPage() {
  const { signIn, signUp, confirmSignUp } = useAuth();
  const navigate = useNavigate();

  const [mode, setMode] = useState<Mode>("signIn");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [code, setCode] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      if (mode === "signUp") {
        await signUp(email, password);
        setMode("confirm");
      } else if (mode === "confirm") {
        await confirmSignUp(email, code);
        await signIn(email, password);
        navigate("/todo");
      } else {
        await signIn(email, password);
        navigate("/todo");
      }
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h1>{mode === "signIn" ? "Sign In" : mode === "signUp" ? "Sign Up" : "Confirm Email"}</h1>
      <div className="card" style={{ maxWidth: 400 }}>
        <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: 16 }}>
          {mode !== "confirm" ? (
            <>
              <input
                type="text"
                placeholder="Email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
              <input
                type="password"
                placeholder="Password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                style={{
                  padding: "10px 16px",
                  border: "2px solid var(--color-border)",
                  borderRadius: "var(--radius)",
                  fontSize: "0.95rem",
                  outline: "none",
                }}
              />
            </>
          ) : (
            <>
              <p style={{ fontSize: "0.9rem" }}>
                A verification code has been sent to <strong>{email}</strong>
              </p>
              <input
                type="text"
                placeholder="Verification code"
                value={code}
                onChange={(e) => setCode(e.target.value)}
                required
              />
            </>
          )}

          {error && (
            <p style={{ color: "var(--color-danger)", fontSize: "0.9rem" }}>{error}</p>
          )}

          <button type="submit" className="btn btn-primary" disabled={loading}>
            {loading
              ? "..."
              : mode === "signIn"
              ? "Sign In"
              : mode === "signUp"
              ? "Sign Up"
              : "Confirm & Sign In"}
          </button>
        </form>

        {mode !== "confirm" && (
          <p style={{ marginTop: 16, textAlign: "center", fontSize: "0.9rem" }}>
            {mode === "signIn" ? (
              <>
                Don't have an account?{" "}
                <a href="#" onClick={() => { setMode("signUp"); setError(""); }}>
                  Sign Up
                </a>
              </>
            ) : (
              <>
                Already have an account?{" "}
                <a href="#" onClick={() => { setMode("signIn"); setError(""); }}>
                  Sign In
                </a>
              </>
            )}
          </p>
        )}
      </div>
    </div>
  );
}

export default LoginPage;
