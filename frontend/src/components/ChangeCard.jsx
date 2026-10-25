function formatTime(iso) {
  const d = new Date(iso);
  return isNaN(d) ? "unknown time" : d.toLocaleString();
}

const TYPE_LABELS = {
  added: "Added",
  removed: "Removed",
  modified: "Modified",
};

export default function ChangeCard({ change }) {
  const safeLink = change.source_url && change.source_url.startsWith("http");
  const oldText = change.old_value ?? "Not present before";
  const newText = change.new_value ?? "No longer present";

  return (
    <div className={change.is_simulated ? "card change change-sim" : "card change"}>
      {change.is_simulated && (
        <div className="sim-banner">
          SIMULATED CHANGE (demo only, not a real rule change)
        </div>
      )}

      <div className="item-head">
        <span className="item-name">{change.item_name}</span>
        <span className={`badge badge-${change.change_type}`}>
          {TYPE_LABELS[change.change_type] || change.change_type}
        </span>
      </div>

      <div className="diff">
        <div className="diff-col diff-old">
          <div className="diff-title">OLD</div>
          <div>{oldText}</div>
        </div>
        <div className="diff-col diff-new">
          <div className="diff-title">NEW</div>
          <div>{newText}</div>
        </div>
      </div>

      <p className="muted">
        Source:{" "}
        {safeLink ? (
          <a href={change.source_url} target="_blank" rel="noreferrer">
            {change.source_url}
          </a>
        ) : (
          change.source_url || "not available"
        )}
        <br />
        Detected: {formatTime(change.detected_at)}
      </p>

      {change.passage ? (
        <blockquote className="passage">{change.passage}</blockquote>
      ) : (
        <p className="muted">No source passage available for this change.</p>
      )}
    </div>
  );
}