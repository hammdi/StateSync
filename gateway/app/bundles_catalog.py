"""
Document Bundles & Life Events — predefined workflows for common citizen needs.
"""

BUNDLES: dict[str, dict] = {
    "job-application": {
        "name": "Job Application Pack",
        "icon": "briefcase",
        "description": "Everything an employer needs: criminal record, diplomas, employment proof, and social security.",
        "services": [
            {"ministry": "justice", "service_id": "justice-b3"},
            {"ministry": "education", "service_id": "edu-transcript"},
            {"ministry": "social", "service_id": "social-attestation"},
            {"ministry": "civil", "service_id": "civil-residence-cert"},
        ],
    },
    "bank-loan": {
        "name": "Bank Loan Pack",
        "icon": "bank",
        "description": "Income proof, tax clearance, property status, and employment verification.",
        "services": [
            {"ministry": "finance", "service_id": "finance-income-cert", "default_details": {"year": "2024"}},
            {"ministry": "finance", "service_id": "finance-tax-clearance"},
            {"ministry": "property", "service_id": "property-no-ownership"},
            {"ministry": "social", "service_id": "social-attestation"},
        ],
    },
    "travel": {
        "name": "Travel Pack",
        "icon": "plane",
        "description": "Criminal record, vaccination certificate, and civil status for visa applications.",
        "services": [
            {"ministry": "justice", "service_id": "justice-b3"},
            {"ministry": "health", "service_id": "health-vaccine-cert"},
            {"ministry": "civil", "service_id": "civil-birth-cert"},
        ],
    },
    "university-enrollment": {
        "name": "University Enrollment Pack",
        "icon": "graduation",
        "description": "Academic transcript, military status, social security, and birth certificate.",
        "services": [
            {"ministry": "education", "service_id": "edu-transcript"},
            {"ministry": "defense", "service_id": "def-service-cert"},
            {"ministry": "social", "service_id": "social-attestation"},
            {"ministry": "civil", "service_id": "civil-birth-cert"},
        ],
    },
    "business-registration": {
        "name": "Business Registration Pack",
        "icon": "building",
        "description": "Tax clearance, criminal record, social security, and residence certificate.",
        "services": [
            {"ministry": "finance", "service_id": "finance-tax-clearance"},
            {"ministry": "justice", "service_id": "justice-b3"},
            {"ministry": "social", "service_id": "social-attestation"},
            {"ministry": "civil", "service_id": "civil-residence-cert"},
        ],
    },
    "retirement": {
        "name": "Retirement Pack",
        "icon": "sunset",
        "description": "Social security attestation, tax declaration, and military service certificate.",
        "services": [
            {"ministry": "social", "service_id": "social-attestation"},
            {"ministry": "social", "service_id": "social-retirement-est"},
            {"ministry": "finance", "service_id": "finance-declaration-copy", "default_details": {"year": "2024"}},
            {"ministry": "defense", "service_id": "def-service-cert"},
        ],
    },
}

