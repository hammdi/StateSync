import { useState, useEffect } from "react";
import type { ServiceDef, ServiceField } from "../types";
import { fetchServicesCatalog, submitServiceRequest } from "../api/client";

interface Props {
  cin: string;
  onRequestSubmitted: () => void;
}

const categoryStyle: Record<string, string> = {
  certificate: "bg-blue-100 text-blue-700",
  update: "bg-amber-100 text-amber-700",
  application: "bg-purple-100 text-purple-700",
};

export default function ServicesPage({ cin, onRequestSubmitted }: Props) {
  const [catalog, setCatalog] = useState<Record<string, ServiceDef[]>>({});
  const [labels, setLabels] = useState<Record<string, string>>({});
  const [selected, setSelected] = useState<{ ministry: string; service: ServiceDef } | null>(null);
  const [formData, setFormData] = useState<Record<string, string>>({});
  const [submitting, setSubmitting] = useState(false);
  const [success, setSuccess] = useState<string | null>(null);
  const [filter, setFilter] = useState("");

  useEffect(() => {
    fetchServicesCatalog().then((d) => {
      setCatalog(d.catalog);
      setLabels(d.labels);
    });
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selected) return;
    setSubmitting(true);
    try {
      const result = await submitServiceRequest({
        cin,
        ministry: selected.ministry,
        service_id: selected.service.id,
        details: formData,
      });
      setSuccess(
        result.status === "approved"
          ? `${selected.service.name} — approved instantly! Document generated.`
          : `${selected.service.name} — request submitted. Estimated: ${selected.service.processing}.`
      );
      setSelected(null);
      setFormData({});
      onRequestSubmitted();
    } catch {
      alert("Failed to submit request");
    } finally {
      setSubmitting(false);
    }
  };

  const lowerFilter = filter.toLowerCase();
  const filteredCatalog = Object.entries(catalog).filter(([, services]) =>
    services.some(
      (s) =>
        s.name.toLowerCase().includes(lowerFilter) ||
        s.description.toLowerCase().includes(lowerFilter),
    ),
  );

  // ── Request form modal ──
  if (selected) {
    return (
      <div className="animate-fade-in max-w-xl mx-auto">
        <button onClick={() => setSelected(null)} className="text-sm text-blue-600 hover:underline mb-4 block">
          &larr; Back to services
        </button>
        <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
          <span className={`text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-md ${categoryStyle[selected.service.category] || "bg-gray-100"}`}>
            {selected.service.category}
          </span>
          <h2 className="text-xl font-bold text-gray-900 mt-2">{selected.service.name}</h2>
          <p className="text-sm text-gray-500 mt-1">{selected.service.description}</p>
          <p className="text-xs text-gray-400 mt-1">Ministry of {labels[selected.ministry]} &middot; Processing: {selected.service.processing}</p>

          <form onSubmit={handleSubmit} className="mt-6 space-y-4">
            {selected.service.requires.length === 0 && (
              <p className="text-sm text-gray-500 bg-gray-50 rounded-lg p-3">No additional information required.</p>
            )}
            {selected.service.requires.map((f: ServiceField) => (
              <div key={f.field}>
                <label className="block text-sm font-medium text-gray-700 mb-1">{f.label}</label>
                {f.type === "select" ? (
                  <select
                    value={formData[f.field] || ""}
                    onChange={(e) => setFormData({ ...formData, [f.field]: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-200 rounded-xl text-sm bg-gray-50"
                    required
                  >
                    <option value="">Select...</option>
                    {f.options?.map((o) => <option key={o} value={o}>{o}</option>)}
                  </select>
                ) : f.type === "textarea" ? (
                  <textarea
                    value={formData[f.field] || ""}
                    onChange={(e) => setFormData({ ...formData, [f.field]: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-200 rounded-xl text-sm bg-gray-50"
                    rows={3} required
                  />
                ) : (
                  <input
                    type={f.type === "number" ? "number" : f.type === "date" ? "date" : "text"}
                    value={formData[f.field] || ""}
                    onChange={(e) => setFormData({ ...formData, [f.field]: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-200 rounded-xl text-sm bg-gray-50"
                    required
                  />
                )}
              </div>
            ))}
            <button
              type="submit"
              disabled={submitting}
              className="w-full py-3 bg-gradient-to-r from-blue-600 to-indigo-600 text-white font-semibold rounded-xl hover:shadow-md disabled:opacity-50 transition-all"
            >
              {submitting ? "Submitting..." : selected.service.auto_approve ? "Request & Get Document Instantly" : "Submit Request"}
            </button>
          </form>
        </div>
      </div>
    );
  }

  return (
    <div className="animate-fade-in">
      {success && (
        <div className="mb-6 bg-emerald-50 border border-emerald-200 text-emerald-800 rounded-xl px-4 py-3 flex items-center justify-between">
          <span className="text-sm">{success}</span>
          <button onClick={() => setSuccess(null)} className="text-emerald-600 text-xs font-medium">Dismiss</button>
        </div>
      )}

      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-xl font-bold text-gray-900">Government Services</h2>
          <p className="text-sm text-gray-500 mt-1">Request documents, certificates, and updates — no ministry visit needed.</p>
        </div>
      </div>

      <input
        type="text"
        placeholder="Search services..."
        value={filter}
        onChange={(e) => setFilter(e.target.value)}
        className="w-full px-4 py-2.5 border border-gray-200 rounded-xl text-sm mb-6 bg-white focus:ring-2 focus:ring-blue-500/20 outline-none"
      />

      <div className="space-y-8">
        {filteredCatalog.map(([ministry, services]) => {
          const filtered = services.filter(
            (s) => s.name.toLowerCase().includes(lowerFilter) || s.description.toLowerCase().includes(lowerFilter),
          );
          if (!filtered.length) return null;
          return (
            <div key={ministry}>
              <h3 className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-3">
                {labels[ministry] || ministry}
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {filtered.map((s) => (
                  <button
                    key={s.id}
                    onClick={() => { setSelected({ ministry, service: s }); setFormData({}); setSuccess(null); }}
                    className="text-left bg-white rounded-xl border border-gray-100 p-4 hover:shadow-md hover:border-blue-200 transition-all group"
                  >
                    <div className="flex items-start justify-between">
                      <h4 className="text-sm font-semibold text-gray-900 group-hover:text-blue-600 transition-colors">
                        {s.name}
                      </h4>
                      <span className={`text-[10px] font-bold uppercase px-2 py-0.5 rounded-md flex-shrink-0 ml-2 ${categoryStyle[s.category] || ""}`}>
                        {s.category}
                      </span>
                    </div>
                    <p className="text-xs text-gray-500 mt-1">{s.description}</p>
                    <div className="flex items-center gap-3 mt-2.5 text-[11px] text-gray-400">
                      <span>{s.processing}</span>
                      {s.auto_approve && <span className="text-emerald-600 font-semibold">Instant</span>}
                    </div>
                  </button>
                ))}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
