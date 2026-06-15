import { useState, useEffect, useCallback } from "react";

const API = import.meta.env.VITE_API_URL || "http://localhost:8080";

interface Props { cin: string }

export default function AppointmentsPage({ cin }: Props) {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [slots, setSlots] = useState<any[]>([]);
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [myAppts, setMyAppts] = useState<any[]>([]);
  const [ministry, setMinistry] = useState("");
  const [booking, setBooking] = useState<string | null>(null);
  const [purpose, setPurpose] = useState("");
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [confirmation, setConfirmation] = useState<any>(null);

  const loadSlots = useCallback(async () => {
    const res = await fetch(`${API}/appointments/slots?ministry=${ministry}`);
    if (res.ok) setSlots(await res.json());
  }, [ministry]);

  const loadAppts = useCallback(async () => {
    const res = await fetch(`${API}/appointments/${cin}`);
    if (res.ok) setMyAppts(await res.json());
  }, [cin]);

  useEffect(() => { loadSlots(); loadAppts(); }, [loadSlots, loadAppts]);

  const handleBook = async (slotId: string) => {
    const res = await fetch(`${API}/appointments`, {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ cin, slot_id: slotId, purpose }),
    });
    if (res.ok) {
      setConfirmation(await res.json());
      setBooking(null);
      setPurpose("");
      loadSlots();
      loadAppts();
    }
  };

  const handleCancel = async (id: string) => {
    await fetch(`${API}/appointments/${cin}/${id}`, { method: "DELETE" });
    loadAppts();
    loadSlots();
  };

  // Group slots by date
  const byDate: Record<string, typeof slots> = {};
  slots.forEach(s => { byDate[s.date] = byDate[s.date] || []; byDate[s.date].push(s); });

  if (confirmation) {
    return (
      <div className="animate-fade-in max-w-md mx-auto mt-4">
        <div className="bg-white rounded-2xl border-2 border-emerald-400 p-8 text-center shadow-lg">
          <div className="w-16 h-16 bg-emerald-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg className="w-8 h-8 text-emerald-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
          </div>
          <h3 className="text-lg font-bold text-gray-900">Appointment Confirmed</h3>
          <div className="mt-4 bg-gray-50 rounded-xl p-4 text-left text-sm space-y-2">
            <div className="flex justify-between"><span className="text-gray-500">Reference</span><span className="font-mono font-bold">{confirmation.reference}</span></div>
            <div className="flex justify-between"><span className="text-gray-500">Location</span><span>{confirmation.location}</span></div>
            <div className="flex justify-between"><span className="text-gray-500">Date</span><span>{confirmation.date}</span></div>
            <div className="flex justify-between"><span className="text-gray-500">Time</span><span>{confirmation.time_start} - {confirmation.time_end}</span></div>
          </div>
          <p className="text-xs text-gray-400 mt-4">Show your reference number at the ministry office.</p>
          <button onClick={() => setConfirmation(null)} className="mt-4 px-6 py-2 bg-gray-100 rounded-xl text-sm font-medium hover:bg-gray-200">Done</button>
        </div>
      </div>
    );
  }

  return (
    <div className="animate-fade-in">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-xl font-bold text-gray-900">Appointments</h2>
          <p className="text-sm text-gray-500 mt-1">Book an appointment when physical presence is required.</p>
        </div>
      </div>

      {/* My appointments */}
      {myAppts.length > 0 && (
        <div className="mb-8">
          <h3 className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-3">My Appointments</h3>
          <div className="space-y-2">
            {myAppts.map(a => (
              <div key={a.id} className={`bg-white rounded-xl border p-4 flex items-center justify-between ${a.status === "cancelled" ? "opacity-50" : ""}`}>
                <div>
                  <div className="text-sm font-semibold">{a.purpose}</div>
                  <div className="text-xs text-gray-500">{a.location} - {a.date} at {a.time_start}</div>
                  <div className="text-[11px] font-mono text-gray-400">Ref: {a.reference}</div>
                </div>
                {a.status === "confirmed" && (
                  <button onClick={() => handleCancel(a.id)} className="px-3 py-1 bg-red-50 text-red-600 rounded-lg text-xs font-semibold">Cancel</button>
                )}
                {a.status === "cancelled" && <span className="text-xs text-gray-400">Cancelled</span>}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Filter */}
      <div className="mb-4">
        <select value={ministry} onChange={e => setMinistry(e.target.value)}
          className="px-3 py-2 border rounded-xl text-sm bg-white">
          <option value="">All ministries</option>
          <option value="civil">Civil Status</option>
          <option value="transport">Transport</option>
          <option value="justice">Justice</option>
        </select>
      </div>

      {/* Slots by date */}
      {Object.entries(byDate).length === 0 && (
        <div className="bg-white rounded-xl border p-12 text-center text-gray-400 text-sm">No available slots.</div>
      )}
      {Object.entries(byDate).map(([date, dateSlots]) => (
        <div key={date} className="mb-6">
          <h3 className="text-sm font-bold text-gray-700 mb-2">{new Date(date + "T00:00:00").toLocaleDateString(undefined, { weekday: "long", month: "long", day: "numeric" })}</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
            {dateSlots.map(s => (
              <div key={s.id} className="bg-white rounded-xl border p-3 text-center hover:border-blue-400 hover:shadow-sm transition-all">
                <div className="text-xs text-gray-500 capitalize">{s.ministry}</div>
                <div className="text-sm font-bold text-gray-900 mt-1">{s.time_start} - {s.time_end}</div>
                <div className="text-[11px] text-gray-400">{s.available} spot{s.available > 1 ? "s" : ""}</div>
                {booking === s.id ? (
                  <div className="mt-2">
                    <input type="text" placeholder="Purpose..." value={purpose} onChange={e => setPurpose(e.target.value)}
                      className="w-full px-2 py-1 border rounded text-xs mb-1" />
                    <div className="flex gap-1">
                      <button onClick={() => handleBook(s.id)} disabled={!purpose}
                        className="flex-1 px-2 py-1 bg-blue-600 text-white rounded text-xs disabled:opacity-50">Confirm</button>
                      <button onClick={() => setBooking(null)} className="px-2 py-1 bg-gray-100 rounded text-xs">X</button>
                    </div>
                  </div>
                ) : (
                  <button onClick={() => setBooking(s.id)} className="mt-2 px-3 py-1 bg-blue-50 text-blue-700 rounded-lg text-xs font-semibold hover:bg-blue-100">Book</button>
                )}
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}
