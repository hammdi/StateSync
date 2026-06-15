import { useState, useEffect } from "react";
import { fetchCompleteness } from "../api/client";

interface Props { cin: string }

export default function CompletenessCard({ cin }: Props) {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [data, setData] = useState<any>(null);
  const [expanded, setExpanded] = useState(false);

  useEffect(() => {
    fetchCompleteness(cin).then(setData);
  }, [cin]);

  if (!data) return null;

  const incomplete = data.checks.filter((c: { complete: boolean }) => !c.complete);
  const scoreColor = data.score >= 80 ? "text-emerald-600" : data.score >= 50 ? "text-amber-600" : "text-red-600";
  const ringColor = data.score >= 80 ? "stroke-emerald-500" : data.score >= 50 ? "stroke-amber-500" : "stroke-red-500";

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-5">
      <div className="flex items-center gap-5">
        {/* Ring */}
        <div className="relative w-20 h-20 flex-shrink-0">
          <svg className="w-20 h-20 -rotate-90" viewBox="0 0 36 36">
            <path d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
              fill="none" stroke="#e5e7eb" strokeWidth="3" />
            <path d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
              fill="none" className={ringColor} strokeWidth="3" strokeLinecap="round"
              strokeDasharray={`${data.score}, 100`}
              style={{ transition: "stroke-dasharray 1s ease" }} />
          </svg>
          <span className={`absolute inset-0 flex items-center justify-center text-lg font-extrabold ${scoreColor}`}>
            {data.score}%
          </span>
        </div>

        <div className="flex-1">
          <div className="text-sm font-bold text-gray-900">Profile Completeness</div>
          <div className="text-xs text-gray-500 mt-0.5">
            {data.completed}/{data.total} fields verified
          </div>
          {incomplete.length > 0 && (
            <button
              onClick={() => setExpanded(!expanded)}
              className="text-xs text-blue-600 font-medium mt-2 hover:underline"
            >
              {expanded ? "Hide" : `${incomplete.length} missing items`}
            </button>
          )}
          {incomplete.length === 0 && (
            <div className="text-xs text-emerald-600 font-semibold mt-2">All fields complete!</div>
          )}
        </div>
      </div>

      {expanded && incomplete.length > 0 && (
        <div className="mt-4 pt-3 border-t border-gray-100">
          <div className="space-y-1.5">
            {incomplete.map((c: { category: string; field: string }, i: number) => (
              <div key={i} className="flex items-center gap-2 text-xs">
                <div className="w-1.5 h-1.5 rounded-full bg-red-400 flex-shrink-0" />
                <span className="text-gray-500">{c.category}:</span>
                <span className="text-gray-800 font-medium">{c.field}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
