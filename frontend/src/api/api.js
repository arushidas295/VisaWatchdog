import { mockChecklist, mockChanges, mockAlerts, simulatedChange } from "./mockData.js";

const BASE = import.meta.env.VITE_API_URL;
const USE_MOCK = import.meta.env.VITE_USE_MOCK === "true";

// ---------- token storage (the browser remembers the login) ----------
const TOKEN_KEY = "vw_token";
export const getToken = () => localStorage.getItem(TOKEN_KEY);
export const setToken = (t) => localStorage.setItem(TOKEN_KEY, t);
export const clearToken = () => localStorage.removeItem(TOKEN_KEY);

// ---------- real requests ----------
async function request(path, options = {}) {
  const headers = { "Content-Type": "application/json" };
  const token = getToken();
  if (token) headers.Authorization = `Bearer ${token}`;

  const res = await fetch(`${BASE}${path}`, { ...options, headers });

  if (!res.ok) {
    let message = `Request failed (${res.status})`;
    try {
      const data = await res.json();
      if (data.detail) {
        message = typeof data.detail === "string" ? data.detail : JSON.stringify(data.detail);
      }
    } catch {
      // response had no JSON body; keep the default message
    }
    throw new Error(message);
  }
  return res.json();
}

const post = (path, body) => request(path, { method: "POST", body: JSON.stringify(body) });
const patch = (path, body) => request(path, { method: "PATCH", body: JSON.stringify(body) });

// ---------- mock helpers (in-memory, reset when you refresh the page) ----------
const delay = (ms = 400) => new Promise((resolve) => setTimeout(resolve, ms));
let mockItems = structuredClone(mockChecklist.items);
let mockChangeList = [...mockChanges];
let mockAlertList = [...mockAlerts];

// ---------- the functions your pages will call ----------
export async function register(email, password) {
  if (USE_MOCK) {
    await delay();
    return { message: "registered (mock)" };
  }
  return post("/auth/register", { email, password });
}

export async function login(email, password) {
  if (USE_MOCK) {
    await delay();
    return { access_token: "mock-token", token_type: "bearer" };
  }
  return post("/auth/login", { email, password });
}

export async function createTrip(trip) {
  if (USE_MOCK) {
    await delay(1500); // pretend the real one is slow
    return { id: 1, ...trip };
  }
  return post("/trips", trip);
}

export async function getChecklist(tripId) {
  if (USE_MOCK) {
    await delay();
    return { ...mockChecklist, trip_id: tripId, items: structuredClone(mockItems) };
  }
  return request(`/trips/${tripId}/checklist`);
}

export async function refreshTrip(tripId) {
  if (USE_MOCK) {
    await delay(800);
    return { message: "refresh started (mock)" };
  }
  return post(`/trips/${tripId}/refresh`, {});
}

export async function getChanges(tripId) {
  if (USE_MOCK) {
    await delay();
    return structuredClone(mockChangeList);
  }
  return request(`/trips/${tripId}/changes`);
}

export async function getAlerts() {
  if (USE_MOCK) {
    await delay();
    return structuredClone(mockAlertList);
  }
  return request("/alerts");
}

export async function updateItemStatus(itemId, status) {
  if (USE_MOCK) {
    await delay(200);
    mockItems = mockItems.map((it) => (it.id === itemId ? { ...it, status } : it));
    return mockItems.find((it) => it.id === itemId);
  }
  return patch(`/checklist/${itemId}`, { status });
}

export async function simulateChange(tripId) {
  if (USE_MOCK) {
    await delay(600);
    const change = { ...simulatedChange, trip_id: tripId, detected_at: new Date().toISOString() };
    mockChangeList = [change, ...mockChangeList];
    // alert embeds the change object (PROPOSED shape; confirm with backend)
    mockAlertList = [
      { id: Date.now(), user_id: 1, change_id: change.id, seen: false, created_at: change.detected_at, change },
      ...mockAlertList,
    ];
    return change;
  }
  return post("/demo/simulate-change", { trip_id: tripId });
}