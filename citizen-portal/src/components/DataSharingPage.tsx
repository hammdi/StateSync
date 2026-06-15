import { useState, useEffect, useCallback } from "react";

const API = import.meta.env.VITE_API_URL || "http://localhost:8080";

interface Props { cin: string }

// eslint-disable-next-line @typescript-eslint/no-explicit-any
type Share = any;

const MINISTRIES = [
  { id: "civil", label: "Civil Status" }, { id: "education", label: "Education" },
  { id: "defense", label: "Defense" }, { id: "health", label: "Health" },
  { id: "justice", label: "Justice" }, { id: "finance", label: "Finance" },
  { id: "social", label: "Social Affairs" }, { id: "transport", label: "Transport" },
  { id: "property", label: "Property" },
];

export default function DataSharingPage({ cin }: Props) {
  const [shares, setShares] = useState<Share[]>([]);
  const [showForm, setShowForm] = useState(false);
  const [result, setResult] = useState<{ token: string; access_code: string; share_url: string } | null>(null);

  // Form state
  const [recipient, setRecipient] = useState("");
  const [purpose, setPurpose] = useState("");
  const [selected, setSelected] = useState<string[]>([]);
  const [hours, setHours] = useState(24);
  const [oneTime, setOneTime] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  const loadShares = useCallback(async () => {
    const res = await fetch(`${API}/shares/${cin}`);
    if (res.ok) setShares(await res.json());
  }, [cin]);

  useEffect(() => { loadShares(); }, [loadShares]);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      const res = await fetch(`${API}/shares`, {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ cin, recipient_name: recipient, purpose, ministries: selected, expires_hours: hours, one_time: oneTime }),
      });
      if (res.ok) {
        const data = await res.json();
        setResult(data);
        setShowForm(false);
        loadShares();
      }
    } catch { alert("Failed to create share"); }
    setSubmitting(false);
  };

  const handleRevoke = async (token: string) => {
    await fetch(`${API}/shares/${cin}/${token}`, { method: "DELETE" });
    loadShares();
  };

  const toggleMinistry = (id: string) => {
    setSelected(prev => prev.includes(id) ? prev.filter(m => m !== id) : [...prev, id]);
  };

  // ── Success view ──
  if (result) {
    return (
      <div className="animate-fade-in max-w-lg mx-auto">
        <div className="bg-white rounded-2xl border-2 border-emerald-400 p-8 text-center shadow-lg">
          <div className="w-16 h-16 bg-emerald-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg className="w-8 h-8 text-emerald-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101" />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.172 13.828a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.102 1.101" />
            </svg>
          </div>
          <h3 className="text-lg font-bold text-gray-900">Share Link Created</h3>
          <p className="text-sm text-gray-500 mt-2">Send these credentials to your recipient:</p>

          <div className="mt-6 bg-gray-50 rounded-xl p-4 text-left space-y-3">
            <div>
              <div className="text-[10px] font-bold text-gray-400 uppercase">Access Code (share this)</div>
              <div className="text-2xl font-mono font-bold text-indigo-600 tracking-widest mt-1">{result.access_code}</div>
            </div>
            <div>
              <div className="text-[10px] font-bold text-gray-400 uppercase">Share Token</div>
              <div className="text-xs font-mono text-gray-600 break-all mt-1">{result.token}</div>
            </div>
          </div>

          <p className="text-xs text-gray-400 mt-4">
            The recipient needs both the token and access code to view your data.
            You can revoke access at any time.
          </p>

          <button onClick={() => setResult(null)} className="mt-6 px-6 py-2 bg-gray-100 rounded-xl text-sm font-medium hover:bg-gray-200">
            Done
          </button>
        </div>
      </div>
    );
  }

  // ── Create form ──
  if (showForm) {
    return (
      <div className="animate-fade-in max-w-lg mx-auto">
        <button onClick={() => setShowForm(false)} className="text-sm text-blue-600 hover:underline mb-4">&larr; Back</button>
        <div className="bg-white rounded-2xl border p-6 shadow-sm">
          <h2 className="text-lg font-bold text-gray-900 mb-1">Create Share Link</h2>
          <p className="text-xs text-gray-500 mb-5">Choose exactly what data to share and for how long.</p>

          <form onSubmit={handleCreate} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Recipient Name</label>
              <input type="text" value={recipient} onChange={e => setRecipient(e.target.value)} required
                placeholder="e.g., National Bank, Employer Corp" className="w-full px-3 py-2 border rounded-xl text-sm bg-gray-50" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Purpose</label>
              <input type="text" value={purpose} onChange={e => setPurpose(e.target.value)}
                placeholder="e.g., Loan application, Employment verification" className="w-full px-3 py-2 border rounded-xl text-sm bg-gray-50" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Select Data to Share</label>
              <div className="grid grid-cols-3 gap-2">
                {MINISTRIES.map(m => (
                  <button key={m.id} type="button" onClick={() => toggleMinistry(m.id)}
                    className={`px-3 py-2 rounded-lg text-xs font-medium border transition-colors ${
                      selected.includes(m.id) ? "bg-blue-50 border-blue-400 text-blue-700" : "bg-gray-50 border-gray-200 text-gray-600"
                    }`}>{m.label}</button>
                ))}
              </div>
              {selected.length === 0 && <p className="text-xs text-red-500 mt-1">Select at least one ministry</p>}
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Expires In</label>
                <select value={hours} onChange={e => setHours(Number(e.target.value))}
                  className="w-full px-3 py-2 border rounded-xl text-sm bg-gray-50">
                  <option value={1}>1 hour</option>
                  <option value={24}>24 hours</option>
                  <option value={168}>7 days</option>
                  <option value={720}>30 days</option>
                </select>
              </div>
              <div className="flex items-center gap-2 mt-6">
                <input type="checkbox" checked={oneTime} onChange={e => setOneTime(e.target.checked)} id="onetime" className="rounded" />
                <label htmlFor="onetime" className="text-sm text-gray-700">One-time access only</label>
              </div>
            </div>
            <button type="submit" disabled={submitting || selected.length === 0}
              className="w-full py-3 bg-gradient-to-r from-blue-600 to-indigo-600 text-white font-semibold rounded-xl disabled:opacity-50">
              {submitting ? "Creating..." : "Generate Share Link"}
            </button>
          </form>
        </div>
      </div>
    );
  }

  // ── List view ──
  const active = shares.filter((s: Share) => s.active);
  const expired = shares.filter((s: Share) => !s.active);

  return (
    <div className="animate-fade-in">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-xl font-bold text-gray-900">Data Sharing</h2>
          <p className="text-sm text-gray-500 mt-1">Control who can see your data. Create secure, time-limited share links.</p>
        </div>
        <button onClick={() => { setShowForm(true); setRecipient(""); setPurpose(""); setSelected([]); setHours(24); setOneTime(false); }}
          className="px-5 py-2.5 bg-gradient-to-r from-blue-600 to-indigo-600 text-white text-sm font-semibold rounded-xl hover:shadow-md">
          + New Share Link
        </button>
      </div>

      {active.length > 0 && (
        <div className="mb-6">
          <h3 className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-3">Active Shares</h3>
          <div className="space-y-3">
            {active.map((s: Share) => (
              <div key={s.id} className="bg-white rounded-xl border border-emerald-200 p-4 flex items-center justify-between">
                <div>
                  <div className="text-sm font-semibold text-gray-900">{s.recipient_name}</div>
                  <div className="text-xs text-gray-500 mt-0.5">{s.ministries.join(", ")} &middot; {s.purpose || "No purpose specified"}</div>
                  <div className="text-[11px] text-gray-400 mt-1">
                    Expires {new Date(s.expires_at).toLocaleString()} &middot; Accessed {s.access_count}x
                    {s.one_time && " (one-time)"}
                  </div>
                </div>
                <button onClick={() => handleRevoke(s.token)}
                  className="px-3 py-1.5 bg-red-50 text-red-600 rounded-lg text-xs font-semibold hover:bg-red-100">
                  Revoke
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {expired.length > 0 && (
        <div>
          <h3 className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-3">Expired / Revoked</h3>
          <div className="space-y-2">
            {expired.map((s: Share) => (
              <div key={s.id} className="bg-gray-50 rounded-xl p-4 opacity-60">
                <div className="text-sm text-gray-700">{s.recipient_name} — {s.ministries.join(", ")}</div>
                <div className="text-[11px] text-gray-400">{s.revoked ? "Revoked" : "Expired"} &middot; Accessed {s.access_count}x</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {shares.length === 0 && (
        <div className="bg-white rounded-xl border p-12 text-center text-gray-400 text-sm">
          No share links yet. Create one to securely share your data with employers, banks, or institutions.
        </div>
      )}
    </div>
  );
}
