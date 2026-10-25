import { useState } from "react";

const initial = [
  { id: 1, name: "Proof of financial resources", required: true, details: "Blocked account or equivalent funds", status: "pending", source_url: "https://india.diplo.de/in-en/service/2755482-2755482", passage: "Sample passage: applicants must prove they can finance their stay.", last_checked: "2026-10-25 10:05" },
  { id: 2, name: "University admission letter", required: true, details: "Issued by a recognised university", status: "done", source_url: "https://india.diplo.de/in-en/service/2546328-2546328", passage: "Sample passage: a letter of admission must be submitted.", last_checked: "2026-10-25 10:05" },
  { id: 3, name: "Health insurance proof", required: true, details: "Valid for the full stay", status: "pending", source_url: "https://india.diplo.de/in-en/service/2755482-2755482", passage: "Sample passage: proof of health insurance is required.", last_checked: "2026-10-25 10:05" },
];

export default function Checklist() {
  const [items, setItems] = useState(initial);
  const toggle = (id) =>
    setItems(items.map((i) => (i.id === id ? { ...i, status: i.status === "done" ? "pending" : "done" } : i)));

  return (
    <div style={{ maxWidth: 800, margin: "20px auto", padding: 16, fontFamily: "sans-serif" }}>
      <h2>Checklist: India to Germany (student visa)</h2>
      <p style={{ background: "#fff3cd", padding: 8, borderRadius: 6 }}>SAMPLE DATA for demo</p>
      {items.map((i) => (
        <div key={i.id} style={{ border: "1px solid #ccc", borderRadius: 8, padding: 12, marginBottom: 10 }}>
          <label>
            <input type="checkbox" checked={i.status === "done"} onChange={() => toggle(i.id)} />{" "}
            <b>{i.name}</b> {i.required ? "(required)" : "(optional)"}
          </label>
          <div>{i.details}</div>
          <div style={{ fontStyle: "italic", margin: "6px 0" }}>"{i.passage}"</div>
          <div style={{ fontSize: 13 }}>
            Source: <a href={i.source_url} target="_blank" rel="noreferrer">{i.source_url}</a>
          </div>
          <div style={{ fontSize: 13 }}>Last checked: {i.last_checked}</div>
        </div>
      ))}
    </div>
  );
}
