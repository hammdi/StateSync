-- StateSync Gateway Database
-- Master citizen table, audit log, service requests, documents, employees, error reports.

CREATE TABLE IF NOT EXISTS citizens (
    cin             VARCHAR(20) PRIMARY KEY,
    full_name       VARCHAR(255) NOT NULL,
    birth_date      DATE NOT NULL,
    birth_place     VARCHAR(255),
    nationality     VARCHAR(100) NOT NULL,
    phone           VARCHAR(20),
    email           VARCHAR(255),
    created_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS audit_log (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cin_accessed    VARCHAR(20) NOT NULL,
    accessed_by     VARCHAR(100) NOT NULL,
    ministry        VARCHAR(50),
    action          VARCHAR(50) DEFAULT 'read',
    purpose         TEXT NOT NULL,
    ip_address      VARCHAR(45),
    timestamp       TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE OR REPLACE RULE audit_no_update AS ON UPDATE TO audit_log DO INSTEAD NOTHING;
CREATE OR REPLACE RULE audit_no_delete AS ON DELETE TO audit_log DO INSTEAD NOTHING;
CREATE INDEX IF NOT EXISTS idx_audit_cin ON audit_log (cin_accessed);
CREATE INDEX IF NOT EXISTS idx_audit_ts  ON audit_log (timestamp DESC);

CREATE TABLE IF NOT EXISTS error_reports (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cin             VARCHAR(20) NOT NULL,
    ministry        VARCHAR(50) NOT NULL,
    field_name      VARCHAR(100) NOT NULL,
    current_value   TEXT,
    correct_value   TEXT NOT NULL,
    evidence        TEXT,
    status          VARCHAR(30) DEFAULT 'pending',
    reviewed_by     VARCHAR(100),
    reviewed_at     TIMESTAMP WITH TIME ZONE,
    review_note     TEXT,
    created_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS service_requests (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cin             VARCHAR(20) NOT NULL,
    ministry        VARCHAR(50) NOT NULL,
    service_type    VARCHAR(100) NOT NULL,
    service_name    VARCHAR(255) NOT NULL,
    status          VARCHAR(30) DEFAULT 'pending',
    details         JSONB DEFAULT '{}',
    submitted_at    TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    processed_at    TIMESTAMP WITH TIME ZONE,
    processed_by    VARCHAR(100),
    response_note   TEXT,
    document_id     UUID
);
CREATE INDEX IF NOT EXISTS idx_req_cin ON service_requests (cin);

-- ── Data sharing / consent ───────────────────────────────────

CREATE TABLE IF NOT EXISTS data_shares (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cin             VARCHAR(20) NOT NULL,
    token           VARCHAR(100) UNIQUE NOT NULL,
    access_code     VARCHAR(10) NOT NULL,
    recipient_name  VARCHAR(255) NOT NULL,
    purpose         VARCHAR(255),
    ministries      JSONB NOT NULL,
    expires_at      TIMESTAMP WITH TIME ZONE NOT NULL,
    one_time        BOOLEAN DEFAULT FALSE,
    used            BOOLEAN DEFAULT FALSE,
    revoked         BOOLEAN DEFAULT FALSE,
    access_count    INTEGER DEFAULT 0,
    created_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_shares_cin   ON data_shares (cin);
CREATE INDEX IF NOT EXISTS idx_shares_token ON data_shares (token);

CREATE TABLE IF NOT EXISTS documents (
    id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cin              VARCHAR(20) NOT NULL,
    document_type    VARCHAR(100) NOT NULL,
    ministry         VARCHAR(50) NOT NULL,
    title            VARCHAR(255) NOT NULL,
    content          JSONB NOT NULL,
    reference_number VARCHAR(50) UNIQUE NOT NULL,
    generated_at     TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    valid_until      DATE,
    request_id       UUID
);
CREATE INDEX IF NOT EXISTS idx_doc_cin ON documents (cin);

CREATE TABLE IF NOT EXISTS employees (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username        VARCHAR(100) UNIQUE NOT NULL,
    password_hash   VARCHAR(255) NOT NULL,
    full_name       VARCHAR(255) NOT NULL,
    ministry        VARCHAR(50) NOT NULL,
    role            VARCHAR(50) DEFAULT 'agent',
    active          BOOLEAN DEFAULT TRUE,
    created_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS otp_codes (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cin             VARCHAR(20) NOT NULL,
    code            VARCHAR(6) NOT NULL,
    expires_at      TIMESTAMP WITH TIME ZONE NOT NULL,
    used            BOOLEAN DEFAULT FALSE,
    created_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ── 10 Citizens ──────────────────────────────────────────────

INSERT INTO citizens (cin, full_name, birth_date, birth_place, nationality, phone) VALUES
  ('10000001', 'Ahmed El Fassi',    '1989-03-15', 'Capital City',     'National', '+1-555-0101'),
  ('10000002', 'Maria Santos',      '1996-07-22', 'Harbor Town',      'National', '+1-555-0102'),
  ('10000003', 'John Mitchell',     '1979-11-08', 'Mountain View',    'National', '+1-555-0103'),
  ('10000004', 'Aisha Patel',       '1992-04-17', 'River City',       'National', '+1-555-0104'),
  ('10000005', 'Youssef Karim',     '1969-01-30', 'Capital City',     'National', '+1-555-0105'),
  ('10000006', 'Lin Chen',          '2000-09-12', 'East Borough',     'National', '+1-555-0106'),
  ('10000007', 'David Rousseau',    '1984-06-05', 'Lake District',    'National', '+1-555-0107'),
  ('10000008', 'Amina Diallo',      '1986-12-25', 'Harbor Town',      'National', '+1-555-0108'),
  ('10000009', 'Carlos Mendoza',    '1974-08-19', 'South Plains',     'National', '+1-555-0109'),
  ('10000010', 'Sophie Andersson',  '1995-02-28', 'North Bay',        'Resident', '+1-555-0110')
ON CONFLICT (cin) DO NOTHING;

-- ── Employees (password: admin123 — SHA-256) ─────────────────

INSERT INTO employees (username, password_hash, full_name, ministry, role) VALUES
  ('civil.agent',    '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9', 'Sarah Johnson',   'civil',     'agent'),
  ('edu.agent',      '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9', 'David Lee',       'education', 'agent'),
  ('defense.agent',  '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9', 'Kenji Yamamoto',  'defense',   'agent'),
  ('health.agent',   '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9', 'Emma Wilson',     'health',    'agent'),
  ('justice.agent',  '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9', 'Robert Martin',   'justice',   'agent'),
  ('finance.agent',  '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9', 'James Brown',     'finance',   'agent'),
  ('social.agent',   '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9', 'Alice Chen',      'social',    'agent'),
  ('transport.agent','240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9', 'Nina Petrov',     'transport', 'agent'),
  ('property.agent', '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9', 'Fatima Zahra',    'property',  'agent'),
  ('admin',          '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9', 'System Admin',    'all',       'admin')
ON CONFLICT (username) DO NOTHING;

-- ── Sample audit log (100 entries) ───────────────────────────

INSERT INTO audit_log (cin_accessed, accessed_by, ministry, action, purpose) VALUES
  ('10000001', 'citizen-portal', NULL, 'read', 'Citizen data consultation'),
  ('10000001', 'ministry-health', 'health', 'read', 'Medical checkup verification'),
  ('10000001', 'ministry-finance', 'finance', 'read', 'Tax assessment review'),
  ('10000002', 'citizen-portal', NULL, 'read', 'Citizen data consultation'),
  ('10000002', 'ministry-education', 'education', 'update', 'Diploma verification completed'),
  ('10000003', 'citizen-portal', NULL, 'read', 'Citizen data consultation'),
  ('10000003', 'ministry-finance', 'finance', 'read', 'Company tax audit'),
  ('10000003', 'ministry-justice', 'justice', 'read', 'Background check for business license'),
  ('10000004', 'ministry-education', 'education', 'update', 'Teaching certification added'),
  ('10000004', 'citizen-portal', NULL, 'read', 'Citizen data consultation'),
  ('10000005', 'ministry-defense', 'defense', 'read', 'Pension eligibility check'),
  ('10000005', 'ministry-social', 'social', 'read', 'Retirement benefits calculation'),
  ('10000005', 'citizen-portal', NULL, 'read', 'Citizen data consultation'),
  ('10000006', 'ministry-education', 'education', 'update', 'Scholarship renewal'),
  ('10000006', 'citizen-portal', NULL, 'read', 'Citizen data consultation'),
  ('10000007', 'ministry-justice', 'justice', 'read', 'Bar association membership verification'),
  ('10000007', 'ministry-transport', 'transport', 'read', 'License violation check'),
  ('10000007', 'citizen-portal', NULL, 'read', 'Citizen data consultation'),
  ('10000008', 'ministry-health', 'health', 'update', 'Vaccination record updated'),
  ('10000008', 'citizen-portal', NULL, 'read', 'Citizen data consultation'),
  ('10000009', 'ministry-property', 'property', 'read', 'Land title verification'),
  ('10000009', 'ministry-finance', 'finance', 'read', 'Agricultural tax assessment'),
  ('10000009', 'citizen-portal', NULL, 'read', 'Citizen data consultation'),
  ('10000010', 'citizen-portal', NULL, 'read', 'Citizen data consultation'),
  ('10000010', 'ministry-social', 'social', 'read', 'Work permit verification');
