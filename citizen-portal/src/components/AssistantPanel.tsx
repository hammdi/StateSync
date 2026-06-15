import { useState, useEffect } from "react";
import { fetchAssistant } from "../api/client";

interface Props {
  cin: string;
  open: boolean;
  onClose: () => void;
  onNavigate: (page: string) => void;
}

const priorityStyle: Record<string, string> = {
  urgent: "border-red-400 bg-red-50",
  warning: "border-amber-400 bg-amber-50",
  info: "border-blue-400 bg-blue-50",
};

const categoryIcons: Record<string, string> = {
  life: "💍", urgent: "🚨", info: "💡", finance: "💰", career: "💼",
  business: "🏢", health: "❤️", family: "👨‍👩‍👧", car: "🚗",
  alert: "⚠️", money: "💸", file: "📄", wrench: "🔧",
  heart: "❤️", gift: "🎁", shield: "🛡️", sunset: "🌅",
};

export default function AssistantPanel({ cin, open, onClose, onNavigate }: Props) {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (open && cin) {
      setLoading(true);
      fetchAssistant(cin).then(setData).finally(() => setLoading(false));
    }
  }, [open, cin]);

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex justify-end">
      {/* Backdrop */}
      <div className="absolute inset-0 bg-black/30 backdrop-blur-sm" onClick={onClose} />

      {/* Panel */}
      <div className="relative w-full max-w-md bg-white shadow-2xl flex flex-col animate-slide-in-right">
        {/* Header */}
        <div className="bg-gradient-to-r from-indigo-600 to-purple-600 text-white px-6 py-5">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-lg font-bold">Smart Assistant</h2>
              <p className="text-indigo-200 text-xs mt-0.5">Personalized insights for {data?.citizen || "you"}</p>
            </div>
            <button onClick={onClose} className="w-8 h-8 bg-white/20 rounded-full flex items-center justify-center hover:bg-white/30 text-sm">X</button>
          </div>
          {data && (
            <div className="mt-4 flex items-center gap-3">
              <div className="relative w-14 h-14">
                <svg className="w-14 h-14 -rotate-90" viewBox="0 0 36 36">
                  <path d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                    fill="none" stroke="rgba(255,255,255,0.2)" strokeWidth="3" />
                  <path d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                    fill="none" stroke="white" strokeWidth="3" strokeLinecap="round"
                    strokeDasharray={`${data.completeness}, 100`} />
                </svg>
                <span className="absolute inset-0 flex items-center justify-center text-sm font-bold">{data.completeness}%</span>
              </div>
              <div>
                <div className="text-sm font-semibold">Profile Completeness</div>
                <div className="text-indigo-200 text-xs">{data.completeness >= 80 ? "Great job!" : data.completeness >= 50 ? "Good, keep going" : "Needs attention"}</div>
              </div>
            </div>
          )}
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto px-5 py-4">
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <div className="w-8 h-8 border-2 border-indigo-200 border-t-indigo-600 rounded-full animate-spin" />
            </div>
          ) : data ? (
            <div className="space-y-6">
              {/* Reminders */}
              {data.reminders.length > 0 && (
                <div>
                  <h3 className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-3">Reminders & Alerts</h3>
                  <div className="space-y-2">
                    {/* eslint-disable-next-line @typescript-eslint/no-explicit-any */}
                    {data.reminders.map((r: any, i: number) => (
                      <div key={i} className={`border-l-4 rounded-r-lg p-3 ${priorityStyle[r.priority] || "border-gray-300 bg-gray-50"}`}>
                        <div className="flex items-start gap-2">
                          <span className="text-base">{categoryIcons[r.icon] || "📌"}</span>
                          <div className="flex-1 min-w-0">
                            <div className="text-sm font-semibold text-gray-900">{r.title}</div>
                            <div className="text-xs text-gray-600 mt-0.5">{r.message}</div>
                            {r.action && (
                              <button
                                onClick={() => { onNavigate("services"); onClose(); }}
                                className="text-xs text-blue-600 font-medium mt-1 hover:underline"
                              >
                                Take action &rarr;
                              </button>
                            )}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Suggestions */}
              {data.suggestions.length > 0 && (
                <div>
                  <h3 className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-3">Suggestions</h3>
                  <div className="space-y-2">
                    {/* eslint-disable-next-line @typescript-eslint/no-explicit-any */}
                    {data.suggestions.map((s: any, i: number) => (
                      <div key={i} className="bg-gray-50 rounded-xl p-3.5 hover:bg-gray-100 transition-colors">
                        <div className="flex items-start gap-2">
                          <span className="text-base">{categoryIcons[s.category] || "💡"}</span>
                          <div className="flex-1">
                            <div className="text-sm font-semibold text-gray-900">{s.title}</div>
                            <div className="text-xs text-gray-600 mt-0.5">{s.message}</div>
                            {s.action && (
                              <button
                                onClick={() => {
                                  if (s.action.type === "life_event") onNavigate("life-events");
                                  else if (s.action.type === "bundle") onNavigate("bundles");
                                  else onNavigate("services");
                                  onClose();
                                }}
                                className="text-xs text-indigo-600 font-medium mt-1.5 hover:underline"
                              >
                                {s.action.type === "life_event" ? "Start life event" : s.action.type === "bundle" ? "Get bundle" : "Request service"} &rarr;
                              </button>
                            )}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {data.reminders.length === 0 && data.suggestions.length === 0 && (
                <div className="text-center py-8 text-gray-400 text-sm">
                  Everything looks good! No actions needed right now.
                </div>
              )}
            </div>
          ) : null}
        </div>
      </div>

      <style>{`
        @keyframes slideInRight { from { transform: translateX(100%); } to { transform: translateX(0); } }
        .animate-slide-in-right { animation: slideInRight 0.3s ease-out; }
      `}</style>
    </div>
  );
}