LIFE_EVENTS: dict[str, dict] = {
    "getting-married": {
        "name": "Getting Married",
        "icon": "rings",
        "description": "All administrative steps for your marriage — from certificates to status update.",
        "steps": [
            {"order": 1, "ministry": "civil", "service_id": "civil-birth-cert", "label": "Obtain Birth Certificate", "phase": "preparation"},
            {"order": 2, "ministry": "justice", "service_id": "justice-b3", "label": "Criminal Record Check", "phase": "preparation"},
            {"order": 3, "ministry": "health", "service_id": "health-medical-summary", "label": "Medical Certificate", "phase": "preparation", "details": {"purpose": "Legal"}},
            {"order": 4, "ministry": "civil", "service_id": "civil-residence-cert", "label": "Residence Certificate", "phase": "preparation"},
            {"order": 5, "ministry": "civil", "service_id": "civil-marital-update", "label": "Register Marriage", "phase": "registration", "details": {"new_status": "Married"}},
            {"order": 6, "ministry": "civil", "service_id": "civil-family-cert", "label": "New Family Certificate", "phase": "completion"},
        ],
    },
    "having-a-baby": {
        "name": "Having a Baby",
        "icon": "baby",
        "description": "Register your newborn and activate all benefits automatically.",
        "steps": [
            {"order": 1, "ministry": "civil", "service_id": "civil-birth-cert", "label": "Birth Registration", "phase": "registration"},
            {"order": 2, "ministry": "health", "service_id": "health-vaccine-cert", "label": "Vaccination Record", "phase": "health"},
            {"order": 3, "ministry": "social", "service_id": "social-benefit-claim", "label": "Apply for Child Benefit", "phase": "benefits", "details": {"benefit_type": "Child Benefit", "justification": "New child born"}},
            {"order": 4, "ministry": "civil", "service_id": "civil-family-cert", "label": "Updated Family Certificate", "phase": "completion"},
        ],
    },
    "starting-university": {
        "name": "Starting University",
        "icon": "university",
        "description": "Defer military service, check scholarships, get your documents ready.",
        "steps": [
            {"order": 1, "ministry": "education", "service_id": "edu-transcript", "label": "Academic Transcript", "phase": "preparation"},
            {"order": 2, "ministry": "defense", "service_id": "def-service-cert", "label": "Military Status Certificate", "phase": "preparation"},
            {"order": 3, "ministry": "social", "service_id": "social-attestation", "label": "Social Security Attestation", "phase": "enrollment"},
            {"order": 4, "ministry": "civil", "service_id": "civil-birth-cert", "label": "Birth Certificate", "phase": "enrollment"},
        ],
    },
    "retiring": {
        "name": "Retiring",
        "icon": "rocking-chair",
        "description": "Calculate your pension, update your tax status, and secure your benefits.",
        "steps": [
            {"order": 1, "ministry": "social", "service_id": "social-retirement-est", "label": "Pension Estimate", "phase": "calculation"},
            {"order": 2, "ministry": "social", "service_id": "social-attestation", "label": "Contribution History", "phase": "calculation"},
            {"order": 3, "ministry": "finance", "service_id": "finance-declaration-copy", "label": "Last Tax Declaration", "phase": "tax", "details": {"year": "2024"}},
            {"order": 4, "ministry": "defense", "service_id": "def-service-cert", "label": "Military Service Proof", "phase": "documentation"},
            {"order": 5, "ministry": "health", "service_id": "health-vaccine-cert", "label": "Health Record", "phase": "documentation"},
        ],
    },
    "starting-a-business": {
        "name": "Starting a Business",
        "icon": "rocket",
        "description": "Get all clearances and registrations to launch your business.",
        "steps": [
            {"order": 1, "ministry": "justice", "service_id": "justice-b3", "label": "Criminal Record Clear", "phase": "clearance"},
            {"order": 2, "ministry": "finance", "service_id": "finance-tax-clearance", "label": "Tax Clearance", "phase": "clearance"},
            {"order": 3, "ministry": "social", "service_id": "social-attestation", "label": "Social Security Registration", "phase": "registration"},
            {"order": 4, "ministry": "civil", "service_id": "civil-residence-cert", "label": "Business Address Proof", "phase": "registration"},
        ],
    },
    "buying-property": {
        "name": "Buying Property",
        "icon": "house",
        "description": "Tax clearance, identity verification, and property registry check.",
        "steps": [
            {"order": 1, "ministry": "civil", "service_id": "civil-birth-cert", "label": "Identity Verification", "phase": "verification"},
            {"order": 2, "ministry": "finance", "service_id": "finance-tax-clearance", "label": "Tax Clearance", "phase": "clearance"},
            {"order": 3, "ministry": "finance", "service_id": "finance-income-cert", "label": "Income Proof", "phase": "clearance", "details": {"year": "2024"}},
            {"order": 4, "ministry": "property", "service_id": "property-no-ownership", "label": "Current Property Status", "phase": "registry"},
        ],
    },
    "death-of-relative": {
        "name": "Death of a Relative",
        "icon": "candle",
        "description": "Handle inheritance, benefits, and administrative updates during a difficult time.",
        "steps": [
            {"order": 1, "ministry": "civil", "service_id": "civil-family-cert", "label": "Family Certificate", "phase": "documentation"},
            {"order": 2, "ministry": "social", "service_id": "social-attestation", "label": "Benefits Status", "phase": "benefits"},
            {"order": 3, "ministry": "property", "service_id": "property-ownership", "label": "Property Registry Check", "phase": "inheritance", "details": {"property_id": "ALL"}},
            {"order": 4, "ministry": "finance", "service_id": "finance-declaration-copy", "label": "Tax Records", "phase": "inheritance", "details": {"year": "2024"}},
        ],
    },
}
