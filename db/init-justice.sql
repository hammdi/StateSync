-- Ministry of Justice — criminal records, cases, sentences

CREATE TABLE IF NOT EXISTS justice_records (
    cin              VARCHAR(20) PRIMARY KEY,
    criminal_record  VARCHAR(20) NOT NULL DEFAULT 'clean',
    cases            JSONB DEFAULT '[]'::jsonb,
    sentences        JSONB DEFAULT '[]'::jsonb,
    restrictions     JSONB DEFAULT '[]'::jsonb,
    created_at       TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at       TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

INSERT INTO justice_records (cin, criminal_record, cases, sentences, restrictions) VALUES
('10000001', 'clean', '[]', '[]', '[]'),
('10000002', 'clean', '[]', '[]', '[]'),
('10000003', 'clean',
 '[{"case_id":"CIV-2018-4421","type":"civil","date":"2018-05-10","description":"Commercial dispute - breach of contract","verdict":"Settled","status":"closed"}]',
 '[]', '[]'),
('10000004', 'clean', '[]', '[]', '[]'),
('10000005', 'clean', '[]', '[]', '[]'),
('10000006', 'clean', '[]', '[]', '[]'),
('10000007', 'minor',
 '[{"case_id":"TRF-2022-1187","type":"traffic","date":"2022-11-15","description":"Excessive speeding - 140km/h in 80 zone","verdict":"Guilty","status":"closed"},
   {"case_id":"TRF-2023-0342","type":"traffic","date":"2023-03-22","description":"Running red light","verdict":"Guilty","status":"closed"}]',
 '[{"case_id":"TRF-2022-1187","type":"Fine","amount":1500,"currency":"USD","date":"2022-12-01","paid":true},
   {"case_id":"TRF-2023-0342","type":"Fine","amount":800,"currency":"USD","date":"2023-04-15","paid":true}]',
 '[]'),
('10000008', 'clean', '[]', '[]', '[]'),
('10000009', 'clean',
 '[{"case_id":"CIV-2020-7890","type":"civil","date":"2020-06-15","description":"Land boundary dispute with neighbor","verdict":"Ruling in favor","status":"closed"}]',
 '[]', '[]'),
('10000010', 'clean', '[]', '[]', '[]')
ON CONFLICT (cin) DO NOTHING;
