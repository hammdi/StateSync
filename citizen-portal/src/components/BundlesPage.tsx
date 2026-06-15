import { useState, useEffect } from "react";
import { fetchBundles, requestBundle } from "../api/client";

interface Props { cin: string; onRequested: () => void }

const iconMap: Record<string, string> = {
  briefcase: "💼", bank: "🏦", plane: "✈️", graduation: "🎓",
  building: "🏢", sunset: "🌅",
};

export default function BundlesPage({ cin, onRequested }: Props) {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [bundles, setBundles] = useState<Record<string, any>>({});
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [result, setResult] = useState<any>(null);
  const [requesting, setRequesting] = useState<string | null>(null);

  useEffect(() => {
    fetchBundles().then((d) => setBundles(d.bundles || {}));
  }, []);

  const handleRequest = async (bundleId: string) => {
    setRequesting(bundleId);
    try {
      const res = await requestBundle(bundleId, cin);
      setResult(res);
      onRequested();
    } catch { alert("Failed to request bundle"); }
    finally { setRequesting(null); }
  };

  if (result) {
    return (
      <div className="animate-fade-in max-w-xl mx-auto">
        <button onClick={() => setResult(null)} className="text-sm text-blue-600 hover:underline mb-4">&larr; Back to bundles</button>

        <div className="bg-white rounded-2xl shadow-sm border p-6 text-center">
          <div className="w-16 h-16 bg-emerald-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg className="w-8 h-8 text-emerald-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
          </div>
          <h3 className="text-lg font-bold text-gray-900">{result.bundle_name}</h3>
          <p className="text-sm text-gray-500 mt-2">
            {result.approved_instantly} document(s) ready instantly.
            {result.pending_review > 0 && ` ${result.pending_review} pending employee review.`}
          </p>
          <div className="mt-4 space-y-2 text-left">
            {/* eslint-disable-next-line @typescript-eslint/no-explicit-any */}
            {result.requests.map((r: any) => (
              <div key={r.id} className="flex items-center justify-between bg-gray-50 rounded-lg px-4 py-2 text-sm">
                <span>{r.service_name}</span>
                <span className={`text-xs font-bold px-2 py-0.5 rounded ${
                  r.status === "approved" ? "bg-emerald-100 text-emerald-700" : "bg-amber-100 text-amber-700"
                }`}>{r.status === "approved" ? "Ready" : "Pending"}</span>
              </div>
            ))}
          </div>
          <p className="text-xs text-gray-400 mt-4">Go to "My Requests" to download your documents.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="animate-fade-in">
      <div className="mb-8">
        <h2 className="text-xl font-bold text-gray-900">Document Bundles</h2>
        <p className="text-sm text-gray-500 mt-1">
          Pre-packaged document sets for common needs. One click = multiple documents.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {Object.entries(bundles).map(([id, b]) => (
          <div key={id} className="bg-white rounded-2xl border border-gray-100 p-5 hover:shadow-lg hover:border-blue-200 transition-all flex flex-col">
            <div className="flex items-center gap-3 mb-3">
              <span className="text-2xl">{iconMap[b.icon] || "📦"}</span>
              <h3 className="text-sm font-bold text-gray-900">{b.name}</h3>
            </div>
            <p className="text-xs text-gray-500 leading-relaxed flex-1">{b.description}</p>
            <div className="flex items-center justify-between mt-4 pt-3 border-t border-gray-100">
              <span className="text-[11px] text-gray-400">{b.document_count} documents</span>
              <button
                onClick={() => handleRequest(id)}
                disabled={requesting !== null}
                className="px-4 py-1.5 bg-blue-600 text-white text-xs font-semibold rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors"
              >
                {requesting === id ? "..." : "Request All"}
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
