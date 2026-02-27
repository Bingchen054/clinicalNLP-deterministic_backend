from typing import Dict, Any, List


def _get(d: Dict[str, Any], key: str, default=None):
    if not d:
        return default
    return d.get(key, default)


# =====================================================
# HIGH-FIDELITY REVISED HPI TEMPLATE
# =====================================================

def generate_revised_hpi(original_note: str,
                         features: Dict[str, Any],
                         results: Dict[str, Any]) -> str:
    """
    Deterministic Revised HPI aligned with payer-style inpatient documentation.
    Designed to mirror formal utilization review narrative structure.
    """

    paragraphs: List[str] = []

    # -------------------------------------------------
    # 1️⃣ Demographics + Chief Complaint
    # -------------------------------------------------

    age = _get(features, "age")
    gender = _get(features, "gender")
    comorbs = _get(features, "comorbidities", []) or []
    duration = _get(features, "symptom_duration_days")
    symptoms = _get(features, "symptoms", []) or []

    intro_parts = []

    if age and gender:
        intro_parts.append(f"The patient is an {age}-year-old {gender}")
    elif age:
        intro_parts.append(f"The patient is an {age}-year-old individual")
    else:
        intro_parts.append("The patient")

    if comorbs:
        intro_parts.append(f"with a history of {', '.join(comorbs)}")

    intro_sentence = " ".join(intro_parts)

    if duration:
        intro_sentence += f" who presented to the emergency department with a {duration}-day history of respiratory symptoms."
    else:
        intro_sentence += " who presented to the emergency department with progressive respiratory symptoms."

    paragraphs.append(intro_sentence)

    # -------------------------------------------------
    # 2️⃣ Symptom progression / outpatient failure
    # -------------------------------------------------

    outpatient_fail = bool(_get(features, "outpatientFailure", False))

    if symptoms:
        symptom_text = ", ".join(symptoms)
        symptom_sentence = f"Per documentation, symptoms included {symptom_text}"
        if duration:
            symptom_sentence += f" for approximately {duration} days"
        symptom_sentence += " and were progressively worsening."
        paragraphs.append(symptom_sentence)

    if outpatient_fail:
        paragraphs.append(
            "Per documentation, the patient had been treated in the outpatient setting; however, symptoms worsened despite recent therapy, consistent with failure of outpatient management."
        )

    # -------------------------------------------------
    # 3️⃣ Emergency Department Findings
    # -------------------------------------------------

    vitals = _get(features, "vitals", {}) or {}
    lowest_spo2 = _get(features, "lowest_spo2")
    oxygen_req = bool(_get(features, "oxygenRequirement", False))
    oxygen_flow = _get(features, "oxygen_flow")

    ed_lines = []

    if lowest_spo2 is not None:
        ed_lines.append(
            f"Emergency department monitoring demonstrated oxygen desaturation to {lowest_spo2}%."
        )

    if oxygen_req:
        if oxygen_flow:
            ed_lines.append(
                f"Supplemental oxygen via {oxygen_flow} was required to maintain adequate oxygen saturation."
            )
        else:
            ed_lines.append(
                "Supplemental oxygen was required to maintain adequate oxygen saturation."
            )

    # Imaging
    imaging = _get(features, "imagingFindings", []) or []
    pneumonia_location = _get(features, "pneumonia_location")

    if imaging:
        if pneumonia_location:
            ed_lines.append(
                f"Chest imaging demonstrated findings consistent with {pneumonia_location} pneumonia."
            )
        else:
            ed_lines.append(
                "Chest imaging demonstrated findings consistent with pneumonia."
            )

    # Labs
    labs = _get(features, "labs", {}) or {}
    wbc = labs.get("wbc")
    neut = labs.get("neutrophils_percent")

    if wbc is not None:
        if neut is not None:
            ed_lines.append(
                f"Laboratory evaluation revealed leukocytosis with neutrophilic predominance, with a white blood cell count of {float(wbc)} and neutrophils at {float(neut)}%, consistent with an acute bacterial infectious process."
            )
        else:
            ed_lines.append(
                f"Laboratory evaluation revealed leukocytosis with a white blood cell count of {float(wbc)}, supporting an acute infectious process."
            )

    if _get(features, "iv_antibiotics", False):
        ed_lines.append(
            "Broad-spectrum intravenous antibiotics were initiated in the emergency department."
        )

    if ed_lines:
        paragraphs.append(" ".join(ed_lines))

    # -------------------------------------------------
    # 4️⃣ Inpatient Medical Necessity Summary
    # -------------------------------------------------

    summary_components: List[str] = []

    if lowest_spo2 is not None and lowest_spo2 < 90:
        summary_components.append("documented hypoxemia requiring supplemental oxygen")

    if imaging:
        if pneumonia_location:
            summary_components.append(f"imaging findings consistent with {pneumonia_location} pneumonia")
        else:
            summary_components.append("radiographic evidence of pneumonia")

    if outpatient_fail:
        summary_components.append("failure of outpatient therapy")

    if wbc is not None:
        summary_components.append("laboratory evidence of bacterial infection")

    if summary_components:
        paragraphs.append(
            "In summary, this patient demonstrates "
            + ", ".join(summary_components)
            + ", warranting inpatient-level management."
        )

    revised_body = "\n\n".join(paragraphs)

    return f"""Revised HPI

{revised_body}
"""


# =====================================================
# OPTIONAL COMPACT SUMMARY
# =====================================================

def generate_compact_summary(features: Dict[str, Any],
                             results: Dict[str, Any]) -> str:
    triggers = results.get("triggers", []) or []
    severity = results.get("severityScore", "N/A")
    level = results.get("level", "Undetermined")

    return f"""MCG Admission Summary

Triggers Met: {", ".join(triggers) if triggers else "None"}
Severity Score: {severity}
Determination: {level}
"""


# =====================================================
# SAFE FALLBACK
# =====================================================

def generate_safe_output(original_note: str) -> str:
    return f"""Revised HPI

Insufficient structured data available to reconstruct a payer-aligned narrative.

--- Original Documentation ---
{original_note}
"""