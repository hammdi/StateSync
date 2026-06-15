import { useState, useEffect, useCallback } from "react";
import type { EmployeeInfo, EmployeeDashboardData, ServiceRequest } from "../types";
import { employeeLogin, fetchEmployeeDashboard, fetchEmployeeRequests, processRequest } from "../api/client";

interface Props {
  onBack: () => void;
}

const statusStyle: Record<string, string> = {
  pending: "bg-amber-100 text-amber-700",
  approved: "bg-emerald-100 text-emerald-700",
  rejected: "bg-red-100 text-red-700",
};

export default function EmployeePortal({ onBack }: Props) {
  const [token, setToken] = useState<string | null>(null);
  const [employee, setEmployee] = useState<EmployeeInfo | null>(null);
  const [dashboard, setDashboard] = useState<EmployeeDashboardData | null>(null);
  const [requests, setRequests] = useState<ServiceRequest[]>([]);
  const [tab, setTab] = useState<"dashboard" | "pending" | "processed">("dashboard");
  const [processing, setProcessing] = useState<string | null>(null);
  const [note, setNote] = useState("");

  // Login state
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [loginError, setLoginError] = useState("");
  const [loggingIn, setLoggingIn] = useState(false);

  const loadDashboard = useCallback(async () => {
    if (!token) return;
    try {
      const d = await fetchEmployeeDashboard(token);
      setDashboard(d);
    } catch { /* */ }
  }, [token]);

  const loadRequests = useCallback(async (status: string) => {
    if (!token) return;
    try { setRequests(await fetchEmployeeRequests(token, status)); } catch { /* */ }
  }, [token]);

  useEffect(() => {
    if (token && tab === "dashboard") loadDashboard();
    if (token && tab === "pending") loadRequests("pending");
    if (token && tab === "processed") loadRequests("approved");
  }, [token, tab, loadDashboard, loadRequests]);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoggingIn(true);
    setLoginError("");
    try {
      const res = await employeeLogin(username, password);
      setToken(res.access_token);
      setEmployee(res.employee);
    } catch (err) {
      setLoginError(err instanceof Error ? err.message : "Login failed");
    } finally {
      setLoggingIn(false);
    }
  };

  const handleProcess = async (id: string, action: string) => {
    if (!token) return;
    setProcessing(id);
    try {
      await processRequest(id, action, note, token);
      setNote("");
      setProcessing(null);
      loadDashboard();
      loadRequests(tab === "pending" ? "pending" : "approved");
    } catch {
      alert("Failed to process request");
      setProcessing(null);
    }
  };

  // ── Login screen ──
  if (!token) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-800 to-slate-900 flex items-center justify-center p-4">
        <div className="w-full max-w-sm">
          <button onClick={onBack} className="text-slate-400 hover:text-white text-sm mb-6 block">&larr; Back to Citizen Portal</button>
          <div className="bg-white rounded-2xl shadow-xl p-8">
            <div className="text-center mb-6">
              <div className="w-12 h-12 bg-slate-800 rounded-xl flex items-center justify-center text-white text-lg font-bold mx-auto">S</div>
              <h1 className="text-xl font-bold text-gray-900 mt-3">Employee Portal</h1>
              <p className="text-sm text-gray-500 mt-1">Ministry staff login</p>
            </div>
            <form onSubmit={handleLogin} className="space-y-4">
              <input type="text" placeholder="Username" value={username} onChange={(e) => setUsername(e.target.value)}
                className="w-full px-4 py-2.5 border rounded-xl text-sm bg-gray-50" required />
              <input type="password" placeholder="Password" value={password} onChange={(e) => setPassword(e.target.value)}
                className="w-full px-4 py-2.5 border rounded-xl text-sm bg-gray-50" required />
              {loginError && <p className="text-red-600 text-xs">{loginError}</p>}
              <button type="submit" disabled={loggingIn}
                className="w-full py-2.5 bg-slate-800 text-white rounded-xl text-sm font-semibold hover:bg-slate-700 disabled:opacity-50">
                {loggingIn ? "Logging in..." : "Login"}
              </button>
            </form>
            <p className="text-[11px] text-gray-400 text-center mt-4">Demo: civil.agent / admin123</p>
          </div>
        </div>
      </div>
    );
  }

  // ── Logged in ──
  const tabs = [
    { id: "dashboard" as const, label: "Dashboard" },
    { id: "pending" as const, label: "Pending", count: dashboard?.stats.pending },
    { id: "processed" as const, label: "Processed" },
  ];

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-slate-800 text-white shadow-lg">
        <div className="max-w-6xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-white/10 rounded-xl flex items-center justify-center font-bold">S</div>
            <div>
              <h1 className="text-lg font-bold">StateSync <span className="text-slate-400 font-normal">Employee</span></h1>
              <p className="text-slate-400 text-[11px]">{employee?.ministry_label} &middot; {employee?.full_name}</p>
            </div>
          </div>
          <div className="flex gap-2">
            <button onClick={onBack} className="px-3 py-1.5 bg-white/10 rounded-lg text-xs hover:bg-white/20">Citizen Portal</button>
            <button onClick={() => { setToken(null); setEmployee(null); }} className="px-3 py-1.5 bg-white/10 rounded-lg text-xs hover:bg-white/20">Logout</button>
          </div>
        </div>
      </header>

      {/* Tabs */}
      <nav className="bg-white border-b sticky top-0 z-10 shadow-sm">
        <div className="max-w-6xl mx-auto px-4 flex gap-1">
          {tabs.map((t) => (
            <button key={t.id} onClick={() => setTab(t.id)}
              className={`relative px-5 py-3 text-sm font-medium ${tab === t.id ? "text-slate-800" : "text-gray-500 hover:text-gray-700"}`}>
              {t.label}
              {t.count != null && t.count > 0 && <span className="ml-1.5 text-[10px] bg-amber-100 text-amber-700 px-1.5 py-0.5 rounded-full font-bold">{t.count}</span>}
              {tab === t.id && <span className="absolute bottom-0 left-2 right-2 h-0.5 bg-slate-800 rounded-full" />}
            </button>
          ))}
        </div>
      </nav>

      <main className="max-w-6xl mx-auto px-4 py-6">
        {/* Dashboard */}
        {tab === "dashboard" && dashboard && (
          <div className="space-y-6 animate-fade-in">
            <div className="grid grid-cols-4 gap-4">
              {[
                { label: "Total", value: dashboard.stats.total, color: "bg-slate-800" },
                { label: "Pending", value: dashboard.stats.pending, color: "bg-amber-500" },
                { label: "Approved", value: dashboard.stats.approved, color: "bg-emerald-500" },
                { label: "Rejected", value: dashboard.stats.rejected, color: "bg-red-500" },
              ].map((s) => (
                <div key={s.label} className="bg-white rounded-xl border p-5 shadow-sm">
                  <div className="text-3xl font-bold text-gray-900">{s.value}</div>
                  <div className="text-xs text-gray-500 mt-1">{s.label}</div>
                  <div className={`h-1 w-10 rounded-full ${s.color} mt-2`} />
                </div>
              ))}
            </div>
            <h3 className="text-sm font-bold text-gray-600 uppercase tracking-wider">Pending Queue</h3>
            {dashboard.pending_requests.length === 0 ? (
              <div className="bg-white rounded-xl p-8 text-center text-gray-400 text-sm">No pending requests.</div>
            ) : (
              <div className="space-y-3">
                {dashboard.pending_requests.map((r) => (
                  <RequestCard key={r.id} request={r} processing={processing} note={note} setNote={setNote} onProcess={handleProcess} />
                ))}
              </div>
            )}
          </div>
        )}

        {/* Pending / Processed lists */}
        {(tab === "pending" || tab === "processed") && (
          <div className="space-y-3 animate-fade-in">
            {requests.length === 0 ? (
              <div className="bg-white rounded-xl p-8 text-center text-gray-400 text-sm">No {tab} requests.</div>
            ) : (
              requests.map((r) => (
                <RequestCard key={r.id} request={r} processing={processing} note={note} setNote={setNote}
                  onProcess={tab === "pending" ? handleProcess : undefined} />
              ))
            )}
          </div>
        )}
      </main>
    </div>
  );
}

