-- Ministry of Employment Database

CREATE TABLE IF NOT EXISTS employment_records (
    cin                VARCHAR(20) PRIMARY KEY,
    employment_status  VARCHAR(50) DEFAULT 'Employed',
    current_employer   VARCHAR(255),
    contracts          JSONB DEFAULT '[]'::jsonb,
    created_at         TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at         TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Seed data
INSERT INTO employment_records (cin, employment_status, current_employer, contracts) VALUES
    ('12345678', 'Employed', 'National Tech Corp',
     '[{"employer": "National Tech Corp", "role": "Software Engineer", "start_date": "2013-01-15", "end_date": null, "type": "Permanent"}]'),
    ('87654321', 'Employed', 'City Hospital',
     '[{"employer": "City Hospital", "role": "Senior Physician", "start_date": "2011-06-01", "end_date": null, "type": "Permanent"},
       {"employer": "Medical Academy", "role": "Resident", "start_date": "2008-09-01", "end_date": "2011-05-31", "type": "Fixed-term"}]'),
    ('11223344', 'Self-employed', 'Tanaka Engineering Ltd',
     '[{"employer": "Tanaka Engineering Ltd", "role": "Managing Director", "start_date": "2005-03-01", "end_date": null, "type": "Self-employed"},
       {"employer": "National Construction Co", "role": "Civil Engineer", "start_date": "2001-02-01", "end_date": "2005-02-28", "type": "Permanent"}]')
ON CONFLICT (cin) DO NOTHING;
