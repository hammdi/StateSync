-- Ministry of Interior Database

CREATE TABLE IF NOT EXISTS interior_records (
    cin               VARCHAR(20) PRIMARY KEY,
    passport_number   VARCHAR(50),
    passport_expiry   DATE,
    residence_permit  VARCHAR(100),
    permit_expiry     DATE,
    created_at        TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at        TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Seed data
INSERT INTO interior_records (cin, passport_number, passport_expiry, residence_permit, permit_expiry) VALUES
    ('12345678', 'P12345678', '2028-09-15', NULL, NULL),
    ('87654321', 'P87654321', '2027-03-20', NULL, NULL),
    ('11223344', 'P11223344', '2026-12-01', 'Permanent Resident', '2030-12-01')
ON CONFLICT (cin) DO NOTHING;
