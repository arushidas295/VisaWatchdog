import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { getChanges, simulateChange, getTripId, getToken } from "../api/api.js";
import ChangeCard from "../components/ChangeCard.jsx";

export default function Changes() {
  const navigate = useNavigate();
  const tripId = getTripId();
  const [changes, setChanges] = useState([]);
  const [loading, setLoading] = useState(true);
  const [simulating, setSimulating] = useState(false);
  const [error, setError] = useState("");

  async function load() {
    setError("");
    try {
      const result = await getChanges(tripId);
      setChanges(result);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    if (tripId && getToken()) load();
    else setLoading(false);
  }, []);

  async function handleSimulate() {
    setSimulating(true);
    setError("");
    try {
      await simulateChange(tripId);
      await load();
    } catch (err) {
      setError(err.message);
    } finally {
      setSimulating(false);
    }
  }

  if (!getToken()) {
    return (
      <div className="card">
        <p>Please log in first.</p>
        <button onClick={() => navigate("/")}>Go to login</button>
      </div>
    );
  }
  if (!tripId) {
    return (
      <div className="card">
        <p>No trip yet. Create one first.</p>
        <button onClick={() => navigate("/trip")}>Plan a trip</button>
      </div>
    );
  }
  if (loading) return <p className="muted">Loading changes...</p>;

  return (
    <div>
      <h2>What changed</h2>
      <p className="muted">
        Old and new requirements side by side, with the source passage. Review
        on the official website before applying.
      </p>

      {error && <p className="error">{error}</p>}

      {changes.length === 0 && (
        <div className="card">
          <p>No changes detected yet. Your checklist matches the last check.</p>
        </div>
      )}

      {changes.map((change) => (
        <ChangeCard key={change.id} change={change} />
      ))}

      <button onClick={handleSimulate} disabled={simulating}>
        {simulating ? "Simulating..." : "Simulate a change (demo)"}
      </button>{" "}
      <Link to="/checklist">Back to checklist</Link>
    </div>
  );
}