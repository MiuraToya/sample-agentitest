import { BrowserRouter, Routes, Route, Link } from "react-router-dom";
import Home from "./pages/Home";
import About from "./pages/About";
import Todo from "./pages/Todo";

function App() {
  return (
    <BrowserRouter>
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
        </div>
      </nav>
      <main>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/about" element={<About />} />
          <Route path="/todo" element={<Todo />} />
        </Routes>
      </main>
    </BrowserRouter>
  );
}

export default App;
