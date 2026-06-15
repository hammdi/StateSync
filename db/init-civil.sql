-- Ministry of Civil Status — identity, family, residence

CREATE TABLE IF NOT EXISTS civil_records (
    cin             VARCHAR(20) PRIMARY KEY,
    address         TEXT,
    city            VARCHAR(100),
    marital_status  VARCHAR(50),
    children        JSONB DEFAULT '[]'::jsonb,
    parents         JSONB DEFAULT '{}'::jsonb,
    death_date      DATE,
    created_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

INSERT INTO civil_records (cin, address, city, marital_status, children, parents) VALUES
('10000001', '42 Republic Ave, Apt 5B', 'Capital City', 'Married',
 '[{"name":"Sara El Fassi","birth_date":"2018-06-10","cin":null},{"name":"Omar El Fassi","birth_date":"2021-01-22","cin":null}]',
 '{"father":"Hassan El Fassi","mother":"Khadija Bouzid"}'),
('10000002', '15 Ocean Drive', 'Harbor Town', 'Single', '[]',
 '{"father":"Pedro Santos","mother":"Isabella Santos"}'),
('10000003', '8 Commerce Blvd, Suite 200', 'Mountain View', 'Married',
 '[{"name":"Emma Mitchell","birth_date":"2005-03-14","cin":null},{"name":"Jack Mitchell","birth_date":"2008-09-01","cin":null},{"name":"Lily Mitchell","birth_date":"2012-12-20","cin":null}]',
 '{"father":"Robert Mitchell","mother":"Helen Mitchell"}'),
('10000004', '23 Jasmine Street', 'River City', 'Married',
 '[{"name":"Priya Patel","birth_date":"2020-11-05","cin":null}]',
 '{"father":"Raj Patel","mother":"Sunita Patel"}'),
('10000005', '7 Veterans Road', 'Capital City', 'Married',
 '[{"name":"Layla Karim","birth_date":"1995-04-18","cin":"10000020"},{"name":"Tarek Karim","birth_date":"1998-07-09","cin":"10000021"}]',
 '{"father":"Mustafa Karim","mother":"Zahra Karim"}'),
('10000006', '112 University Campus, Dorm C', 'East Borough', 'Single', '[]',
 '{"father":"Wei Chen","mother":"Mei Lin Chen"}'),
('10000007', '5 Justice Lane, Apt 12', 'Lake District', 'Divorced', '[]',
 '{"father":"Pierre Rousseau","mother":"Claire Rousseau"}'),
('10000008', '30 Health Center Road', 'Harbor Town', 'Married',
 '[{"name":"Ibrahim Diallo","birth_date":"2015-08-30","cin":null},{"name":"Fatou Diallo","birth_date":"2019-02-14","cin":null}]',
 '{"father":"Moussa Diallo","mother":"Mariam Diallo"}'),
('10000009', '1 Valley Farm, Rural Route 3', 'South Plains', 'Widowed',
 '[{"name":"Elena Mendoza","birth_date":"2000-05-12","cin":"10000030"},{"name":"Diego Mendoza","birth_date":"2003-10-27","cin":"10000031"}]',
 '{"father":"Miguel Mendoza","mother":"Rosa Mendoza"}'),
('10000010', '88 Tech Hub, Apt 22A', 'North Bay', 'Single', '[]',
 '{"father":"Erik Andersson","mother":"Anna Andersson"}')
ON CONFLICT (cin) DO NOTHING;
