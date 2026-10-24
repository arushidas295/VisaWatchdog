import { Routes, Route, Link } from "react-router-dom";
import Login from "./pages/Login.jsx";
import TripForm from "./pages/TripForm.jsx";
import Checklist from "./pages/Checklist.jsx";
import Changes from "./pages/Changes.jsx";
import Alerts from "./pages/Alerts.jsx";
import Dashboard from "./pages/Dashboard.jsx";

export default function App() {
  return (
    <div>
      <nav className="nav">
        <strong>Visa Rule Watchdog</strong>
        <Link to="/">Login</Link>
        <Link to="/trip">New trip</Link>
        <Link to="/checklist">Checklist</Link>
        <Link to="/changes">Changes</Link>
        <Link to="/alerts">Alerts</Link>
        <Link to="/dashboard">Dashboard</Link>
      </nav>
      <main className="page">
        <Routes>
          <Route path="/" element={<Login />} />
          <Route path="/trip" element={<TripForm />} />
          <Route path="/checklist" element={<Checklist />} />
          <Route path="/changes" element={<Changes />} />
          <Route path="/alerts" element={<Alerts />} />
          <Route path="/dashboard" element={<Dashboard />} />
        </Routes>
      </main>
    </div>
  );
}