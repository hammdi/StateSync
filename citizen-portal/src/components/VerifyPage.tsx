import { useState } from "react";
import { verifyDocument } from "../api/client";

export default function VerifyPage() {
  const [reference, setReference] = useState("");
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleVerify = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!reference.trim()) return;
    setLoading(true);
    setError("");
    setResult(null);
    try {
      const res = await verifyDocument(reference.trim());
      setResult(res);
    } catch {
      setError("Failed to verify. Check the reference number.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 flex flex-col items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <div className="w-14 h-14 bg-slate-800 rounded-2xl flex items-center justify-center text-white text-xl font-bold mx-auto">S</div>
          <h1 className="text-2xl font-bold text-gray-900 mt-4">Document Verification</h1>
          <p className="text-sm text-gray-500 mt-2">Enter a document reference number or scan the QR code to verify authenticity.</p>
        </div>

        <form onSubmit={handleVerify} className="flex gap-2">
          <input
            type="text"
            value={reference}
            onChange={(e) => setReference(e.target.value)}
            placeholder="e.g. CIVIL-10000003-20260615..."
            className="flex-1 px-4 py-3 border border-gray-200 rounded-xl text-sm bg-white focus:ring-2 focus:ring-blue-500/20 outline-none font-mono"
          />
          <button type="submit" disabled={loading}
            className="px-6 py-3 bg-slate-800 text-white rounded-xl text-sm font-semibold hover:bg-slate-700 disabled:opacity-50">
            {loading ? "..." : "Verify"}
          </button>
        </form>

        {error && <p className="text-red-600 text-sm mt-4 text-center">{error}</p>}

        {result && (
          <div className="mt-6 animate-fade-in">
            {result.valid ? (
              <div className="bg-white rounded-2xl border-2 border-emerald-400 p-6 text-center shadow-lg">
                <div className="w-20 h-20 bg-emerald-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <svg className="w-10 h-10 text-emerald-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M5 13l4 4L19 7" />
                  </svg>
                </div>
                <div className="text-emerald-700 text-xl font-black uppercase tracking-wider">Authentic</div>
                <p className="text-sm text-gray-500 mt-2">This document is genuine and valid.</p>

                <div className="mt-6 text-left space-y-2 bg-gray-50 rounded-xl p-4">
                  <Row label="Document" value={result.document.title} />
                  <Row label="Ministry" value={result.document.ministry_label} />
                  <Row label="Citizen" value={result.document.citizen_name} />
                  <Row label="CIN" value={result.document.cin_masked} />
                  <Row label="Issued" value={new Date(result.document.issued).toLocaleDateString()} />
                  <Row label="Valid Until" value={result.document.valid_until} />
                  <Row label="Reference" value={result.document.reference} mono />
                </div>
              </div>
            ) : result.expired ? (
              <div className="bg-white rounded-2xl border-2 border-amber-400 p-6 text-center shadow-lg">
                <div className="w-20 h-20 bg-amber-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <svg className="w-10 h-10 text-amber-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M12 9v2m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <div className="text-amber-700 text-xl font-black uppercase tracking-wider">Expired</div>
                <p className="text-sm text-gray-500 mt-2">This document was valid but has expired.</p>
                <div className="mt-4 text-left space-y-2 bg-gray-50 rounded-xl p-4">
                  <Row label="Document" value={result.document.title} />
                  <Row label="Expired" value={result.document.valid_until} />
                </div>
              </div>
            ) : (
              <div className="bg-white rounded-2xl border-2 border-red-400 p-6 text-center shadow-lg">
                <div className="w-20 h-20 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <svg className="w-10 h-10 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </div>
                <div className="text-red-700 text-xl font-black uppercase tracking-wider">Invalid</div>
                <p className="text-sm text-gray-500 mt-2">This reference number was not found. The document may be forged.</p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

function Row({ label, value, mono }: { label: string; value: string; mono?: boolean }) {
  return (
    <div className="flex justify-between text-sm">
      <span className="text-gray-500">{label}</span>
      <span className={`text-gray-900 font-medium ${mono ? "font-mono text-xs" : ""}`}>{value}</span>
    </div>
  );
}
