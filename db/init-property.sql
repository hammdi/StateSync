-- Ministry of Property — land registry, properties, mortgages

CREATE TABLE IF NOT EXISTS property_records (
    cin            VARCHAR(20) PRIMARY KEY,
    properties     JSONB DEFAULT '[]'::jsonb,
    mortgages      JSONB DEFAULT '[]'::jsonb,
    land_registry  JSONB DEFAULT '[]'::jsonb,
    created_at     TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at     TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

INSERT INTO property_records (cin, properties, mortgages, land_registry) VALUES
('10000001',
 '[{"title_id":"PROP-2019-00142","address":"42 Republic Ave, Apt 5B, Capital City","area_sqm":95,"type":"Apartment","acquired":"2019-03-20","value":120000}]',
 '[{"bank":"National Bank","amount":90000,"remaining":62000,"rate":4.5,"start":"2019-03-20","end":"2039-03-20","status":"active"}]',
 '[]'),
('10000002', '[]', '[]', '[]'),
('10000003',
 '[{"title_id":"PROP-2008-00891","address":"8 Commerce Blvd, Mountain View","area_sqm":350,"type":"Villa","acquired":"2008-06-15","value":450000},
   {"title_id":"PROP-2015-01234","address":"12 Industrial Zone, Sector 4","area_sqm":2000,"type":"Industrial","acquired":"2015-09-01","value":380000},
   {"title_id":"PROP-2020-02100","address":"55 Beach Road, Harbor Town","area_sqm":120,"type":"Apartment","acquired":"2020-12-10","value":180000}]',
 '[{"bank":"National Bank","amount":300000,"remaining":95000,"rate":3.8,"start":"2008-06-15","end":"2028-06-15","status":"active"}]',
 '[]'),
('10000004',
 '[{"title_id":"PROP-2021-01567","address":"23 Jasmine Street, River City","area_sqm":110,"type":"Apartment","acquired":"2021-07-01","value":95000}]',
 '[{"bank":"Housing Credit Bank","amount":75000,"remaining":58000,"rate":5.0,"start":"2021-07-01","end":"2046-07-01","status":"active"}]',
 '[]'),
('10000005',
 '[{"title_id":"PROP-2002-00234","address":"7 Veterans Road, Capital City","area_sqm":200,"type":"House","acquired":"2002-11-15","value":220000}]',
 '[]', '[]'),
('10000006', '[]', '[]', '[]'),
('10000007',
 '[{"title_id":"PROP-2016-00789","address":"5 Justice Lane, Apt 12, Lake District","area_sqm":85,"type":"Apartment","acquired":"2016-04-01","value":135000}]',
 '[]', '[]'),
('10000008', '[]', '[]', '[]'),
('10000009',
 '[{"title_id":"PROP-1998-00056","address":"Valley Farm, Rural Route 3, South Plains","area_sqm":50000,"type":"Agricultural land","acquired":"1998-01-01","value":200000},
   {"title_id":"PROP-2005-00321","address":"1 Valley Farm House, South Plains","area_sqm":180,"type":"House","acquired":"2005-05-10","value":85000}]',
 '[]',
 '[{"parcel_id":"LR-SP-1998-056","area_hectares":5.0,"classification":"Agricultural","zone":"Rural South Plains"}]'),
('10000010', '[]', '[]', '[]')
ON CONFLICT (cin) DO NOTHING;
