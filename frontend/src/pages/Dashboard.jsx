const done = 1;
const total = 4;

export default function Dashboard() {
  const pct = Math.round((done / total) * 100);
  return (
    <div style={{ maxWidth: 800, margin: "20px auto", padding: 16, fontFamily: "sans-serif" }}>
      <h2>Readiness Dashboard</h2>
      <p style={{ background: "#fff3cd", padding: 8, borderRadius: 6 }}>SAMPLE DATA for demo</p>
      <div style={{ background: "#eee", borderRadius: 8, height: 24, overflow: "hidden" }}>
        <div style={{ width: pct + "%", background: "#28a745", height: "100%" }} />
      </div>
      <p>
        <b>{pct}% ready</b>: {done} done, {total - done} pending
      </p>
    </div>
  );
}
