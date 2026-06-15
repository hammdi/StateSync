import { useState } from "react";

interface Props {
  onSearch: (cin: string) => void;
  loading: boolean;
}

export default function SearchBar({ onSearch, loading }: Props) {
  const [cin, setCin] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const trimmed = cin.trim();
    if (trimmed) onSearch(trimmed);
  };

  return (
    <form onSubmit={handleSubmit} className="flex gap-3">
      <input
        type="text"
        value={cin}
        onChange={(e) => setCin(e.target.value)}
        placeholder="Enter your CIN number"
        className="flex-1 px-5 py-3.5 bg-white border border-gray-200 rounded-xl text-sm
                   shadow-sm focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500
                   outline-none placeholder:text-gray-400"
        disabled={loading}
      />
      <button
        type="submit"
        disabled={loading || !cin.trim()}
        className="px-8 py-3.5 bg-gradient-to-r from-blue-600 to-indigo-600 text-white
                   text-sm font-semibold rounded-xl shadow-sm hover:shadow-md
                   disabled:opacity-50 disabled:cursor-not-allowed transition-all"
      >
        {loading ? "Searching..." : "Search"}
      </button>
    </form>
  );
}
