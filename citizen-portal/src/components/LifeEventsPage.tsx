import { useState, useEffect } from "react";
import { fetchLifeEvents, startLifeEvent } from "../api/client";

interface Props { cin: string; onStarted: () => void }

const phaseColors: Record<string, string> = {
  preparation: "bg-blue-500", registration: "bg-indigo-500", completion: "bg-emerald-500",
  health: "bg-rose-500", benefits: "bg-purple-500", clearance: "bg-amber-500",
  calculation: "bg-cyan-500", tax: "bg-green-500", documentation: "bg-slate-500",
  enrollment: "bg-violet-500", verification: "bg-teal-500", inheritance: "bg-orange-500",
  registry: "bg-pink-500",
};

const iconMap: Record<string, string> = {
  rings: "💍", baby: "👶", university: "🎓", "rocking-chair": "🏖️",
  rocket: "🚀", house: "🏠", candle: "🕯️",
};

export default function LifeEventsPage({ cin, onStarted }: Props) {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [events, setEvents] = useState<Record<string, any>>({});
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [result, setResult] = useState<any>(null);
  const [starting, setStarting] = useState<string | null>(null);

  useEffect(() => {
    fetchLifeEvents().then((d) => setEvents(d.events || {}));
  }, []);

  const handleStart = async (eventId: string) => {
    setStarting(eventId);
    try {
      const res = await startLifeEvent(eventId, cin);
      setResult(res);
      onStarted();
    } catch { alert("Failed to start life event"); }
    finally { setStarting(null); }
  };

  // ── Result view (after starting) ──
  if (result) {
    return (
      <div className="animate-fade-in max-w-2xl mx-auto">
        <button onClick={() => setResult(null)} className="text-sm text-blue-600 hover:underline mb-4">&larr; Back to life events</button>

        <div className="bg-white rounded-2xl shadow-sm border p-6 mb-6">
          <h2 className="text-xl font-bold text-gray-900">{result.event_name}</h2>
          <div className="flex items-center gap-4 mt-3">
            <div className="flex-1 bg-gray-200 rounded-full h-3 overflow-hidden">
              <div className="bg-gradient-to-r from-blue-500 to-emerald-500 h-full rounded-full transition-all" style={{ width: `${result.progress_percent}%` }} />
            </div>
            <span className="text-sm font-bold text-gray-700">{result.progress_percent}%</span>
          </div>
          <p className="text-sm text-gray-500 mt-2">
            {result.completed}/{result.total_steps} steps completed instantly.
            {result.pending > 0 && ` ${result.pending} pending employee review.`}
          </p>
        </div>

        <div className="space-y-3">
          {/* eslint-disable-next-line @typescript-eslint/no-explicit-any */}
          {result.steps.map((step: any) => (
            <div key={step.order} className="bg-white rounded-xl border p-4 flex items-center gap-4">
              <div className={`w-8 h-8 rounded-full flex items-center justify-center text-white text-xs font-bold ${
                step.request.status === "approved" ? "bg-emerald-500" : "bg-amber-400"
              }`}>
                {step.request.status === "approved" ? "✓" : step.order}
              </div>
              <div className="flex-1">
                <div className="text-sm font-semibold text-gray-900">{step.label}</div>
                <div className="flex items-center gap-2 mt-0.5">
                  <span className={`text-[10px] px-2 py-0.5 rounded-full text-white ${phaseColors[step.phase] || "bg-gray-400"}`}>
                    {step.phase}
                  </span>
                  <span className="text-xs text-gray-500">{step.request.ministry_label}</span>
                </div>
              </div>
              <span className={`text-xs font-bold px-2 py-1 rounded-lg ${
                step.request.status === "approved" ? "bg-emerald-100 text-emerald-700" : "bg-amber-100 text-amber-700"
              }`}>
                {step.request.status === "approved" ? "Done" : "Pending"}
              </span>
            </div>
          ))}
        </div>

        <p className="text-xs text-gray-400 text-center mt-6">
          Check "My Requests" tab to download documents and track pending approvals.
        </p>
      </div>
    );
  }

  return (
    <div className="animate-fade-in">
      <div className="mb-8">
        <h2 className="text-xl font-bold text-gray-900">Life Events</h2>
        <p className="text-sm text-gray-500 mt-1">
          Tell us what's happening in your life. We handle ALL the paperwork across every ministry — automatically.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {Object.entries(events).map(([id, ev]) => (
          <div key={id} className="bg-white rounded-2xl border border-gray-100 p-6 hover:shadow-lg hover:border-blue-200 transition-all group">
            <div className="flex items-start gap-4">
              <div className="text-3xl">{iconMap[ev.icon] || "📋"}</div>
              <div className="flex-1">
                <h3 className="text-base font-bold text-gray-900 group-hover:text-blue-600 transition-colors">{ev.name}</h3>
                <p className="text-xs text-gray-500 mt-1 leading-relaxed">{ev.description}</p>
                <div className="flex items-center justify-between mt-4">
                  <span className="text-[11px] text-gray-400">{ev.steps} steps across ministries</span>
                  <button
                    onClick={() => handleStart(id)}
                    disabled={starting !== null}
                    className="px-4 py-1.5 bg-gradient-to-r from-blue-600 to-indigo-600 text-white text-xs font-semibold rounded-lg
                               hover:shadow-md disabled:opacity-50 transition-all"
                  >
                    {starting === id ? "Starting..." : "Start"}
                  </button>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
