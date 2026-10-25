const alerts = [
  {
    id: 1,
    item_name: "Proof of onward travel",
    change_type: "added",
    old_value: "Not required",
    new_value: "Required: confirmed return or onward ticket",
    passage: "Sample passage: applicants must show proof of onward travel.",
    source_url: "https://www.gov.uk/student-visa [SIMULATED]",
    detected_at: "2026-10-25 10:30",
  },
];

export default function Alerts() {
  return (
    <div style={{ maxWidth: 800, margin: "20px auto", padding: 16, fontFamily: "sans-serif" }}>
      <h2>Alerts</h2>
      <p style={{ background: "#fff3cd", padding: 8, borderRadius: 6 }}>SIMULATED change. SAMPLE DATA for demo</p>
      {alerts.map((a) => (
        <div key={a.id} style={{ border: "2px solid #d9534f", borderRadius: 8, padding: 12 }}>
          <b>{a.item_name}</b> ({a.change_type})
          <div style={{ display: "flex", gap: 12, margin: "10px 0" }}>
            <div style={{ flex: 1, background: "#fde8e8", padding: 8, borderRadius: 6 }}>
              <b>Old</b>
              <div>{a.old_value}</div>
            </div>
            <div style={{ flex: 1, background: "#e6f4ea", padding: 8, borderRadius: 6 }}>
              <b>New</b>
              <div>{a.new_value}</div>
            </div>
          </div>
          <div style={{ fontStyle: "italic" }}>"{a.passage}"</div>
          <div style={{ fontSize: 13 }}>Source: {a.source_url}</div>
          <div style={{ fontSize: 13 }}>Detected: {a.detected_at}</div>
          <div style={{ marginTop: 6 }}>Status: Verified, review before applying</div>
        </div>
      ))}
    </div>
  );
}
