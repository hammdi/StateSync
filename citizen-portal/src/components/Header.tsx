import type { CitizenData } from "../types";

interface Props {
  citizen?: CitizenData | null;
  onReset?: () => void;
  onExport?: () => void;
}

export default function Header({ citizen, onReset, onExport }: Props) {
  return (
    <header className="bg-gradient-to-r from-blue-700 via-blue-800 to-indigo-900 text-white shadow-lg">
      <div className="max-w-6xl mx-auto px-4 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-white/15 backdrop-blur rounded-xl flex items-center justify-center text-lg font-black tracking-tighter">
            S
          </div>
          <div>
            <h1 className="text-xl font-bold tracking-tight leading-tight">StateSync</h1>
            <p className="text-blue-300 text-[11px] leading-tight">Citizen Data Portal</p>
          </div>
        </div>
        {citizen && (
          <div className="flex items-center gap-3">
            <div className="text-right hidden sm:block">
              <div className="text-sm font-semibold">{citizen.full_name}</div>
              <div className="text-blue-300 text-xs font-mono">CIN {citizen.cin}</div>
            </div>
            <div className="flex gap-2">
              {onExport && (
                <button
                  onClick={onExport}
                  className="px-3 py-1.5 bg-white/10 hover:bg-white/20 rounded-lg text-xs font-medium transition-colors"
                >
                  Export JSON
                </button>
              )}
              {onReset && (
                <button
                  onClick={onReset}
                  className="px-3 py-1.5 bg-white/10 hover:bg-white/20 rounded-lg text-xs font-medium transition-colors"
                >
                  New Search
                </button>
              )}
            </div>
          </div>
        )}
      </div>
    </header>
  );
}
