import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { register, login, setToken } from "../api/api.js";

export default function Login() {
  const navigate = useNavigate();
  const [mode, setMode] = useState("login"); // "login" or "register"
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault(); // stop the browser reloading the page
    setError("");
    setLoading(true);
    try {
      if (mode === "register") {
        await register(email, password);
      }
      const data = await login(email, password);
      setToken(data.access_token);
      navigate("/trip");
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="card" style={{ maxWidth: 400, margin: "0 auto" }}>
      <h2>{mode === "login" ? "Log in" : "Create account"}</h2>
      <p className="muted">Your visa requirements change. Your checklist should too.</p>

      <form onSubmit={handleSubmit}>
        <label>Email</label>
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />

        <label>Password</label>
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          minLength={6}
          required
        />

        {error && <p className="error">{error}</p>}

        <button type="submit" disabled={loading}>
          {loading ? "Please wait..." : mode === "login" ? "Log in" : "Register"}
        </button>
      </form>

      <p className="muted">
        {mode === "login" ? "No account yet? " : "Already registered? "}
        <a
          href="#"
          onClick={(e) => {
            e.preventDefault();
            setMode(mode === "login" ? "register" : "login");
            setError("");
          }}
        >
          {mode === "login" ? "Register" : "Log in"}
        </a>
      </p>
    </div>
  );
}