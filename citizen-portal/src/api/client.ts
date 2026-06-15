import type {
  CitizenData, AuditEntry, ErrorReportPayload,
  ServiceDef, ServiceRequest, DocumentMeta, DocumentFull,
  EmployeeInfo, EmployeeDashboardData,
} from "../types";

const API = import.meta.env.VITE_API_URL || "http://localhost:8080";

async function get<T>(path: string, token?: string): Promise<T> {
  const headers: Record<string, string> = {};
  if (token) headers["Authorization"] = `Bearer ${token}`;
  const res = await fetch(`${API}${path}`, { headers });
  if (!res.ok) {
    const body = await res.json().catch(() => ({ detail: "Network error" }));
    throw new Error(body.detail || `Request failed (${res.status})`);
  }
  return res.json();
}

async function post<T>(path: string, body: unknown, token?: string): Promise<T> {
  const headers: Record<string, string> = { "Content-Type": "application/json" };
  if (token) headers["Authorization"] = `Bearer ${token}`;
  const res = await fetch(`${API}${path}`, { method: "POST", headers, body: JSON.stringify(body) });
  if (!res.ok) {
    const b = await res.json().catch(() => ({ detail: "Network error" }));
    throw new Error(b.detail || `Request failed (${res.status})`);
  }
  return res.json();
}

async function put<T>(path: string, body: unknown, token?: string): Promise<T> {
  const headers: Record<string, string> = { "Content-Type": "application/json" };
  if (token) headers["Authorization"] = `Bearer ${token}`;
  const res = await fetch(`${API}${path}`, { method: "PUT", headers, body: JSON.stringify(body) });
  if (!res.ok) {
    const b = await res.json().catch(() => ({ detail: "Network error" }));
    throw new Error(b.detail || `Request failed (${res.status})`);
  }
  return res.json();
}

// ── Citizen ──────────────────────────────────
export const fetchCitizenData = (cin: string) => get<CitizenData>(`/citizen/${encodeURIComponent(cin)}`);
export const fetchAuditTrail = (cin: string) => get<AuditEntry[]>(`/citizen/${encodeURIComponent(cin)}/audit`);
export const submitErrorReport = (cin: string, r: ErrorReportPayload) => post<void>(`/citizen/${encodeURIComponent(cin)}/report`, r);

// ── Services ─────────────────────────────────
export const fetchServicesCatalog = () => get<{ catalog: Record<string, ServiceDef[]>; labels: Record<string, string> }>("/services");
export const submitServiceRequest = (body: { cin: string; ministry: string; service_id: string; details: Record<string, string> }) =>
  post<ServiceRequest>("/requests", body);

// ── Requests ─────────────────────────────────
export const fetchRequests = (cin: string) => get<ServiceRequest[]>(`/requests/${encodeURIComponent(cin)}`);

// ── Documents ────────────────────────────────
export const fetchDocuments = (cin: string) => get<DocumentMeta[]>(`/documents/${encodeURIComponent(cin)}`);
export const fetchDocument = (cin: string, docId: string) => get<DocumentFull>(`/documents/${encodeURIComponent(cin)}/${docId}`);
export const getDocumentPdfUrl = (cin: string, docId: string) => `${API}/documents/${encodeURIComponent(cin)}/${docId}/pdf`;

// ── Employee ─────────────────────────────────
export const employeeLogin = (username: string, password: string) =>
  post<{ access_token: string; employee: EmployeeInfo }>("/employee/login", { username, password });
export const fetchEmployeeDashboard = (token: string) => get<EmployeeDashboardData>("/employee/dashboard", token);
export const fetchEmployeeRequests = (token: string, status = "pending") => get<ServiceRequest[]>(`/employee/requests?status=${status}`, token);
export const processRequest = (id: string, action: string, note: string, token: string) =>
  put<ServiceRequest>(`/employee/requests/${id}`, { action, note }, token);
