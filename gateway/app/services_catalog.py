"""
Service catalog — every government service citizens can request online.

Each service has:
  id            — unique key
  name          — display name
  description   — what it does
  category      — certificate | update | application
  requires      — fields the citizen must fill in
  processing    — estimated processing time
  auto_approve  — True = instant document, False = needs employee review
"""

CATALOG: dict[str, list[dict]] = {
    "civil": [
        {"id": "civil-birth-cert", "name": "Birth Certificate", "description": "Official copy of your birth certificate", "category": "certificate", "requires": [], "processing": "Instant", "auto_approve": True},
        {"id": "civil-family-cert", "name": "Family Composition Certificate", "description": "Certificate listing all family members", "category": "certificate", "requires": [], "processing": "Instant", "auto_approve": True},
        {"id": "civil-residence-cert", "name": "Residence Certificate", "description": "Proof of your registered address", "category": "certificate", "requires": [], "processing": "Instant", "auto_approve": True},
        {"id": "civil-address-change", "name": "Address Change Request", "description": "Update your registered address", "category": "update", "requires": [{"field": "new_address", "label": "New Address", "type": "text"}], "processing": "2-3 days", "auto_approve": False},
        {"id": "civil-marital-update", "name": "Marital Status Update", "description": "Declare marriage, divorce, or widowhood", "category": "update", "requires": [{"field": "new_status", "label": "New Status", "type": "select", "options": ["Married", "Divorced", "Widowed"]}, {"field": "date", "label": "Date of Event", "type": "date"}], "processing": "5-7 days", "auto_approve": False},
    ],
    "education": [
        {"id": "edu-diploma-verify", "name": "Diploma Verification Letter", "description": "Official letter verifying your diploma authenticity", "category": "certificate", "requires": [{"field": "diploma_title", "label": "Diploma Title", "type": "text"}], "processing": "3-5 days", "auto_approve": False},
        {"id": "edu-transcript", "name": "Academic Transcript", "description": "Official academic record", "category": "certificate", "requires": [], "processing": "Instant", "auto_approve": True},
        {"id": "edu-equivalence", "name": "Foreign Diploma Equivalence", "description": "Request equivalence recognition for a foreign diploma", "category": "application", "requires": [{"field": "foreign_diploma", "label": "Foreign Diploma", "type": "text"}, {"field": "institution", "label": "Institution", "type": "text"}, {"field": "country", "label": "Country", "type": "text"}], "processing": "15-30 days", "auto_approve": False},
    ],
    "defense": [
        {"id": "def-service-cert", "name": "Military Service Certificate", "description": "Proof of military service completion or exemption", "category": "certificate", "requires": [], "processing": "Instant", "auto_approve": True},
    ],
    "health": [
        {"id": "health-vaccine-cert", "name": "Vaccination Certificate", "description": "Official vaccination record for travel or employment", "category": "certificate", "requires": [], "processing": "Instant", "auto_approve": True},
        {"id": "health-medical-summary", "name": "Medical Record Summary", "description": "Summary of your medical file", "category": "certificate", "requires": [{"field": "purpose", "label": "Purpose", "type": "select", "options": ["Employment", "Insurance", "Travel", "Legal"]}], "processing": "3-5 days", "auto_approve": False},
    ],
    "justice": [
        {"id": "justice-b3", "name": "Criminal Record Extract (B3)", "description": "Bulletin N.3 — standard criminal record check", "category": "certificate", "requires": [], "processing": "Instant", "auto_approve": True},
        {"id": "justice-b2", "name": "Criminal Record Extract (B2)", "description": "Bulletin N.2 — detailed record for employers", "category": "certificate", "requires": [{"field": "employer", "label": "Requesting Employer", "type": "text"}], "processing": "2-3 days", "auto_approve": False},
    ],
    "finance": [
        {"id": "finance-tax-clearance", "name": "Tax Clearance Certificate", "description": "Proof that all taxes are paid and up to date", "category": "certificate", "requires": [], "processing": "1-2 days", "auto_approve": False},
        {"id": "finance-declaration-copy", "name": "Tax Declaration Copy", "description": "Certified copy of your annual tax declaration", "category": "certificate", "requires": [{"field": "year", "label": "Year", "type": "number"}], "processing": "Instant", "auto_approve": True},
        {"id": "finance-income-cert", "name": "Income Certificate", "description": "Official proof of declared income", "category": "certificate", "requires": [{"field": "year", "label": "Year", "type": "number"}], "processing": "Instant", "auto_approve": True},
    ],
    "social": [
        {"id": "social-attestation", "name": "Social Security Attestation", "description": "Proof of social security enrollment and contributions", "category": "certificate", "requires": [], "processing": "Instant", "auto_approve": True},
        {"id": "social-retirement-est", "name": "Retirement Benefit Estimate", "description": "Projected retirement benefits based on contributions", "category": "certificate", "requires": [], "processing": "5-10 days", "auto_approve": False},
        {"id": "social-benefit-claim", "name": "New Benefit Application", "description": "Apply for a new social benefit", "category": "application", "requires": [{"field": "benefit_type", "label": "Benefit Type", "type": "select", "options": ["Child Benefit", "Disability Support", "Housing Aid", "Unemployment"]}, {"field": "justification", "label": "Justification", "type": "textarea"}], "processing": "10-15 days", "auto_approve": False},
    ],
    "transport": [
        {"id": "transport-license-renew", "name": "License Renewal", "description": "Renew your driver's license", "category": "application", "requires": [], "processing": "7-10 days", "auto_approve": False},
        {"id": "transport-vehicle-cert", "name": "Vehicle Registration Certificate", "description": "Official vehicle registration document", "category": "certificate", "requires": [{"field": "vehicle_plate", "label": "License Plate", "type": "text"}], "processing": "Instant", "auto_approve": True},
        {"id": "transport-driving-record", "name": "Driving Record", "description": "Official history of driving infractions", "category": "certificate", "requires": [], "processing": "Instant", "auto_approve": True},
    ],
    "property": [
        {"id": "property-ownership", "name": "Ownership Certificate", "description": "Official proof of property ownership", "category": "certificate", "requires": [{"field": "property_id", "label": "Property Title ID", "type": "text"}], "processing": "3-5 days", "auto_approve": False},
        {"id": "property-no-ownership", "name": "Non-Ownership Certificate", "description": "Certificate stating you own no registered property", "category": "certificate", "requires": [], "processing": "Instant", "auto_approve": True},
    ],
}

MINISTRY_LABELS = {
    "civil": "Civil Status",
    "education": "Education",
    "defense": "Defense",
    "health": "Health",
    "justice": "Justice",
    "finance": "Finance",
    "social": "Social Affairs",
    "transport": "Transport",
    "property": "Property",
}