function RequestCard({ request: r, processing, note, setNote, onProcess }: {
  request: ServiceRequest;
  processing: string | null;
  note: string;
  setNote: (n: string) => void;
  onProcess?: (id: string, action: string) => void;
}) {
  const isActive = processing === r.id;
  return (
    <div className="bg-white rounded-xl border border-gray-100 p-5 shadow-sm">
      <div className="flex items-start justify-between">
        <div>
          <div className="flex items-center gap-2">
            <h3 className="text-sm font-semibold text-gray-900">{r.service_name}</h3>
            <span className={`text-[10px] font-bold uppercase px-2 py-0.5 rounded-md ${statusStyle[r.status]}`}>{r.status}</span>
          </div>
          <p className="text-xs text-gray-500 mt-1">CIN: <span className="font-mono">{r.cin}</span> &middot; {r.ministry_label}</p>
          {r.details && Object.keys(r.details).length > 0 && (
            <div className="mt-2 flex flex-wrap gap-2">
              {Object.entries(r.details).map(([k, v]) => (
                <span key={k} className="text-[11px] bg-gray-100 rounded px-2 py-0.5">{k}: <span className="font-medium">{v}</span></span>
              ))}
            </div>
          )}
        </div>
        <time className="text-[11px] text-gray-400 flex-shrink-0">{new Date(r.submitted_at).toLocaleString()}</time>
      </div>

      {r.response_note && (
        <p className="text-xs text-gray-600 mt-2 bg-gray-50 rounded-lg px-3 py-2">{r.response_note}</p>
      )}

      {onProcess && r.status === "pending" && (
        <div className="mt-3 pt-3 border-t border-gray-100">
          <input
            type="text" placeholder="Add a note (optional)..."
            value={isActive ? note : ""}
            onChange={(e) => { setNote(e.target.value); }}
            onFocus={() => { /* set active */ }}
            className="w-full px-3 py-2 border border-gray-200 rounded-lg text-xs mb-2 bg-gray-50"
          />
          <div className="flex gap-2">
            <button onClick={() => onProcess(r.id, "approve")} disabled={processing !== null}
              className="px-4 py-1.5 bg-emerald-600 text-white rounded-lg text-xs font-semibold hover:bg-emerald-700 disabled:opacity-50">
              Approve
            </button>
            <button onClick={() => onProcess(r.id, "reject")} disabled={processing !== null}
              className="px-4 py-1.5 bg-red-600 text-white rounded-lg text-xs font-semibold hover:bg-red-700 disabled:opacity-50">
              Reject
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
