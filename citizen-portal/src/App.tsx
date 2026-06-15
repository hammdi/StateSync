import { useState, useCallback, useEffect } from "react";
import type { CitizenData, AuditEntry } from "./types";
import { fetchCitizenData, fetchAuditTrail } from "./api/client";
import { t, getDir, LANGUAGES, type Lang } from "./i18n/translations";
import Header from "./components/Header";
import SearchBar from "./components/SearchBar";
import Dashboard from "./components/Dashboard";
import CitizenDataView from "./components/CitizenData";
import AuditTrail from "./components/AuditTrail";
import ErrorReport from "./components/ErrorReport";
import ServicesPage from "./components/ServicesPage";
import RequestsPage from "./components/RequestsPage";
import EmployeePortal from "./components/EmployeePortal";
import LifeEventsPage from "./components/LifeEventsPage";
import BundlesPage from "./components/BundlesPage";
import VerifyPage from "./components/VerifyPage";
import AssistantPanel from "./components/AssistantPanel";
import DataSharingPage from "./components/DataSharingPage";
import AppointmentsPage from "./components/AppointmentsPage";
import AnalyticsPage from "./components/AnalyticsPage";

type Page = "dashboard" | "life-events" | "bundles" | "services" | "requests" | "sharing" | "appointments" | "data" | "audit" | "analytics" | "report";

