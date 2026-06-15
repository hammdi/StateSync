import { useState, useEffect } from "react";

const API = import.meta.env.VITE_API_URL || "http://localhost:8080";

const LABELS: Record<string, string> = {
  civil: "Civil", education: "Education", defense: "Defense", health: "Health",
  justice: "Justice", finance: "Finance", social: "Social", transport: "Transport", property: "Property",
};

export default function AnalyticsPage() {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [data, setData] = useState<any>(null);

  useEffect(() => {
    fetch(`${API}/analytics/overview`).then(r => r.json()).then(setData);
  }, []);

  if (!data) return <div className="text-center py-12 text-gray-400 text-sm">Loading analytics...</div>;

  const { totals, pending, last_24h, by_ministry } = data;

  const topCards = [
    { label: "Citizens", value: totals.citizens, color: "from-blue-500 to-blue-600" },
    { label: "Requests", value: totals.requests, color: "from-indigo-500 to-indigo-600" },
    { label: "Documents", value: totals.documents, color: "from-emerald-500 to-emerald-600" },
    { label: "Audit Log", value: totals.audit_entries, color: "from-purple-500 to-purple-600" },
    { label: "Shares", value: totals.shares, color: "from-cyan-500 to-cyan-600" },
    { label: "Appointments", value: totals.appointments, color: "from-amber-500 to-amber-600" },
  ];

  // Compute max for bar chart
  const ministryNames = Object.keys(by_ministry);
  const maxRequests = Math.max(1, ...ministryNames.map(m => {
    const stats = by_ministry[m];
    return Object.values(stats as Record<string, number>).reduce((a, b) => a + b, 0);
  }));

  return (
    <div className="animate-fade-in space-y-6">
      <div>
        <h2 className="text-xl font-bold text-gray-900">System Analytics</h2>
        <p className="text-sm text-gray-500 mt-1">Real-time overview of the StateSync platform.</p>
      </div>

      {/* Top metrics */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3 stagger">
        {topCards.map(c => (
          <div key={c.label} className="bg-white rounded-xl border p-4 shadow-sm">
            <div className="text-2xl font-bold text-gray-900">{c.value.toLocaleString()}</div>
            <div className="text-xs text-gray-500 mt-1">{c.label}</div>
            <div className={`h-1 w-8 rounded-full bg-gradient-to-r ${c.color} mt-2`} />
          </div>
        ))}
      </div>

      {/* Live indicators */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <div className="bg-amber-50 border border-amber-200 rounded-xl p-4">
          <div className="text-2xl font-bold text-amber-700">{pending.requests}</div>
          <div className="text-xs text-amber-600">Pending Requests</div>
        </div>
        <div className="bg-red-50 border border-red-200 rounded-xl p-4">
          <div className="text-2xl font-bold text-red-700">{pending.error_reports}</div>
          <div className="text-xs text-red-600">Pending Error Reports</div>
        </div>
        <div className="bg-blue-50 border border-blue-200 rounded-xl p-4">
          <div className="text-2xl font-bold text-blue-700">{last_24h.audit_entries}</div>
          <div className="text-xs text-blue-600">Audits (24h)</div>
        </div>
        <div className="bg-emerald-50 border border-emerald-200 rounded-xl p-4">
          <div className="text-2xl font-bold text-emerald-700">{last_24h.requests}</div>
          <div className="text-xs text-emerald-600">Requests (24h)</div>
        </div>
      </div>

      {/* Ministry bar chart */}
      <div className="bg-white rounded-2xl border p-6">
        <h3 className="text-sm font-bold text-gray-700 mb-4">Requests by Ministry</h3>
        <div className="space-y-3">
          {ministryNames.map(m => {
            const stats = by_ministry[m] as Record<string, number>;
            const total = Object.values(stats).reduce((a, b) => a + b, 0);
            const approved = stats.approved || 0;
            const pendingC = stats.pending || 0;
            const rejected = stats.rejected || 0;

            return (
              <div key={m} className="flex items-center gap-3">
                <div className="w-20 text-xs text-gray-600 font-medium text-right">{LABELS[m] || m}</div>
                <div className="flex-1 flex h-6 rounded-full overflow-hidden bg-gray-100">
                  {approved > 0 && <div className="bg-emerald-500" style={{ width: `${(approved / maxRequests) * 100}%` }} />}
                  {pendingC > 0 && <div className="bg-amber-400" style={{ width: `${(pendingC / maxRequests) * 100}%` }} />}
                  {rejected > 0 && <div className="bg-red-400" style={{ width: `${(rejected / maxRequests) * 100}%` }} />}
                </div>
                <div className="w-8 text-xs text-gray-500 text-right">{total}</div>
              </div>
            );
          })}
        </div>
        <div className="flex gap-4 mt-4 text-[11px] text-gray-400">
          <span className="flex items-center gap-1"><span className="w-3 h-3 rounded bg-emerald-500 inline-block" /> Approved</span>
          <span className="flex items-center gap-1"><span className="w-3 h-3 rounded bg-amber-400 inline-block" /> Pending</span>
          <span className="flex items-center gap-1"><span className="w-3 h-3 rounded bg-red-400 inline-block" /> Rejected</span>
        </div>
      </div>
    </div>
  );
}
