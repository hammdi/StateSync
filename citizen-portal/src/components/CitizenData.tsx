import { useState } from "react";
import type {
  CitizenData,
  ServiceError,
  MinistryData,
  Diploma,
  Equivalence,
  Vaccination,
  TaxDeclaration,
  Benefit,
  Vehicle,
  Business,
  Property,
  Contract,
  JusticeCase,
} from "../types";

interface Props {
  data: CitizenData;
}

function isError(obj: unknown): obj is ServiceError {
  return typeof obj === "object" && obj !== null && "error" in obj;
}

/* ── Reusable sub-components ─────────────────────── */

function KV({ items }: { items: [string, string | number | null | undefined][] }) {
  return (
    <dl className="grid grid-cols-1 sm:grid-cols-2 gap-x-6 gap-y-3 text-sm">
      {items.map(([label, value]) => (
        <div key={label}>
          <dt className="text-gray-400 text-xs font-medium uppercase tracking-wider">
            {label}
          </dt>
          <dd className="text-gray-900 mt-0.5 font-medium">
            {value ?? "N/A"}
          </dd>
        </div>
      ))}
    </dl>
  );
}

function Badge({ children, color = "gray" }: { children: React.ReactNode; color?: string }) {
  const colors: Record<string, string> = {
    gray: "bg-gray-100 text-gray-700",
    green: "bg-emerald-100 text-emerald-700",
    amber: "bg-amber-100 text-amber-700",
    red: "bg-red-100 text-red-700",
    blue: "bg-blue-100 text-blue-700",
  };
  return (
    <span className={`text-xs font-semibold px-2.5 py-0.5 rounded-full ${colors[color] || colors.gray}`}>
      {children}
    </span>
  );
}

function Section({
  title,
  borderColor,
  data,
  defaultOpen = false,
  summary,
  children,
}: {
  title: string;
  borderColor: string;
  data: MinistryData | ServiceError | null;
  defaultOpen?: boolean;
  summary?: string;
  children: (d: MinistryData) => React.ReactNode;
}) {
  const [open, setOpen] = useState(defaultOpen);
  const hasData = data && !isError(data);

  return (
    <div className={`bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden border-l-4 ${borderColor}`}>
      <button
        onClick={() => setOpen(!open)}
        className="w-full flex items-center justify-between px-5 py-4 text-left hover:bg-gray-50/50 transition-colors"
      >
        <div className="flex items-center gap-3 min-w-0">
          <h2 className="text-sm font-bold text-gray-800 uppercase tracking-wider">
            {title}
          </h2>
          {!open && summary && hasData && (
            <span className="text-xs text-gray-400 truncate hidden sm:inline">
              {summary}
            </span>
          )}
        </div>
        <div className="flex items-center gap-2 flex-shrink-0">
          {isError(data) && <Badge color="red">Unavailable</Badge>}
          {data === null && <Badge>No data</Badge>}
          {hasData && !open && <Badge color="green">Available</Badge>}
          <svg
            className={`w-4 h-4 text-gray-400 transition-transform duration-200 ${open ? "rotate-180" : ""}`}
            fill="none" viewBox="0 0 24 24" stroke="currentColor"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </div>
      </button>
      {open && (
        <div className="px-5 pb-5 border-t border-gray-100 pt-4 animate-fade-in">
          {isError(data) ? (
            <p className="text-red-500 text-sm">{data.error}</p>
          ) : data ? (
            children(data)
          ) : (
            <p className="text-gray-400 text-sm">No records found for this citizen.</p>
          )}
        </div>
      )}
    </div>
  );
}

/* ── Main component ──────────────────────────────── */

