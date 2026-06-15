"""
Smart Assistant — rule-based engine that analyzes citizen data
and produces personalized recommendations, reminders, and completeness scores.
"""

from datetime import datetime, date

# ── Helpers ──────────────────────────────────────


def _days_until(d: str | None) -> int | None:
    if not d:
        return None
    try:
        return (date.fromisoformat(str(d)) - date.today()).days
    except (ValueError, TypeError):
        return None


def _safe(ministry_data: dict | None, key: str, default=None):
    if not ministry_data or isinstance(ministry_data, str):
        return default
    if "error" in ministry_data:
        return default
    return ministry_data.get(key, default)


# ── Completeness Score ───────────────────────────


def compute_completeness(citizen: dict, ministries: dict) -> dict:
    """Calculate data completeness across all ministries."""
    checks = []

    # Personal info
    for field in ["full_name", "birth_date", "birth_place", "nationality", "phone"]:
        checks.append({
            "category": "Personal",
            "field": field.replace("_", " ").title(),
            "complete": bool(citizen.get(field)),
        })

    # Civil
    civil = ministries.get("civil")
    if civil and "error" not in str(civil):
        for f in ["address", "city", "marital_status", "parents"]:
            val = civil.get(f)
            complete = bool(val) and val != "{}" and val != "[]"
            checks.append({"category": "Civil Status", "field": f.replace("_", " ").title(), "complete": complete})
    else:
        checks.append({"category": "Civil Status", "field": "Civil record", "complete": False})

    # Education
    edu = ministries.get("education")
    if edu and "error" not in str(edu):
        checks.append({"category": "Education", "field": "Diplomas", "complete": bool(edu.get("diplomas"))})
    else:
        checks.append({"category": "Education", "field": "Education record", "complete": False})

    # Defense
    defense = ministries.get("defense")
    if defense and "error" not in str(defense):
        checks.append({"category": "Defense", "field": "Military status", "complete": bool(defense.get("military_status"))})
    else:
        checks.append({"category": "Defense", "field": "Defense record", "complete": False})

    # Health
    health = ministries.get("health")
    if health and "error" not in str(health):
        for f in ["blood_type", "vaccinations"]:
            val = health.get(f)
            checks.append({"category": "Health", "field": f.replace("_", " ").title(), "complete": bool(val) and val != "[]"})
        checks.append({"category": "Health", "field": "Organ donor declared", "complete": health.get("organ_donor") is not None})
    else:
        checks.append({"category": "Health", "field": "Health record", "complete": False})

    # Finance
    finance = ministries.get("finance")
    if finance and "error" not in str(finance):
        checks.append({"category": "Finance", "field": "Tax ID", "complete": bool(finance.get("tax_id"))})
        checks.append({"category": "Finance", "field": "Tax declarations", "complete": bool(finance.get("annual_declarations"))})
    else:
        checks.append({"category": "Finance", "field": "Finance record", "complete": False})

    # Social
    social = ministries.get("social")
    if social and "error" not in str(social):
        checks.append({"category": "Social", "field": "Social number", "complete": bool(social.get("social_number"))})
    else:
        checks.append({"category": "Social", "field": "Social record", "complete": False})

    # Transport
    transport = ministries.get("transport")
    if transport and "error" not in str(transport):
        dl = transport.get("driving_license", {})
        checks.append({"category": "Transport", "field": "Driving license", "complete": bool(dl.get("number"))})
    else:
        checks.append({"category": "Transport", "field": "Transport record", "complete": False})

    # Property
    prop = ministries.get("property")
    if prop and "error" not in str(prop):
        checks.append({"category": "Property", "field": "Property registry", "complete": True})
    else:
        checks.append({"category": "Property", "field": "Property record", "complete": False})

    # Justice
    justice = ministries.get("justice")
    if justice and "error" not in str(justice):
        checks.append({"category": "Justice", "field": "Criminal record", "complete": bool(justice.get("criminal_record"))})
    else:
        checks.append({"category": "Justice", "field": "Justice record", "complete": False})

    completed = sum(1 for c in checks if c["complete"])
    total = len(checks)

    return {
        "score": round(completed / total * 100) if total else 0,
        "completed": completed,
        "total": total,
        "checks": checks,
    }


# ── Proactive Reminders ─────────────────────────


