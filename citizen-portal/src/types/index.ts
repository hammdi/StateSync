// eslint-disable-next-line @typescript-eslint/no-explicit-any
export type MinistryData = Record<string, any>;

export interface CitizenData {
  cin: string;
  full_name: string;
  birth_date: string;
  nationality: string;
  ministries: Record<string, MinistryData | ServiceError | null>;
}

export interface ServiceError { error: string }

export interface AuditEntry {
  id: string;
  cin_accessed: string;
  accessed_by: string;
  purpose: string;
  timestamp: string;
}

export interface ErrorReportPayload { ministry: string; field: string; message: string }

// ── Services & Requests ──────────────────────────

export interface ServiceField {
  field: string;
  label: string;
  type: "text" | "number" | "date" | "select" | "textarea";
  options?: string[];
}

export interface ServiceDef {
  id: string;
  name: string;
  description: string;
  category: "certificate" | "update" | "application";
  requires: ServiceField[];
  processing: string;
  auto_approve: boolean;
}

export interface ServiceRequest {
  id: string;
  cin: string;
  ministry: string;
  ministry_label: string;
  service_type: string;
  service_name: string;
  status: "pending" | "approved" | "rejected";
  details: Record<string, string>;
  submitted_at: string;
  processed_at: string | null;
  processed_by: string | null;
  response_note: string | null;
  document_id: string | null;
}

// ── Documents ────────────────────────────────────

export interface DocumentMeta {
  id: string;
  cin: string;
  document_type: string;
  ministry: string;
  title: string;
  reference_number: string;
  generated_at: string;
  valid_until: string | null;
}

export interface DocumentSection {
  heading: string;
  fields?: [string, string][];
  text?: string;
  list?: string[];
}

export interface DocumentContent {
  header: { country: string; ministry: string; emblem: string };
  reference: string;
  issued_date: string;
  citizen: { full_name: string; cin: string; birth_date: string; nationality: string };
  title: string;
  sections: DocumentSection[];
  valid_until: string | null;
  verification_url: string;
  footer: string;
}

export interface DocumentFull extends DocumentMeta { content: DocumentContent }

// ── Employee ─────────────────────────────────────

export interface EmployeeInfo {
  username: string;
  full_name: string;
  ministry: string;
  ministry_label: string;
  role: string;
}

export interface EmployeeDashboardData {
  employee: { name: string; ministry: string };
  stats: { total: number; pending: number; approved: number; rejected: number };
  pending_requests: ServiceRequest[];
}

// ── Display types ────────────────────────────────

export interface Diploma { title: string; institution: string; year: number }
export interface Equivalence { foreign_diploma: string; local_equivalent: string; year: number }
export interface Vaccination { name: string; date: string; doses: number }
export interface TaxDeclaration { year: number; income: number; tax_paid: number }
export interface Benefit { type: string; amount: number; currency: string; frequency: string }
export interface Vehicle { plate: string; make: string; model: string; year: number }
export interface Business { name: string; registration_id: string; type: string; status: string; founded: number }
export interface Property { title_id: string; type: string; address: string; area_sqm: number; acquired: number }
export interface Contract { employer: string; role: string; start_date: string; end_date: string | null; type: string }
export interface JusticeCase { description: string; date: string; status: string }
