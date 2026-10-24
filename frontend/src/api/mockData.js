// MOCK DATA ONLY. Not real visa rules. Shapes are PROPOSED; confirm with backend.

export const mockChecklist = {
  trip_id: 1,
  // source status: "ok" | "blocked" | "error"  (ask backend where this really lives)
  source_status: "ok",
  items: [
    {
      id: 1,
      trip_id: 1,
      name: "Valid passport",
      required: true,
      details: "Passport valid for the whole stay (MOCK).",
      status: "pending",
      source_url: "https://example.org/mock-germany-student-visa",
      passage: "Applicants must hold a valid passport. (MOCK passage)",
      last_checked: "2026-10-24T10:30:00Z",
    },
    {
      id: 2,
      trip_id: 1,
      name: "Proof of financial resources",
      required: true,
      details: "Blocked account or equivalent proof of funds (MOCK).",
      status: "done",
      source_url: "https://example.org/mock-germany-student-visa",
      passage: "Proof of financial means must be provided. (MOCK passage)",
      last_checked: "2026-10-24T10:30:00Z",
    },
    {
      id: 3,
      trip_id: 1,
      name: "University admission letter",
      required: true,
      details: "Letter of admission from a German university (MOCK).",
      status: "pending",
      source_url: "https://example.org/mock-germany-student-visa",
      passage: "A letter of admission is required. (MOCK passage)",
      last_checked: "2026-10-24T10:30:00Z",
    },
    {
      id: 4,
      trip_id: 1,
      name: "Health insurance",
      required: true,
      details: "Valid health insurance coverage (MOCK).",
      status: "pending",
      source_url: "https://example.org/mock-germany-student-visa",
      passage: "Proof of health insurance must be submitted. (MOCK passage)",
      last_checked: "2026-10-24T10:30:00Z",
    },
  ],
};

export const mockChanges = [];
export const mockAlerts = [];

// Used by the mock "simulate change" button
export const simulatedChange = {
  id: 100,
  trip_id: 1,
  item_name: "Proof of onward travel",
  change_type: "added",
  old_value: null,
  new_value: "Required: confirmed return or onward ticket",
  passage: "Applicants must show proof of onward travel. (SIMULATED passage)",
  source_url: "https://example.org/mock-germany-student-visa",
  detected_at: "2026-10-24T11:00:00Z",
  is_simulated: true,
};