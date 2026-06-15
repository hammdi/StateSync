import { useState } from "react";
import { submitErrorReport } from "../api/client";

interface Props {
  cin: string;
}

const MINISTRIES = [
  { value: "civil", label: "Civil Status" },
  { value: "education", label: "Education" },
  { value: "defense", label: "Defense" },
  { value: "health", label: "Health" },
  { value: "justice", label: "Justice" },
  { value: "finance", label: "Finance" },
  { value: "social", label: "Social Affairs" },
  { value: "interior", label: "Interior" },
  { value: "transport", label: "Transport" },
  { value: "commerce", label: "Commerce" },
  { value: "property", label: "Property" },
  { value: "employment", label: "Employment" },
];

export default function ErrorReport({ cin }: Props) {
  const [ministry, setMinistry] = useState("civil");
  const [field, setField] = useState("");
  const [message, setMessage] = useState("");
  const [status, setStatus] = useState<"idle" | "sending" | "sent" | "error">(
    "idle",
  );

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setStatus("sending");
    try {
      await submitErrorReport(cin, { ministry, field, message });
      setStatus("sent");
      setField("");
      setMessage("");
    } catch {
      setStatus("error");
    }
  };

  if (status === "sent") {
    return (
      <div className="animate-fade-in max-w-xl mx-auto mt-8">
        <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-10 text-center">
          <div className="w-16 h-16 bg-emerald-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg className="w-8 h-8 text-emerald-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
          </div>
          <h3 className="text-lg font-bold text-gray-900">Report Submitted</h3>
          <p className="text-sm text-gray-500 mt-2">
            Your error report has been recorded in the audit trail and will be
            reviewed by the relevant ministry.
          </p>
          <button
            onClick={() => setStatus("idle")}
            className="mt-6 px-5 py-2 bg-gray-100 hover:bg-gray-200 rounded-xl text-sm font-medium transition-colors"
          >
            Submit Another Report
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="animate-fade-in max-w-xl mx-auto">
      <div className="mb-6">
        <h2 className="text-xl font-bold text-gray-900">Report an Error</h2>
        <p className="text-sm text-gray-500 mt-1">
          If any of your data is incorrect, submit a correction request here.
          Your report will be logged in the immutable audit trail.
        </p>
      </div>

      <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
        <form onSubmit={handleSubmit} className="space-y-5">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1.5">
              Ministry
            </label>
            <select
              value={ministry}
              onChange={(e) => setMinistry(e.target.value)}
              className="w-full px-4 py-2.5 border border-gray-200 rounded-xl text-sm
                         focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 outline-none
                         bg-gray-50 hover:bg-gray-100 transition-colors"
            >
              {MINISTRIES.map((m) => (
                <option key={m.value} value={m.value}>
                  {m.label}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1.5">
              Field with error
            </label>
            <input
              type="text"
              value={field}
              onChange={(e) => setField(e.target.value)}
              placeholder="e.g., address, marital_status, blood_type"
              className="w-full px-4 py-2.5 border border-gray-200 rounded-xl text-sm
                         focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 outline-none
                         bg-gray-50 placeholder:text-gray-400"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1.5">
              What is incorrect?
            </label>
            <textarea
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              placeholder="Describe the error and provide the correct information..."
              className="w-full px-4 py-2.5 border border-gray-200 rounded-xl text-sm
                         focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 outline-none
                         bg-gray-50 placeholder:text-gray-400 resize-none"
              rows={4}
              required
            />
          </div>

          <div className="flex items-center gap-3 pt-2">
            <button
              type="submit"
              disabled={status === "sending"}
              className="px-6 py-2.5 bg-red-600 text-white text-sm font-semibold rounded-xl
                         hover:bg-red-700 disabled:opacity-50 transition-colors shadow-sm"
            >
              {status === "sending" ? "Submitting..." : "Submit Report"}
            </button>
            {status === "error" && (
              <p className="text-red-600 text-sm">
                Submission failed. Please try again.
              </p>
            )}
          </div>
        </form>
      </div>
    </div>
  );
}
