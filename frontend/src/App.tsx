import { BrowserRouter, Routes, Route, Link, Navigate } from "react-router-dom";
import { AuthProvider, useAuth } from "./auth/AuthContext";
import Home from "./pages/Home";
import About from "./pages/About";
import Todo from "./pages/Todo";
import Login from "./pages/Login";

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { auth } = useAuth();
  if (auth.status === "loading") return null;
  if (auth.status === "unauthenticated") return <Navigate to="/login" />;
  return <>{children}</>;
}

function NavBar() {
  const { auth, signOut } = useAuth();
  return (
    <nav>
      <div className="nav-inner">
        <Link to="/" className="logo">
          SampleApp
        </Link>
        <Link to="/" className="nav-link">
          Home
        </Link>
        <Link to="/about" className="nav-link">
          About
        </Link>
        <Link to="/todo" className="nav-link">
          Todo
        </Link>
        {auth.status === "authenticated" ? (
          <button
            className="btn"
            onClick={signOut}
            style={{ marginLeft: 8, fontSize: "0.85rem", padding: "6px 12px" }}
          >
            Sign Out
          </button>
        ) : (
          <Link to="/login" className="nav-link">
            Sign In
          </Link>
        )}
      </div>
    </nav>
  );
}

function AppRoutes() {
  return (
    <>
      <NavBar />
      <main>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/about" element={<About />} />
          <Route path="/login" element={<Login />} />
          <Route
            path="/todo"
            element={
              <ProtectedRoute>
                <Todo />
              </ProtectedRoute>
            }
          />
        </Routes>
      </main>
    </>
  );
}

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppRoutes />
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;
