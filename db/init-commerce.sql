-- Ministry of Commerce Database

CREATE TABLE IF NOT EXISTS commerce_records (
    cin          VARCHAR(20) PRIMARY KEY,
    businesses   JSONB DEFAULT '[]'::jsonb,
    created_at   TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at   TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Seed data
INSERT INTO commerce_records (cin, businesses) VALUES
    ('12345678', '[]'),
    ('87654321',
     '[{"name": "Garcia Medical Clinic", "registration_id": "BIZ-20150042", "type": "Healthcare", "status": "Active", "founded": 2015}]'),
    ('11223344',
     '[{"name": "Tanaka Engineering Ltd", "registration_id": "BIZ-20050018", "type": "Engineering", "status": "Active", "founded": 2005}]')
ON CONFLICT (cin) DO NOTHING;
