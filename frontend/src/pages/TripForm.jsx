import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { createTrip, setTripId, getToken } from "../api/api.js";

const DESTINATIONS = ["Germany", "United Kingdom", "Canada"];

export default function TripForm() {
  const navigate = useNavigate();
  const today = new Date().toISOString().split("T")[0];

  const [nationality] = useState("India"); // MVP: India only
  const [destination, setDestination] = useState("Germany");
  const [visaType] = useState("student"); // MVP: student visa only
  const [travelDate, setTravelDate] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  // Not logged in? Ask the user to log in first.
  if (!getToken()) {
    return (
      <div className="card">
        <p>Please log in first.</p>
        <button onClick={() => navigate("/")}>Go to login</button>
      </div>
    );
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    setLoading(true);
    try {
      const trip = await createTrip({
        nationality,
        destination,
        visa_type: visaType,
        travel_date: travelDate,
      });
      setTripId(trip.id);
      navigate("/checklist");
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="card" style={{ maxWidth: 480, margin: "0 auto" }}>
      <h2>Plan your trip</h2>
      <p className="muted">
        We find the official visa pages and build a checklist where every item
        shows its source.
      </p>

      <form onSubmit={handleSubmit}>
        <label>Nationality</label>
        <select value={nationality} disabled>
          <option>India</option>
        </select>

        <label>Destination</label>
        <select
          value={destination}
          onChange={(e) => setDestination(e.target.value)}
          disabled={loading}
        >
          {DESTINATIONS.map((d) => (
            <option key={d}>{d}</option>
          ))}
        </select>

        <label>Visa type</label>
        <select value={visaType} disabled>
          <option value="student">Student</option>
        </select>

        <label>Travel date</label>
        <input
          type="date"
          min={today}
          value={travelDate}
          onChange={(e) => setTravelDate(e.target.value)}
          required
          disabled={loading}
        />

        {error && <p className="error">{error}</p>}

        {loading && (
          <p className="muted">
            Searching official sources and reading them. This can take up to a
            minute. Please keep this page open...
          </p>
        )}

        <button type="submit" disabled={loading}>
          {loading ? "Building your checklist..." : "Build my checklist"}
        </button>
      </form>
    </div>
  );
}