import { useState } from "react";

function formatTime(iso) {
  const d = new Date(iso);
  return isNaN(d) ? "unknown time" : d.toLocaleString();
}

export default function ChecklistItem({ item, onToggle }) {
  const [open, setOpen] = useState(false); // is the passage expanded?
  const done = item.status === "done";
  const safeLink = item.source_url && item.source_url.startsWith("http");

  return (
    <div className={done ? "card item item-done" : "card item"}>
      <div className="item-head">
        <label className="check">
          <input type="checkbox" checked={done} onChange={() => onToggle(item)} />
          <span className="item-name">{item.name}</span>
        </label>
        <span className={item.required ? "badge badge-req" : "badge"}>
          {item.required ? "Required" : "Optional"}
        </span>
        {item.uncertain && <span className="badge badge-warn">Uncertain</span>}
      </div>

      {item.details && <p className="item-details">{item.details}</p>}

      <p className="muted">
        Source:{" "}
        {safeLink ? (
          <a href={item.source_url} target="_blank" rel="noreferrer">
            {item.source_url}
          </a>
        ) : (
          item.source_url
        )}
        <br />
        Last checked: {formatTime(item.last_checked)}
      </p>

      <button className="link-button" onClick={() => setOpen(!open)}>
        {open ? "Hide source passage" : "Show source passage"}
      </button>
      {open && <blockquote className="passage">{item.passage}</blockquote>}
    </div>
  );
}