export default function CitizenDataView({ data }: Props) {
  const m = data.ministries;

  return (
    <div className="space-y-3 animate-fade-in">
      {/* Personal Information — always open */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 border-l-4 border-l-gray-800 px-5 py-5">
        <h2 className="text-sm font-bold text-gray-800 uppercase tracking-wider mb-4">
          Personal Information
        </h2>
        <KV
          items={[
            ["Full Name", data.full_name],
            ["CIN", data.cin],
            ["Date of Birth", data.birth_date],
            ["Nationality", data.nationality],
          ]}
        />
      </div>

      <Section
        title="Civil Status"
        borderColor="border-l-blue-500"
        data={m.civil}
        defaultOpen
        summary={m.civil && !isError(m.civil) ? `${(m.civil as MinistryData).marital_status}, ${(m.civil as MinistryData).children_count} children` : undefined}
      >
        {(d) => (
          <KV
            items={[
              ["Address", d.address],
              ["Marital Status", d.marital_status],
              ["Children", d.children_count],
            ]}
          />
        )}
      </Section>

      <Section title="Education" borderColor="border-l-indigo-500" data={m.education} defaultOpen
        summary={m.education && !isError(m.education) ? `${(m.education as MinistryData).diplomas?.length || 0} diploma(s)` : undefined}>
        {(d) => (
          <div className="space-y-5">
            <div>
              <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3">Diplomas</h3>
              {(d.diplomas as Diploma[]).length > 0 ? (
                <div className="space-y-2">
                  {(d.diplomas as Diploma[]).map((dip, i) => (
                    <div key={i} className="flex items-baseline gap-3 bg-gray-50 rounded-lg p-3">
                      <div className="w-1.5 h-1.5 rounded-full bg-indigo-400 mt-1.5 flex-shrink-0" />
                      <div>
                        <div className="text-sm font-semibold text-gray-900">{dip.title}</div>
                        <div className="text-xs text-gray-500">{dip.institution} &middot; {dip.year}</div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : <p className="text-gray-400 text-sm">None</p>}
            </div>
            <div>
              <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3">Equivalences</h3>
              {(d.equivalences as Equivalence[]).length > 0 ? (
                <div className="space-y-2">
                  {(d.equivalences as Equivalence[]).map((eq, i) => (
                    <div key={i} className="bg-gray-50 rounded-lg p-3 text-sm">
                      <span className="font-semibold">{eq.foreign_diploma}</span>
                      <span className="text-gray-400 mx-2">=</span>
                      <span>{eq.local_equivalent}</span>
                      <span className="text-gray-400 ml-2">({eq.year})</span>
                    </div>
                  ))}
                </div>
              ) : <p className="text-gray-400 text-sm">None</p>}
            </div>
          </div>
        )}
      </Section>

      <Section title="Military Service" borderColor="border-l-slate-500" data={m.defense}>
        {(d) => <KV items={[["Status", d.military_status], ["Completion Date", d.completion_date]]} />}
      </Section>

      <Section title="Health Records" borderColor="border-l-emerald-500" data={m.health}
        summary={m.health && !isError(m.health) ? `Blood: ${(m.health as MinistryData).blood_type}` : undefined}>
        {(d) => (
          <div className="space-y-5">
            <KV items={[["Blood Type", d.blood_type]]} />
            <div>
              <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3">Chronic Conditions</h3>
              {(d.chronic_conditions as string[]).length > 0 ? (
                <div className="flex gap-2 flex-wrap">
                  {(d.chronic_conditions as string[]).map((c, i) => (
                    <span key={i} className="bg-orange-50 text-orange-700 text-xs font-semibold px-3 py-1 rounded-full border border-orange-200">{c}</span>
                  ))}
                </div>
              ) : <Badge color="green">None reported</Badge>}
            </div>
            <div>
              <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3">Vaccinations</h3>
              {(d.vaccinations as Vaccination[]).length > 0 ? (
                <div className="space-y-2">
                  {(d.vaccinations as Vaccination[]).map((v, i) => (
                    <div key={i} className="flex items-center justify-between bg-gray-50 rounded-lg p-3 text-sm">
                      <div className="flex items-center gap-3">
                        <div className="w-1.5 h-1.5 rounded-full bg-emerald-400 flex-shrink-0" />
                        <span className="font-semibold">{v.name}</span>
                      </div>
                      <div className="text-gray-500 text-xs">{v.doses} dose{v.doses > 1 ? "s" : ""} &middot; {v.date}</div>
                    </div>
                  ))}
                </div>
              ) : <p className="text-gray-400 text-sm">None</p>}
            </div>
          </div>
        )}
      </Section>

      <Section title="Criminal Record" borderColor="border-l-amber-500" data={m.justice}
        summary={m.justice && !isError(m.justice) ? (m.justice as MinistryData).criminal_record_status : undefined}>
        {(d) => (
          <div className="space-y-3">
            <div className="flex items-center gap-2">
              <span className="text-sm text-gray-500">Status:</span>
              <Badge color={d.criminal_record_status === "Clean" ? "green" : "red"}>
                {d.criminal_record_status}
              </Badge>
            </div>
            {(d.cases as JusticeCase[]).length > 0 && (
              <div className="space-y-2 mt-3">
                {(d.cases as JusticeCase[]).map((c, i) => (
                  <div key={i} className="bg-gray-50 rounded-lg p-3 text-sm">{c.description} ({c.status})</div>
                ))}
              </div>
            )}
          </div>
        )}
      </Section>

      <Section title="Finance & Taxes" borderColor="border-l-green-500" data={m.finance}
        summary={m.finance && !isError(m.finance) ? (m.finance as MinistryData).tax_status : undefined}>
        {(d) => (
          <div className="space-y-5">
            <KV items={[["Tax ID", d.tax_id], ["Status", d.tax_status]]} />
            {(d.annual_declarations as TaxDeclaration[]).length > 0 && (
              <div>
                <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3">Declarations</h3>
                <div className="overflow-x-auto rounded-lg border border-gray-200">
                  <table className="w-full text-sm">
                    <thead><tr className="bg-gray-50 text-gray-500 text-xs uppercase">
                      <th className="px-4 py-2.5 text-left font-semibold">Year</th>
                      <th className="px-4 py-2.5 text-right font-semibold">Income</th>
                      <th className="px-4 py-2.5 text-right font-semibold">Tax Paid</th>
                    </tr></thead>
                    <tbody>
                      {(d.annual_declarations as TaxDeclaration[]).map((dec) => (
                        <tr key={dec.year} className="border-t border-gray-100">
                          <td className="px-4 py-2.5 font-medium">{dec.year}</td>
                          <td className="px-4 py-2.5 text-right text-gray-600">{dec.income.toLocaleString()}</td>
                          <td className="px-4 py-2.5 text-right text-gray-600">{dec.tax_paid.toLocaleString()}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>
        )}
      </Section>

      <Section title="Social Security" borderColor="border-l-purple-500" data={m.social}>
        {(d) => (
          <div className="space-y-5">
            <KV items={[["SS Number", d.social_security_number], ["Retirement", d.retirement_status]]} />
            {(d.benefits as Benefit[]).length > 0 && (
              <div>
                <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3">Active Benefits</h3>
                <div className="space-y-2">
                  {(d.benefits as Benefit[]).map((b, i) => (
                    <div key={i} className="flex items-center justify-between bg-purple-50 rounded-lg p-3 text-sm">
                      <span className="font-semibold text-purple-900">{b.type}</span>
                      <span className="text-purple-700 font-mono text-xs">{b.amount} {b.currency}/{b.frequency}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </Section>

      <Section title="Passport & Residence" borderColor="border-l-cyan-500" data={m.interior}>
        {(d) => (
          <KV items={[
            ["Passport", d.passport_number],
            ["Passport Expiry", d.passport_expiry],
            ["Residence Permit", d.residence_permit],
            ["Permit Expiry", d.permit_expiry],
          ]} />
        )}
      </Section>

      <Section title="Transport & Vehicles" borderColor="border-l-orange-500" data={m.transport}
        summary={m.transport && !isError(m.transport) ? `${(m.transport as MinistryData).vehicles?.length || 0} vehicle(s)` : undefined}>
        {(d) => (
          <div className="space-y-5">
            <KV items={[["License", d.license_number], ["Category", d.license_category], ["Expiry", d.license_expiry]]} />
            {(d.vehicles as Vehicle[]).length > 0 && (
              <div>
                <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3">Registered Vehicles</h3>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                  {(d.vehicles as Vehicle[]).map((v, i) => (
                    <div key={i} className="bg-gray-50 rounded-lg p-3 text-sm flex justify-between items-center">
                      <div>
                        <div className="font-semibold">{v.make} {v.model}</div>
                        <div className="text-xs text-gray-500">{v.year}</div>
                      </div>
                      <span className="font-mono text-xs bg-white px-2 py-1 rounded border border-gray-200">{v.plate}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </Section>

      <Section title="Business Registry" borderColor="border-l-rose-500" data={m.commerce}
        summary={m.commerce && !isError(m.commerce) ? `${(m.commerce as MinistryData).businesses?.length || 0} business(es)` : undefined}>
        {(d) => (
          (d.businesses as Business[]).length > 0 ? (
            <div className="space-y-2">
              {(d.businesses as Business[]).map((b, i) => (
                <div key={i} className="bg-gray-50 rounded-lg p-4">
                  <div className="flex items-start justify-between">
                    <div>
                      <div className="font-semibold text-sm">{b.name}</div>
                      <div className="text-xs text-gray-500 mt-1">{b.type} &middot; Founded {b.founded}</div>
                    </div>
                    <Badge color={b.status === "Active" ? "green" : "gray"}>{b.status}</Badge>
                  </div>
                  <div className="text-xs text-gray-400 mt-2 font-mono">ID: {b.registration_id}</div>
                </div>
              ))}
            </div>
          ) : <p className="text-gray-400 text-sm">No businesses registered</p>
        )}
      </Section>

      <Section title="Land & Property" borderColor="border-l-teal-500" data={m.property}
        summary={m.property && !isError(m.property) ? `${(m.property as MinistryData).properties?.length || 0} propert(ies)` : undefined}>
        {(d) => (
          (d.properties as Property[]).length > 0 ? (
            <div className="space-y-2">
              {(d.properties as Property[]).map((p, i) => (
                <div key={i} className="bg-gray-50 rounded-lg p-4">
                  <div className="flex items-start justify-between">
                    <div>
                      <div className="font-semibold text-sm">{p.type}</div>
                      <div className="text-xs text-gray-500 mt-1">{p.address}</div>
                    </div>
                    <span className="text-xs text-gray-500">{p.area_sqm} m&sup2;</span>
                  </div>
                  <div className="text-xs text-gray-400 mt-2">Acquired {p.acquired} &middot; <span className="font-mono">{p.title_id}</span></div>
                </div>
              ))}
            </div>
          ) : <p className="text-gray-400 text-sm">No properties registered</p>
        )}
      </Section>

      <Section title="Employment" borderColor="border-l-violet-500" data={m.employment}
        summary={m.employment && !isError(m.employment) ? `${(m.employment as MinistryData).employment_status} - ${(m.employment as MinistryData).current_employer}` : undefined}>
        {(d) => (
          <div className="space-y-5">
            <KV items={[["Status", d.employment_status], ["Current Employer", d.current_employer]]} />
            {(d.contracts as Contract[]).length > 0 && (
              <div>
                <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3">Work History</h3>
                <div className="relative">
                  <div className="absolute left-[7px] top-3 bottom-3 w-px bg-gray-200" />
                  <div className="space-y-3">
                    {(d.contracts as Contract[]).map((c, i) => (
                      <div key={i} className="relative flex gap-4 items-start pl-6">
                        <div className="absolute left-0 top-1.5 w-3.5 h-3.5 rounded-full border-2 border-violet-400 bg-white z-10" />
                        <div className="bg-gray-50 rounded-lg p-3 flex-1">
                          <div className="font-semibold text-sm">{c.role}</div>
                          <div className="text-xs text-gray-500">{c.employer}</div>
                          <div className="text-xs text-gray-400 mt-1">
                            <Badge>{c.type}</Badge>
                            <span className="ml-2">{c.start_date} &rarr; {c.end_date || "present"}</span>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </Section>
    </div>
  );
}
