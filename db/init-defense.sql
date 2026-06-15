-- Ministry of Defense — military service records

CREATE TABLE IF NOT EXISTS defense_records (
    cin              VARCHAR(20) PRIMARY KEY,
    military_status  VARCHAR(50) NOT NULL DEFAULT 'pending',
    service_start    DATE,
    service_end      DATE,
    unit             VARCHAR(255),
    rank             VARCHAR(100),
    exemption_reason VARCHAR(255),
    created_at       TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at       TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

INSERT INTO defense_records (cin, military_status, service_start, service_end, unit, rank, exemption_reason) VALUES
('10000001', 'done',     '2013-09-01', '2014-09-01', '3rd Infantry Brigade',       'Corporal',  NULL),
('10000002', 'exempt',   NULL, NULL, NULL, NULL, 'Medical professional — essential service'),
('10000003', 'done',     '2001-06-15', '2002-06-15', 'Logistics Battalion',        'Private',   NULL),
('10000004', 'exempt',   NULL, NULL, NULL, NULL, 'Female — voluntary service only'),
('10000005', 'done',     '1991-07-01', '2019-12-31', 'Special Operations Command', 'Colonel',   NULL),
('10000006', 'deferred', NULL, NULL, NULL, NULL, 'University enrollment — deferred until graduation'),
('10000007', 'done',     '2007-09-01', '2008-09-01', 'Military Police',            'Sergeant',  NULL),
('10000008', 'exempt',   NULL, NULL, NULL, NULL, 'Female — voluntary service only'),
('10000009', 'done',     '1994-03-01', '1995-03-01', '7th Armored Division',       'Corporal',  NULL),
('10000010', 'exempt',   NULL, NULL, NULL, NULL, 'Foreign national — resident status')
ON CONFLICT (cin) DO NOTHING;
