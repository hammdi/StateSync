import { useState, useEffect, useCallback } from "react";
import type { ServiceRequest, DocumentFull } from "../types";
import { fetchRequests, fetchDocument, getDocumentPdfUrl } from "../api/client";

interface Props {
  cin: string;
}

const statusStyle: Record<string, string> = {
  pending: "bg-amber-100 text-amber-700",
  approved: "bg-emerald-100 text-emerald-700",
  rejected: "bg-red-100 text-red-700",
};

export default function RequestsPage({ cin }: Props) {
  const [requests, setRequests] = useState<ServiceRequest[]>([]);
  const [doc, setDoc] = useState<DocumentFull | null>(null);
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    setLoading(true);
    try { setRequests(await fetchRequests(cin)); } catch { /* */ }
    setLoading(false);
  }, [cin]);

  useEffect(() => { load(); }, [load]);

  const openDoc = async (docId: string) => {
    try {
      const d = await fetchDocument(cin, docId);
      setDoc(d);
    } catch { alert("Failed to load document"); }
  };

  // ── Document Preview ──
  if (doc) {
    const c = doc.content;
    return (
      <div className="animate-fade-in">
        <button onClick={() => setDoc(null)} className="text-sm text-blue-600 hover:underline mb-4">&larr; Back to requests</button>
        <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-8 max-w-2xl mx-auto print:shadow-none print:border-none print:p-0" id="document-print">
          {/* Header */}
          <div className="text-center border-b-2 border-gray-800 pb-4 mb-6">
            <div className="text-xs font-bold uppercase tracking-[0.3em] text-gray-500">{c.header.country}</div>
            <div className="text-sm font-bold uppercase tracking-wider text-gray-700 mt-1">{c.header.ministry}</div>
            <div className="text-[10px] text-gray-400 mt-1">{c.header.emblem}</div>
          </div>

          <h1 className="text-xl font-bold text-center text-gray-900 mb-6">{c.title}</h1>

          <div className="text-xs text-gray-500 mb-6 flex justify-between">
            <span>Ref: <span className="font-mono font-medium">{c.reference}</span></span>
            <span>Issued: {c.issued_date}</span>
          </div>

          {/* Sections */}
          <div className="space-y-5">
            {c.sections.map((sec, i) => (
              <div key={i}>
                <h3 className="text-xs font-bold uppercase tracking-wider text-gray-500 mb-2">{sec.heading}</h3>
                {sec.fields && (
                  <div className="space-y-1">
                    {sec.fields.map(([label, value], j) => (
                      <div key={j} className="flex text-sm">
                        <span className="text-gray-500 w-40 flex-shrink-0">{label}:</span>
                        <span className="text-gray-900 font-medium">{value}</span>
                      </div>
                    ))}
                  </div>
                )}
                {sec.text && <p className="text-sm text-gray-700 leading-relaxed">{sec.text}</p>}
                {sec.list && (
                  <ul className="list-disc list-inside text-sm text-gray-700 space-y-1">
                    {sec.list.map((item, j) => <li key={j}>{item}</li>)}
                  </ul>
                )}
              </div>
            ))}
          </div>

          {c.valid_until && (
            <div className="mt-6 text-xs text-gray-500">Valid until: <span className="font-medium">{c.valid_until}</span></div>
          )}

          {/* Footer */}
          <div className="mt-8 pt-4 border-t border-gray-200">
            <p className="text-[10px] text-gray-400 leading-relaxed">{c.footer}</p>
            <div className="mt-2 text-[10px] text-gray-400 font-mono">{c.verification_url}</div>
          </div>

          {/* Signature area */}
          <div className="mt-8 flex justify-end">
            <div className="text-center">
              <div className="w-32 border-b border-gray-400 mb-1" />
              <div className="text-[10px] text-gray-500">Authorized Signature</div>
            </div>
          </div>
        </div>
        <div className="flex justify-center gap-3 mt-6 print:hidden">
          <a
            href={getDocumentPdfUrl(cin, doc.id)}
            target="_blank"
            rel="noopener noreferrer"
            className="px-6 py-2.5 bg-red-600 text-white rounded-xl text-sm font-semibold hover:bg-red-700 inline-flex items-center gap-2"
          >
            Download PDF
          </a>
          <button onClick={() => window.print()} className="px-6 py-2.5 bg-blue-600 text-white rounded-xl text-sm font-semibold hover:bg-blue-700">
            Print
          </button>
          <button onClick={() => setDoc(null)} className="px-6 py-2.5 bg-gray-100 text-gray-700 rounded-xl text-sm font-semibold hover:bg-gray-200">
            Close
          </button>
        </div>
      </div>
    );
  }

  if (loading) return <div className="text-center py-12 text-gray-400 text-sm">Loading requests...</div>;

  return (
    <div className="animate-fade-in">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-xl font-bold text-gray-900">My Requests</h2>
          <p className="text-sm text-gray-500 mt-1">Track all your service requests and download documents.</p>
        </div>
        <button onClick={load} className="px-4 py-2 bg-white border border-gray-200 rounded-xl text-sm text-gray-600 hover:bg-gray-50">Refresh</button>
      </div>

      {requests.length === 0 ? (
        <div className="bg-white rounded-xl border border-gray-100 p-12 text-center">
          <p className="text-gray-400">No requests yet. Go to Services to submit your first request.</p>
        </div>
      ) : (
        <div className="space-y-3">
          {requests.map((r) => (
            <div key={r.id} className="bg-white rounded-xl border border-gray-100 p-5 hover:shadow-sm transition-shadow">
              <div className="flex items-start justify-between">
                <div>
                  <div className="flex items-center gap-2">
                    <h3 className="text-sm font-semibold text-gray-900">{r.service_name}</h3>
                    <span className={`text-[10px] font-bold uppercase px-2 py-0.5 rounded-md ${statusStyle[r.status]}`}>{r.status}</span>
                  </div>
                  <p className="text-xs text-gray-500 mt-1">{r.ministry_label}</p>
                </div>
                <time className="text-[11px] text-gray-400">{new Date(r.submitted_at).toLocaleDateString()}</time>
              </div>
              {r.response_note && (
                <p className="text-xs text-gray-600 mt-2 bg-gray-50 rounded-lg px-3 py-2">{r.response_note}</p>
              )}
              {r.processed_by && (
                <p className="text-[11px] text-gray-400 mt-1">Processed by {r.processed_by}{r.processed_at ? ` on ${new Date(r.processed_at).toLocaleDateString()}` : ""}</p>
              )}
              {r.document_id && (
                <div className="mt-3 flex gap-2">
                  <button
                    onClick={() => openDoc(r.document_id!)}
                    className="px-4 py-1.5 bg-blue-50 text-blue-700 rounded-lg text-xs font-semibold hover:bg-blue-100 transition-colors"
                  >
                    View Document
                  </button>
                  <a
                    href={getDocumentPdfUrl(r.cin, r.document_id!)}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="px-4 py-1.5 bg-red-50 text-red-700 rounded-lg text-xs font-semibold hover:bg-red-100 transition-colors"
                  >
                    Download PDF
                  </a>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