def generate_reminders(citizen: dict, ministries: dict) -> list[dict]:
    """Generate smart reminders based on citizen data."""
    reminders = []
    today = date.today()

    # Passport / license expiry
    transport = ministries.get("transport")
    if transport and "error" not in str(transport):
        dl = transport.get("driving_license", {})
        days = _days_until(dl.get("expires"))
        if days is not None:
            if days < 0:
                reminders.append({"priority": "urgent", "icon": "car", "title": "License Expired",
                    "message": f"Your driving license expired {abs(days)} days ago. Renew immediately to avoid fines.",
                    "action": {"type": "service", "ministry": "transport", "service_id": "transport-license-renew"}})
            elif days < 90:
                reminders.append({"priority": "warning", "icon": "car", "title": "License Expiring Soon",
                    "message": f"Your driving license expires in {days} days.",
                    "action": {"type": "service", "ministry": "transport", "service_id": "transport-license-renew"}})

        # Vehicle inspection due
        for insp in transport.get("technical_inspections", []):
            days = _days_until(insp.get("next_due"))
            if days is not None and 0 < days < 60:
                reminders.append({"priority": "info", "icon": "wrench", "title": "Vehicle Inspection Due",
                    "message": f"Vehicle {insp.get('vehicle', '?')} inspection due in {days} days.",
                    "action": None})

    # Tax status
    finance = ministries.get("finance")
    if finance and "error" not in str(finance):
        if finance.get("tax_status") not in ("compliant", None):
            reminders.append({"priority": "urgent", "icon": "alert", "title": "Tax Issue",
                "message": f"Your tax status is '{finance.get('tax_status')}'. Contact the Ministry of Finance.",
                "action": {"type": "service", "ministry": "finance", "service_id": "finance-tax-clearance"}})

        # Unpaid fines
        unpaid = [f for f in finance.get("fines", []) if not f.get("paid")]
        if unpaid:
            total = sum(f.get("amount", 0) for f in unpaid)
            reminders.append({"priority": "urgent", "icon": "money", "title": f"{len(unpaid)} Unpaid Fine(s)",
                "message": f"You have {len(unpaid)} unpaid fine(s) totaling {total:,} USD.",
                "action": None})

        # Check if latest declaration is filed
        decls = finance.get("annual_declarations", [])
        unfiled = [d for d in decls if not d.get("filed")]
        if unfiled:
            years = [d.get("year") for d in unfiled]
            reminders.append({"priority": "warning", "icon": "file", "title": "Tax Declaration Due",
                "message": f"Year(s) {', '.join(str(y) for y in years)} not yet filed.",
                "action": {"type": "service", "ministry": "finance", "service_id": "finance-declaration-copy"}})

    # Health: vaccination freshness
    health = ministries.get("health")
    if health and "error" not in str(health):
        vaccines = health.get("vaccinations", [])
        if vaccines:
            latest = max(vaccines, key=lambda v: v.get("date", ""), default=None)
            if latest:
                days = _days_until(latest.get("date"))
                if days is not None and abs(days) > 730:
                    reminders.append({"priority": "info", "icon": "health", "title": "Vaccination Check",
                        "message": "Your last vaccination was over 2 years ago. Consider a health checkup.",
                        "action": {"type": "service", "ministry": "health", "service_id": "health-vaccine-cert"}})

        # Chronic conditions without recent checkup
        if health.get("chronic_diseases"):
            reminders.append({"priority": "info", "icon": "heart", "title": "Chronic Condition Monitoring",
                "message": f"You have {len(health['chronic_diseases'])} chronic condition(s). Regular checkups recommended.",
                "action": None})

    # Social: benefit eligibility
    social = ministries.get("social")
    civil = ministries.get("civil")
    if social and civil and "error" not in str(social) and "error" not in str(civil):
        children = civil.get("children", [])
        current_benefits = [b.get("type") for b in social.get("benefits", [])]
        if children and "Child benefit" not in current_benefits:
            reminders.append({"priority": "info", "icon": "gift", "title": "Eligible for Child Benefit",
                "message": f"You have {len(children)} child(ren) but no child benefit registered. You may be eligible.",
                "action": {"type": "service", "ministry": "social", "service_id": "social-benefit-claim"}})

    # Defense: deferred status check
    defense = ministries.get("defense")
    if defense and "error" not in str(defense):
        if defense.get("military_status") == "deferred":
            reminders.append({"priority": "info", "icon": "shield", "title": "Military Service Deferred",
                "message": "Your military service is deferred. It will be required after your studies end.",
                "action": None})

    # Age-based reminders
    birth = citizen.get("birth_date")
    if birth:
        try:
            age = (today - date.fromisoformat(str(birth))).days // 365
            if 58 <= age <= 62 and social:
                current_benefits_types = [b.get("type", "") for b in (social.get("benefits", []) if social and "error" not in str(social) else [])]
                if not any("pension" in b.lower() or "retirement" in b.lower() for b in current_benefits_types):
                    reminders.append({"priority": "warning", "icon": "sunset", "title": "Approaching Retirement",
                        "message": f"You are {age} years old. Consider requesting a retirement projection.",
                        "action": {"type": "life_event", "event_id": "retiring"}})
        except (ValueError, TypeError):
            pass

    # Sort by priority
    order = {"urgent": 0, "warning": 1, "info": 2}
    reminders.sort(key=lambda r: order.get(r["priority"], 9))
    return reminders


