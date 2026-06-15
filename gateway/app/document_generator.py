"""
Document generator — creates structured official documents from citizen data.
The frontend renders these as printable pages.
"""

from datetime import datetime, date, timedelta
import uuid

from .services_catalog import MINISTRY_LABELS


def generate_reference(ministry: str, cin: str) -> str:
    ts = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    short = str(uuid.uuid4())[:6].upper()
    return f"{ministry.upper()}-{cin}-{ts}-{short}"


def generate_document(
    service_id: str,
    citizen: dict,
    ministry: str,
    ministry_data: dict | None,
    details: dict,
) -> dict:
    """Build the document content JSON. Returns the full document payload."""

    ministry_label = MINISTRY_LABELS.get(ministry, ministry.title())
    now = datetime.utcnow()
    ref = generate_reference(ministry, citizen["cin"])

    # Base document structure
    doc = {
        "header": {
            "country": "StateSync Republic",
            "ministry": f"Ministry of {ministry_label}",
            "emblem": "OFFICIAL DOCUMENT",
        },
        "reference": ref,
        "issued_date": now.strftime("%Y-%m-%d"),
        "issued_at": now.isoformat(),
        "citizen": {
            "full_name": citizen["full_name"],
            "cin": citizen["cin"],
            "birth_date": citizen["birth_date"],
            "nationality": citizen["nationality"],
        },
        "title": "",
        "sections": [],
        "valid_until": None,
        "verification_url": f"https://statesync.gov/verify/{ref}",
        "footer": "This document was generated electronically via StateSync and is legally valid. Any alteration renders it void.",
    }

    # ── Certificate templates ────────────────────────

    if service_id == "civil-birth-cert":
        doc["title"] = "Birth Certificate"
        doc["sections"] = [
            {"heading": "Civil Registry Extract", "fields": [
                ("Full Name", citizen["full_name"]),
                ("Date of Birth", citizen["birth_date"]),
                ("Nationality", citizen["nationality"]),
                ("CIN", citizen["cin"]),
            ]},
        ]
        if ministry_data:
            doc["sections"].append({"heading": "Registered Address", "fields": [
                ("Address", ministry_data.get("address", "N/A")),
            ]})

    elif service_id == "civil-family-cert":
        doc["title"] = "Family Composition Certificate"
        doc["sections"] = [
            {"heading": "Head of Household", "fields": [
                ("Full Name", citizen["full_name"]),
                ("CIN", citizen["cin"]),
            ]},
        ]
        if ministry_data:
            doc["sections"].append({"heading": "Family Details", "fields": [
                ("Marital Status", ministry_data.get("marital_status", "N/A")),
                ("Number of Children", str(ministry_data.get("children_count", 0))),
                ("Address", ministry_data.get("address", "N/A")),
            ]})

    elif service_id == "civil-residence-cert":
        doc["title"] = "Certificate of Residence"
        doc["sections"] = [{"heading": "Residence Information", "fields": [
            ("Full Name", citizen["full_name"]),
            ("CIN", citizen["cin"]),
            ("Registered Address", ministry_data.get("address", "N/A") if ministry_data else "N/A"),
        ]}]
        doc["footer"] = "This certifies the above-named person resides at the stated address. " + doc["footer"]

    elif service_id == "justice-b3":
        doc["title"] = "Criminal Record Extract — Bulletin N.3"
        status = ministry_data.get("criminal_record_status", "N/A") if ministry_data else "N/A"
        doc["sections"] = [
            {"heading": "Criminal Record", "fields": [
                ("Full Name", citizen["full_name"]),
                ("CIN", citizen["cin"]),
                ("Date of Birth", citizen["birth_date"]),
                ("Record Status", status),
            ]},
            {"heading": "Declaration", "text": f"The criminal record of {citizen['full_name']} (CIN: {citizen['cin']}) shows status: {status}. This extract is issued for administrative and legal purposes."},
        ]
        doc["valid_until"] = (now + timedelta(days=90)).strftime("%Y-%m-%d")

    elif service_id == "def-service-cert":
        doc["title"] = "Military Service Certificate"
        ms = ministry_data.get("military_status", "N/A") if ministry_data else "N/A"
        cd = ministry_data.get("completion_date") if ministry_data else None
        doc["sections"] = [{"heading": "Military Service Record", "fields": [
            ("Full Name", citizen["full_name"]),
            ("CIN", citizen["cin"]),
            ("Military Status", ms),
            ("Completion Date", cd or "N/A"),
        ]}]

    elif service_id == "health-vaccine-cert":
        doc["title"] = "Vaccination Certificate"
        doc["sections"] = [{"heading": "Citizen", "fields": [
            ("Full Name", citizen["full_name"]),
            ("CIN", citizen["cin"]),
            ("Blood Type", ministry_data.get("blood_type", "N/A") if ministry_data else "N/A"),
        ]}]
        if ministry_data and ministry_data.get("vaccinations"):
            rows = []
            for v in ministry_data["vaccinations"]:
                rows.append(f"{v.get('name', '?')} — {v.get('doses', '?')} dose(s) — {v.get('date', '?')}")
            doc["sections"].append({"heading": "Vaccination Record", "list": rows})
        doc["valid_until"] = (now + timedelta(days=365)).strftime("%Y-%m-%d")

    elif service_id == "finance-declaration-copy":
        year = details.get("year", now.year - 1)
        doc["title"] = f"Tax Declaration Copy — {year}"
        doc["sections"] = [{"heading": "Taxpayer", "fields": [
            ("Full Name", citizen["full_name"]),
            ("Tax ID", ministry_data.get("tax_id", "N/A") if ministry_data else "N/A"),
            ("Tax Status", ministry_data.get("tax_status", "N/A") if ministry_data else "N/A"),
        ]}]
        if ministry_data:
            for dec in ministry_data.get("annual_declarations", []):
                if dec.get("year") == int(year):
                    doc["sections"].append({"heading": f"Declaration {year}", "fields": [
                        ("Declared Income", f"{dec['income']:,}"),
                        ("Tax Paid", f"{dec['tax_paid']:,}"),
                    ]})

    elif service_id == "finance-income-cert":
        year = details.get("year", now.year - 1)
        doc["title"] = f"Income Certificate — {year}"
        doc["sections"] = [{"heading": "Income Declaration", "fields": [
            ("Full Name", citizen["full_name"]),
            ("Tax ID", ministry_data.get("tax_id", "N/A") if ministry_data else "N/A"),
        ]}]
        if ministry_data:
            for dec in ministry_data.get("annual_declarations", []):
                if dec.get("year") == int(year):
                    doc["sections"].append({"heading": "Certified Income", "fields": [
                        ("Year", str(year)),
                        ("Total Income", f"{dec['income']:,}"),
                    ]})

    elif service_id == "social-attestation":
        doc["title"] = "Social Security Attestation"
        doc["sections"] = [{"heading": "Social Security Record", "fields": [
            ("Full Name", citizen["full_name"]),
            ("SS Number", ministry_data.get("social_security_number", "N/A") if ministry_data else "N/A"),
            ("Retirement Status", ministry_data.get("retirement_status", "N/A") if ministry_data else "N/A"),
        ]}]
        if ministry_data and ministry_data.get("benefits"):
            for b in ministry_data["benefits"]:
                doc["sections"].append({"heading": "Active Benefit", "fields": [
                    ("Type", b.get("type", "N/A")),
                    ("Amount", f"{b.get('amount', 0)} {b.get('currency', '')} / {b.get('frequency', '')}"),
                ]})

    elif service_id == "interior-residence-cert":
        doc["title"] = "Residence Registration Certificate"
        doc["sections"] = [{"heading": "Registration", "fields": [
            ("Full Name", citizen["full_name"]),
            ("Passport", ministry_data.get("passport_number", "N/A") if ministry_data else "N/A"),
            ("Residence Permit", ministry_data.get("residence_permit", "N/A") if ministry_data else "N/A"),
            ("Permit Expiry", ministry_data.get("permit_expiry", "N/A") if ministry_data else "N/A"),
        ]}]

    elif service_id == "transport-vehicle-cert":
        plate = details.get("vehicle_plate", "")
        doc["title"] = f"Vehicle Registration Certificate"
        doc["sections"] = [{"heading": "Owner", "fields": [
            ("Full Name", citizen["full_name"]),
            ("License", ministry_data.get("license_number", "N/A") if ministry_data else "N/A"),
        ]}]
        if ministry_data:
            for v in ministry_data.get("vehicles", []):
                if v.get("plate", "").upper() == plate.upper() or not plate:
                    doc["sections"].append({"heading": "Vehicle", "fields": [
                        ("Plate", v.get("plate", "N/A")),
                        ("Make", v.get("make", "N/A")),
                        ("Model", v.get("model", "N/A")),
                        ("Year", str(v.get("year", "N/A"))),
                    ]})

    elif service_id == "transport-driving-record":
        doc["title"] = "Official Driving Record"
        doc["sections"] = [{"heading": "License Information", "fields": [
            ("Full Name", citizen["full_name"]),
            ("License Number", ministry_data.get("license_number", "N/A") if ministry_data else "N/A"),
            ("Category", ministry_data.get("license_category", "N/A") if ministry_data else "N/A"),
            ("Expiry", ministry_data.get("license_expiry", "N/A") if ministry_data else "N/A"),
        ]}, {"heading": "Infractions", "text": "No infractions on record."}]

    elif service_id == "commerce-registration":
        doc["title"] = "Business Registration Certificate"
        doc["sections"] = [{"heading": "Owner", "fields": [
            ("Full Name", citizen["full_name"]),
            ("CIN", citizen["cin"]),
        ]}]
        if ministry_data:
            for b in ministry_data.get("businesses", []):
                doc["sections"].append({"heading": "Registered Business", "fields": [
                    ("Business Name", b.get("name", "N/A")),
                    ("Registration ID", b.get("registration_id", "N/A")),
                    ("Type", b.get("type", "N/A")),
                    ("Status", b.get("status", "N/A")),
                    ("Founded", str(b.get("founded", "N/A"))),
                ]})

    elif service_id == "property-no-ownership":
        doc["title"] = "Non-Ownership Certificate"
        has_properties = bool(ministry_data and ministry_data.get("properties"))
        if has_properties:
            doc["sections"] = [{"heading": "Notice", "text": "This citizen has registered properties. A non-ownership certificate cannot be issued."}]
        else:
            doc["sections"] = [{"heading": "Declaration", "text": f"We hereby certify that {citizen['full_name']} (CIN: {citizen['cin']}) has no registered property in the national land registry."}]

    elif service_id == "employ-unemployment":
        doc["title"] = "Unemployment Attestation"
        status = ministry_data.get("employment_status", "N/A") if ministry_data else "N/A"
        doc["sections"] = [{"heading": "Employment Status", "fields": [
            ("Full Name", citizen["full_name"]),
            ("Current Status", status),
        ]}]
        doc["valid_until"] = (now + timedelta(days=30)).strftime("%Y-%m-%d")

    elif service_id == "employ-work-history":
        doc["title"] = "Work History Certificate"
        doc["sections"] = [{"heading": "Citizen", "fields": [
            ("Full Name", citizen["full_name"]),
            ("Current Status", ministry_data.get("employment_status", "N/A") if ministry_data else "N/A"),
            ("Current Employer", ministry_data.get("current_employer", "N/A") if ministry_data else "N/A"),
        ]}]
        if ministry_data and ministry_data.get("contracts"):
            for c in ministry_data["contracts"]:
                doc["sections"].append({"heading": c.get("role", "Position"), "fields": [
                    ("Employer", c.get("employer", "N/A")),
                    ("Type", c.get("type", "N/A")),
                    ("Period", f"{c.get('start_date', '?')} to {c.get('end_date') or 'present'}"),
                ]})

    elif service_id == "edu-transcript":
        doc["title"] = "Academic Transcript"
        doc["sections"] = [{"heading": "Student", "fields": [
            ("Full Name", citizen["full_name"]),
            ("CIN", citizen["cin"]),
        ]}]
        if ministry_data:
            for d in ministry_data.get("diplomas", []):
                doc["sections"].append({"heading": "Diploma", "fields": [
                    ("Title", d.get("title", "N/A")),
                    ("Institution", d.get("institution", "N/A")),
                    ("Year", str(d.get("year", "N/A"))),
                ]})

    else:
        # Generic document for any service not specifically templated
        doc["title"] = f"Official Certificate"
        doc["sections"] = [
            {"heading": "Citizen Information", "fields": [
                ("Full Name", citizen["full_name"]),
                ("CIN", citizen["cin"]),
                ("Date of Birth", citizen["birth_date"]),
            ]},
        ]
        if ministry_data:
            fields = [(k.replace("_", " ").title(), str(v)) for k, v in ministry_data.items() if k != "cin"]
            doc["sections"].append({"heading": f"Ministry of {ministry_label} — Records", "fields": fields})

    return doc