export default function App() {
  const [citizen, setCitizen] = useState<CitizenData | null>(null);
  const [audit, setAudit] = useState<AuditEntry[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState<Page>("dashboard");
  const [employeeMode, setEmployeeMode] = useState(false);
  const [verifyMode, setVerifyMode] = useState(false);
  const [assistantOpen, setAssistantOpen] = useState(false);
  const [dark, setDark] = useState(() => localStorage.getItem("theme") === "dark");
  const [lang, setLang] = useState<Lang>(() => (localStorage.getItem("lang") as Lang) || "en");

  useEffect(() => {
    document.documentElement.classList.toggle("dark", dark);
    localStorage.setItem("theme", dark ? "dark" : "light");
  }, [dark]);

  useEffect(() => {
    document.documentElement.dir = getDir(lang);
    document.documentElement.lang = lang;
    localStorage.setItem("lang", lang);
  }, [lang]);

  const handleSearch = useCallback(async (cin: string) => {
    setLoading(true);
    setError(null);
    setCitizen(null);
    setAudit([]);
    setPage("dashboard");
    try {
      const [data, trail] = await Promise.all([
        fetchCitizenData(cin),
        fetchAuditTrail(cin),
      ]);
      setCitizen(data);
      setAudit(trail);
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
    } finally {
      setLoading(false);
    }
  }, []);

  const handleAuditRefresh = useCallback(async () => {
    if (!citizen) return;
    try { setAudit(await fetchAuditTrail(citizen.cin)); } catch { /* */ }
  }, [citizen]);

  const handleReset = useCallback(() => {
    setCitizen(null);
    setAudit([]);
    setError(null);
    setPage("dashboard");
  }, []);

  const handleExport = useCallback(() => {
    if (!citizen) return;
    const blob = new Blob([JSON.stringify(citizen, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `statesync-${citizen.cin}.json`;
    a.click();
    URL.revokeObjectURL(url);
  }, [citizen]);

  // ── Employee Portal ──
  if (employeeMode) {
    return <EmployeePortal onBack={() => setEmployeeMode(false)} />;
  }

  if (verifyMode) {
    return (
      <div>
        <VerifyPage />
        <div className="fixed bottom-4 left-1/2 -translate-x-1/2">
          <button onClick={() => setVerifyMode(false)}
            className="px-4 py-2 bg-white shadow-lg rounded-full text-sm text-gray-600 hover:text-gray-900 border">
            &larr; Back to Portal
          </button>
        </div>
      </div>
    );
  }

  // ── Landing page ──
  if (!citizen && !loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100 dark:from-gray-950 dark:via-gray-900 dark:to-gray-950">
        <Header />
        {/* Controls bar */}
        <div className="absolute top-4 right-4 flex items-center gap-2 z-10">
          <select value={lang} onChange={e => setLang(e.target.value as Lang)}
            className="px-2 py-1 bg-white/80 dark:bg-gray-800 border rounded-lg text-xs dark:text-gray-300" aria-label="Language">
            {LANGUAGES.map(l => <option key={l.id} value={l.id}>{l.label}</option>)}
          </select>
          <button onClick={() => setDark(!dark)} aria-label={dark ? t(lang, "light_mode") : t(lang, "dark_mode")}
            className="w-8 h-8 bg-white/80 dark:bg-gray-800 border rounded-lg flex items-center justify-center text-sm">
            {dark ? "☀" : "☾"}
          </button>
        </div>
        <main className="max-w-2xl mx-auto px-4 pt-20 pb-16">
          <div className="text-center mb-10 animate-fade-in">
            <h2 className="text-4xl font-extrabold text-gray-900 dark:text-white tracking-tight">
              {t(lang, "landing.hero")}
            </h2>
            <p className="text-lg text-gray-500 dark:text-gray-400 mt-3 leading-relaxed">
              {t(lang, "landing.sub")}
            </p>
          </div>
          <div className="animate-slide-up">
            <SearchBar onSearch={handleSearch} loading={loading} />
          </div>
          {error && (
            <div className="mt-4 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-xl text-sm">{error}</div>
          )}
          <div className="mt-6 flex justify-center gap-4 text-sm text-gray-400 dark:text-gray-500">
            <span>{t(lang, "landing.try")}</span>
            {["10000001", "10000003", "10000007"].map((cin) => (
              <button key={cin} onClick={() => handleSearch(cin)}
                className="font-mono text-blue-600 dark:text-blue-400 hover:underline">{cin}</button>
            ))}
          </div>
          <div className="mt-16 grid grid-cols-3 gap-4 stagger">
            {[
              { n: "9", key: "landing.ministries" },
              { n: "35+", key: "landing.services" },
              { n: "0", key: "landing.visits" },
            ].map((s) => (
              <div key={s.key} className="bg-white/60 dark:bg-gray-800/60 backdrop-blur-sm rounded-2xl p-6 text-center shadow-sm border border-white/80 dark:border-gray-700">
                <div className="text-3xl font-extrabold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">{s.n}</div>
                <div className="text-xs text-gray-500 dark:text-gray-400 mt-2 font-medium uppercase tracking-wider">{t(lang, s.key)}</div>
              </div>
            ))}
          </div>
          <div className="mt-12 flex justify-center gap-6">
            <button onClick={() => setVerifyMode(true)}
              className="text-xs text-blue-500 hover:text-blue-700 font-medium transition-colors">
              {t(lang, "landing.verify")}
            </button>
            <button onClick={() => setEmployeeMode(true)}
              className="text-xs text-gray-400 hover:text-gray-600 transition-colors">
              {t(lang, "landing.staff")} &rarr;
            </button>
          </div>
        </main>
      </div>
    );
  }

  // ── Loading ──
  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-950">
        <Header />
        <div className="flex items-center justify-center pt-32">
          <div className="text-center animate-fade-in">
            <div className="w-14 h-14 border-[3px] border-blue-100 border-t-blue-600 rounded-full animate-spin mx-auto" />
            <p className="text-gray-400 mt-6 text-sm">{t(lang, "loading")}</p>
          </div>
        </div>
      </div>
    );
  }

  // ── Portal ──
  const tabs: { id: Page; label: string; badge?: number }[] = [
    { id: "dashboard", label: t(lang, "tab.dashboard") },
    { id: "life-events", label: t(lang, "tab.life_events") },
    { id: "bundles", label: t(lang, "tab.bundles") },
    { id: "services", label: t(lang, "tab.services") },
    { id: "requests", label: t(lang, "tab.requests") },
    { id: "sharing", label: t(lang, "tab.sharing") },
    { id: "appointments", label: t(lang, "tab.appointments") },
    { id: "data", label: t(lang, "tab.data") },
    { id: "audit", label: t(lang, "tab.audit"), badge: audit.length },
    { id: "analytics", label: t(lang, "tab.analytics") },
    { id: "report", label: t(lang, "tab.report") },
  ];

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-950 dark:text-gray-100 transition-colors">
      <Header citizen={citizen} onReset={handleReset} onExport={handleExport} />

      <nav className="bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-800 sticky top-0 z-20 shadow-sm">
        <div className="max-w-6xl mx-auto px-4 flex gap-1 overflow-x-auto">
          {tabs.map((tab) => (
            <button key={tab.id} onClick={() => setPage(tab.id)}
              className={`relative px-4 py-3.5 text-xs font-medium whitespace-nowrap transition-colors ${
                page === tab.id ? "text-blue-600 dark:text-blue-400" : "text-gray-500 dark:text-gray-400 hover:text-gray-700"
              }`}>
              {tab.label}
              {tab.badge != null && tab.badge > 0 && (
                <span className="ml-1 text-[10px] bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400 px-1.5 py-0.5 rounded-full font-semibold">{tab.badge}</span>
              )}
              {page === tab.id && <span className="absolute bottom-0 left-2 right-2 h-0.5 bg-blue-600 rounded-full" />}
            </button>
          ))}
          <div className="flex-1" />
          <select value={lang} onChange={e => setLang(e.target.value as Lang)}
            className="px-2 py-1 bg-transparent border border-gray-200 dark:border-gray-700 rounded-lg text-[11px] dark:text-gray-300 my-auto" aria-label="Language">
            {LANGUAGES.map(l => <option key={l.id} value={l.id}>{l.label}</option>)}
          </select>
          <button onClick={() => setDark(!dark)} aria-label="Toggle theme"
            className="w-7 h-7 bg-gray-100 dark:bg-gray-800 rounded-lg flex items-center justify-center text-xs my-auto">
            {dark ? "☀" : "☾"}
          </button>
          <button onClick={() => setAssistantOpen(true)}
            className="px-3 py-1.5 bg-gradient-to-r from-indigo-500 to-purple-500 text-white text-[11px] font-bold rounded-full hover:shadow-md transition-all whitespace-nowrap my-auto">
            {t(lang, "btn.assistant")}
          </button>
          <button onClick={() => setEmployeeMode(true)}
            className="px-2 py-1.5 text-[11px] text-gray-400 hover:text-gray-600 whitespace-nowrap my-auto">
            {t(lang, "btn.staff")} &rarr;
          </button>
        </div>
      </nav>

      <main className="max-w-6xl mx-auto px-4 py-6">
        {page === "dashboard" && <Dashboard data={citizen!} auditCount={audit.length} />}
        {page === "life-events" && <LifeEventsPage cin={citizen!.cin} onStarted={() => {}} />}
        {page === "bundles" && <BundlesPage cin={citizen!.cin} onRequested={() => {}} />}
        {page === "services" && <ServicesPage cin={citizen!.cin} onRequestSubmitted={() => {}} />}
        {page === "requests" && <RequestsPage cin={citizen!.cin} />}
        {page === "sharing" && <DataSharingPage cin={citizen!.cin} />}
        {page === "appointments" && <AppointmentsPage cin={citizen!.cin} />}
        {page === "data" && <CitizenDataView data={citizen!} />}
        {page === "audit" && <AuditTrail entries={audit} onRefresh={handleAuditRefresh} />}
        {page === "analytics" && <AnalyticsPage />}
        {page === "report" && <ErrorReport cin={citizen!.cin} />}
      </main>

      <AssistantPanel
        cin={citizen!.cin}
        open={assistantOpen}
        onClose={() => setAssistantOpen(false)}
        onNavigate={(p) => setPage(p as Page)}
      />
    </div>
  );
}