# ── Smart Assistant Suggestions ──────────────────


def generate_suggestions(citizen: dict, ministries: dict) -> list[dict]:
    """Context-aware suggestions based on citizen profile."""
    suggestions = []
    today = date.today()

    birth = citizen.get("birth_date")
    age = None
    if birth:
        try:
            age = (today - date.fromisoformat(str(birth))).days // 365
        except (ValueError, TypeError):
            pass

    civil = ministries.get("civil")
    education = ministries.get("education")
    defense = ministries.get("defense")
    health = ministries.get("health")
    justice = ministries.get("justice")
    finance = ministries.get("finance")
    social = ministries.get("social")
    transport = ministries.get("transport")
    prop = ministries.get("property")

    # Based on marital status
    marital = _safe(civil, "marital_status", "")
    if marital == "Single" and age and 25 <= age <= 45:
        suggestions.append({
            "category": "life", "title": "Planning to get married?",
            "message": "Use the 'Getting Married' life event to handle all paperwork automatically.",
            "action": {"type": "life_event", "event_id": "getting-married"},
        })

    # Based on employment
    unemployment = _safe(social, "unemployment_status", "")
    if unemployment in ("unemployed", "Unemployed"):
        suggestions.append({
            "category": "urgent", "title": "Unemployment Benefits",
            "message": "You appear to be unemployed. You may be eligible for unemployment benefits.",
            "action": {"type": "service", "ministry": "social", "service_id": "social-benefit-claim"},
        })

    # Based on education
    enrollment = _safe(education, "current_enrollment")
    if enrollment:
        suggestions.append({
            "category": "info", "title": "Student Services",
            "message": f"Currently enrolled: {enrollment}. Make sure your scholarship and military deferral are up to date.",
            "action": {"type": "life_event", "event_id": "starting-university"},
        })

    # Based on property + no mortgage (can get loan)
    properties = _safe(prop, "properties", [])
    mortgages = _safe(prop, "mortgages", [])
    if properties and not mortgages:
        suggestions.append({
            "category": "finance", "title": "Leverage Your Property",
            "message": f"You own {len(properties)} property(ies) with no mortgage. You could use them as collateral for a loan.",
            "action": {"type": "bundle", "bundle_id": "bank-loan"},
        })

    # Clean criminal record = can get sensitive jobs
    criminal = _safe(justice, "criminal_record", "")
    if criminal == "clean":
        suggestions.append({
            "category": "career", "title": "Clean Criminal Record",
            "message": "Your record is clean. You qualify for government and security positions.",
            "action": {"type": "service", "ministry": "justice", "service_id": "justice-b3"},
        })

    # Company ownership
    companies = _safe(finance, "company_ownerships", [])
    if companies:
        active = [c for c in companies if c.get("status") == "Active"]
        suggestions.append({
            "category": "business", "title": f"{len(active)} Active Business(es)",
            "message": "Keep your tax clearance and commercial registry up to date.",
            "action": {"type": "bundle", "bundle_id": "business-registration"},
        })

    # No driving license
    dl = _safe(transport, "driving_license", {})
    if not dl.get("number") and age and age >= 18:
        suggestions.append({
            "category": "info", "title": "No Driving License",
            "message": "You don't have a driving license on file. If you have one, make sure it's registered.",
            "action": None,
        })

    # Organ donor promotion
    organ_donor = _safe(health, "organ_donor", False)
    if not organ_donor:
        suggestions.append({
            "category": "health", "title": "Consider Becoming an Organ Donor",
            "message": "You are not registered as an organ donor. One donor can save up to 8 lives.",
            "action": None,
        })

    # Children approaching school age
    children = _safe(civil, "children", [])
    for child in children:
        child_birth = child.get("birth_date")
        if child_birth:
            try:
                child_age = (today - date.fromisoformat(str(child_birth))).days // 365
                if child_age == 5:
                    suggestions.append({
                        "category": "family", "title": f"School Enrollment for {child.get('name', 'your child')}",
                        "message": f"{child.get('name', 'Your child')} is turning 6 soon. Start school enrollment.",
                        "action": None,
                    })
            except (ValueError, TypeError):
                pass

    return suggestions
