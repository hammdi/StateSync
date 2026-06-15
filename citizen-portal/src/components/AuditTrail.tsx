import type { AuditEntry } from "../types";

interface Props {
  entries: AuditEntry[];
  onRefresh: () => void;
}

export default function AuditTrail({ entries, onRefresh }: Props) {
  return (
    <div className="animate-fade-in">
      <div className="flex items-start justify-between mb-6">
        <div>
          <h2 className="text-xl font-bold text-gray-900">Audit Trail</h2>
          <p className="text-sm text-gray-500 mt-1 max-w-lg">
            Every access to your data is recorded here. This log is immutable
            &mdash; entries can never be modified or deleted.
          </p>
        </div>
        <button
          onClick={onRefresh}
          className="px-4 py-2 bg-white shadow-sm border border-gray-200 rounded-xl text-sm text-gray-700 hover:bg-gray-50 transition-colors font-medium"
        >
          Refresh
        </button>
      </div>

      {entries.length > 0 ? (
        <div className="relative">
          {/* Timeline line */}
          <div className="absolute left-5 top-6 bottom-6 w-px bg-gray-200" />

          <div className="space-y-3">
            {entries.map((entry) => {
              const isReport = entry.purpose.includes("Error report");
              const isUpdate = entry.purpose.includes("Data update");

              const dotColor = isReport
                ? "bg-red-500"
                : isUpdate
                  ? "bg-amber-500"
                  : "bg-blue-500";

              const tagColor = isReport
                ? "bg-red-100 text-red-700"
                : isUpdate
                  ? "bg-amber-100 text-amber-700"
                  : "bg-blue-100 text-blue-700";

              const tagLabel = isReport
                ? "Error Report"
                : isUpdate
                  ? "Data Update"
                  : "Data Access";

              return (
                <div key={entry.id} className="relative flex gap-4 items-start">
                  {/* Dot */}
                  <div className="relative z-10 flex-shrink-0 w-10 h-10 rounded-full bg-white border-2 border-gray-200 flex items-center justify-center">
                    <div className={`w-3 h-3 rounded-full ${dotColor}`} />
                  </div>

                  {/* Card */}
                  <div className="flex-1 bg-white rounded-xl shadow-sm border border-gray-100 p-4 hover:shadow-md transition-shadow">
                    <div className="flex items-start justify-between gap-4">
                      <div className="min-w-0">
                        <span
                          className={`inline-block text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-md ${tagColor}`}
                        >
                          {tagLabel}
                        </span>
                        <p className="text-sm text-gray-700 mt-2 leading-relaxed">
                          {entry.purpose}
                        </p>
                      </div>
                      <time className="text-[11px] text-gray-400 whitespace-nowrap font-mono">
                        {new Date(entry.timestamp).toLocaleString()}
                      </time>
                    </div>
                    <div className="mt-3 flex items-center gap-4 text-[11px] text-gray-400">
                      <span>
                        by{" "}
                        <span className="font-mono font-medium text-gray-500">
                          {entry.accessed_by}
                        </span>
                      </span>
                      <span className="font-mono">{entry.id.slice(0, 8)}...</span>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      ) : (
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-12 text-center">
          <div className="text-gray-300 text-4xl mb-3">~</div>
          <p className="text-gray-400 text-sm">No audit entries recorded yet.</p>
        </div>
      )}
    </div>
  );
}
