import { useMemo } from "react";
import type { CitizenData, ServiceError } from "../types";
import CompletenessCard from "./CompletenessCard";

interface Props {
  data: CitizenData;
  auditCount: number;
}

function isError(obj: unknown): obj is ServiceError {
  return typeof obj === "object" && obj !== null && "error" in obj;
}

function get(ministry: unknown) {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  return ministry && !isError(ministry) ? (ministry as any) : null;
}

interface Alert {
  type: "warning" | "danger" | "success" | "info";
  title: string;
  message: string;
}

export default function Dashboard({ data, auditCount }: Props) {
  const m = data.ministries;

  const stats = useMemo(() => {
    const active = Object.values(m).filter((v) => v && !isError(v)).length;
    return {
      activeMinistries: active,
      vehicles: get(m.transport)?.vehicles?.length || 0,
      properties: get(m.property)?.properties?.length || 0,
      businesses: get(m.commerce)?.businesses?.length || 0,
      benefits: get(m.social)?.benefits?.length || 0,
    };
  }, [m]);

  const alerts = useMemo(() => {
    const result: Alert[] = [];
    const today = Date.now();

    const interior = get(m.interior);
    if (interior?.passport_expiry) {
      const days = Math.floor(
        (new Date(interior.passport_expiry).getTime() - today) / 86400000,
      );
      if (days < 0)
        result.push({
          type: "danger",
          title: "Passport Expired",
          message: `Expired on ${interior.passport_expiry}. Renew immediately.`,
        });
      else if (days < 180)
        result.push({
          type: "warning",
          title: "Passport Expiring Soon",
          message: `Expires in ${days} days (${interior.passport_expiry}).`,
        });
    }

    if (interior?.permit_expiry) {
      const days = Math.floor(
        (new Date(interior.permit_expiry).getTime() - today) / 86400000,
      );
      if (days > 0 && days < 180)
        result.push({
          type: "warning",
          title: "Residence Permit",
          message: `Expires in ${days} days.`,
        });
    }

    const transport = get(m.transport);
    if (transport?.license_expiry) {
      const days = Math.floor(
        (new Date(transport.license_expiry).getTime() - today) / 86400000,
      );
      if (days < 0)
        result.push({
          type: "danger",
          title: "License Expired",
          message: `Expired on ${transport.license_expiry}.`,
        });
      else if (days < 180)
        result.push({
          type: "warning",
          title: "License Expiring",
          message: `Expires in ${days} days.`,
        });
    }

    const finance = get(m.finance);
    if (finance?.tax_status && finance.tax_status !== "Up to date")
      result.push({
        type: "danger",
        title: "Tax Status",
        message: `Status: ${finance.tax_status}. Please check with the Ministry of Finance.`,
      });

    const justice = get(m.justice);
    if (justice?.criminal_record_status === "Clean")
      result.push({
        type: "success",
        title: "Criminal Record",
        message: "Your criminal record is clean.",
      });

    return result;
  }, [m]);

  const alertStyle = {
    warning: "border-amber-300 bg-amber-50 text-amber-900",
    danger: "border-red-300 bg-red-50 text-red-900",
    success: "border-emerald-300 bg-emerald-50 text-emerald-900",
    info: "border-blue-300 bg-blue-50 text-blue-900",
  };
  const dotStyle = {
    warning: "bg-amber-400",
    danger: "bg-red-500",
    success: "bg-emerald-500",
    info: "bg-blue-500",
  };

  const statCards = [
    { label: "Ministries", value: stats.activeMinistries, suffix: "/12", color: "from-blue-500 to-blue-600" },
    { label: "Vehicles", value: stats.vehicles, color: "from-orange-500 to-orange-600" },
    { label: "Properties", value: stats.properties, color: "from-teal-500 to-teal-600" },
    { label: "Businesses", value: stats.businesses, color: "from-rose-500 to-rose-600" },
    { label: "Benefits", value: stats.benefits, color: "from-purple-500 to-purple-600" },
    { label: "Audit Entries", value: auditCount, color: "from-gray-500 to-gray-600" },
  ];

  return (
    <div className="animate-fade-in space-y-6">
      {/* Profile Card */}
      <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6 flex items-center gap-5">
        <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center text-white text-2xl font-bold shadow-md">
          {data.full_name.charAt(0)}
        </div>
        <div className="flex-1 min-w-0">
          <h2 className="text-xl font-bold text-gray-900 truncate">
            {data.full_name}
          </h2>
          <div className="flex flex-wrap gap-x-5 gap-y-1 mt-1.5 text-sm text-gray-500">
            <span>
              CIN{" "}
              <span className="font-mono text-gray-700 font-medium">
                {data.cin}
              </span>
            </span>
            <span>Born {data.birth_date}</span>
            <span>{data.nationality}</span>
            {get(m.employment) && (
              <span className="text-emerald-600 font-medium">
                {get(m.employment).employment_status}
                {get(m.employment).current_employer &&
                  ` at ${get(m.employment).current_employer}`}
              </span>
            )}
          </div>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3 stagger">
        {statCards.map((s) => (
          <div
            key={s.label}
            className="bg-white rounded-xl shadow-sm border border-gray-100 p-4 hover:shadow-md transition-shadow"
          >
            <div className="text-2xl font-bold text-gray-900">
              {s.value}
              {s.suffix && (
                <span className="text-sm text-gray-400 font-normal">
                  {s.suffix}
                </span>
              )}
            </div>
            <div className="text-xs text-gray-500 mt-1">{s.label}</div>
            <div
              className={`h-1 w-8 rounded-full bg-gradient-to-r ${s.color} mt-2`}
            />
          </div>
        ))}
      </div>

      {/* Alerts */}
      {alerts.length > 0 && (
        <div className="space-y-2">
          <h3 className="text-sm font-semibold text-gray-600 uppercase tracking-wider">
            Notifications
          </h3>
          {alerts.map((a, i) => (
            <div
              key={i}
              className={`flex items-start gap-3 border rounded-xl px-4 py-3 ${alertStyle[a.type]}`}
            >
              <div
                className={`w-2.5 h-2.5 rounded-full mt-1 flex-shrink-0 ${dotStyle[a.type]}`}
              />
              <div className="min-w-0">
                <div className="text-sm font-semibold">{a.title}</div>
                <div className="text-sm opacity-80">{a.message}</div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Quick Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {get(m.finance) && (
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-5">
            <div className="text-xs font-semibold text-gray-400 uppercase tracking-wider">
              Tax Status
            </div>
            <div className="mt-2 flex items-center gap-2">
              <span
                className={`inline-block w-2 h-2 rounded-full ${get(m.finance).tax_status === "Up to date" ? "bg-emerald-500" : "bg-red-500"}`}
              />
              <span className="text-lg font-semibold text-gray-900">
                {get(m.finance).tax_status}
              </span>
            </div>
            <div className="text-sm text-gray-500 mt-1">
              Tax ID: {get(m.finance).tax_id}
            </div>
          </div>
        )}
        {get(m.interior) && (
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-5">
            <div className="text-xs font-semibold text-gray-400 uppercase tracking-wider">
              Passport
            </div>
            <div className="mt-2 text-lg font-semibold text-gray-900 font-mono">
              {get(m.interior).passport_number}
            </div>
            <div className="text-sm text-gray-500 mt-1">
              Expires {get(m.interior).passport_expiry || "N/A"}
            </div>
          </div>
        )}
      </div>

      {/* Completeness Score */}
      <CompletenessCard cin={data.cin} />
    </div>
  );
}
