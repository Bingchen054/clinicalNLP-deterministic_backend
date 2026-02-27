from typing import Dict, List, Any, Union
from alignment_types import ClinicalData, EvaluatedCriterion


def _get(d: Union[dict, object], name: str, default=None):
    if d is None:
        return default
    if isinstance(d, dict):
        return d.get(name, default)
    return getattr(d, name, default)


def _format_list(items: List[str]) -> str:
    if not items:
        return ""
    if len(items) == 1:
        return items[0]
    return ", ".join(items[:-1]) + f", and {items[-1]}"


def build_justification(
    clinical_data: ClinicalData,
    evaluated: List[EvaluatedCriterion],
    decision: Dict[str, Any]
) -> Dict[str, str]:

    age = _get(clinical_data, "age")
    gender = _get(clinical_data, "gender")
    symptoms = _get(clinical_data, "symptoms") or []
    duration = _get(clinical_data, "symptom_duration_days")
    labs = _get(clinical_data, "labs") or {}
    imaging = _get(clinical_data, "imagingFindings") or []
    comorbs = _get(clinical_data, "comorbidities") or []
    lowest_spo2 = _get(clinical_data, "lowest_spo2")
    oxyreq = _get(clinical_data, "oxygenRequirement", False)
    iv_abx = _get(clinical_data, "iv_antibiotics", False)

    total_score = decision.get("totalScore")

    paragraphs: List[str] = []

    # ---------------------------------------------------
    # 1️⃣ Demographics + Chief Complaint
    # ---------------------------------------------------

    if age and gender:
        intro = f"The patient is an {age}-year-old {gender}"
    elif age:
        intro = f"The patient is an {age}-year-old individual"
    else:
        intro = "The patient"

    if comorbs:
        intro += f" with a history of {_format_list(comorbs)}"

    if duration:
        intro += f" who presented to the emergency department with a {duration}-day history of respiratory symptoms."
    else:
        intro += " who presented to the emergency department with progressive respiratory symptoms."

    intro += (
        " The patient sought emergency evaluation due to ongoing symptom progression "
        "and concern for worsening respiratory status."
    )

    paragraphs.append(intro)

    # ---------------------------------------------------
    # 2️⃣ Symptom Progression
    # ---------------------------------------------------

    if symptoms:
        symptom_text = _format_list(symptoms)
        if duration:
            paragraphs.append(
                f"Per documentation, symptoms including {symptom_text} had been present for approximately {duration} days "
                f"and were progressively worsening despite conservative measures. "
                "The progressive nature of symptoms raised concern for an evolving lower respiratory tract infection."
            )
        else:
            paragraphs.append(
                f"Per documentation, symptoms included {symptom_text} with progressive worsening, "
                "suggesting an acute infectious or inflammatory respiratory process."
            )

    # ---------------------------------------------------
    # 3️⃣ Emergency Department Findings
    # ---------------------------------------------------

    ed_lines = []

    if lowest_spo2 is not None:
        ed_lines.append(
            f"Emergency department monitoring demonstrated oxygen desaturation to {lowest_spo2}%, "
            "indicating objective hypoxemia at the time of presentation."
        )

    if oxyreq:
        ed_lines.append(
            "Supplemental oxygen therapy was required to restore and maintain adequate oxygen saturation, "
            "reflecting clinically significant respiratory compromise."
        )

    if ed_lines:
        paragraphs.append(" ".join(ed_lines))

    # ---------------------------------------------------
    # 4️⃣ Imaging and Laboratory Findings
    # ---------------------------------------------------

    objective_lines = []

    if imaging:
        objective_lines.append(
            f"Chest imaging demonstrated findings consistent with {_format_list(imaging)}, "
            "supporting the diagnosis of an acute pulmonary infectious process."
        )

    if labs.get("wbc") is not None:
        if labs.get("neutrophils_percent") is not None:
            objective_lines.append(
                f"Laboratory evaluation revealed leukocytosis with neutrophilic predominance, "
                f"with a white blood cell count of {labs.get('wbc')} and neutrophils at {labs.get('neutrophils_percent')}%, "
                "findings consistent with an acute bacterial infectious process."
            )
        else:
            objective_lines.append(
                f"Laboratory evaluation revealed leukocytosis with a white blood cell count of {labs.get('wbc')}, "
                "supporting the presence of systemic inflammatory response."
            )

    if iv_abx:
        objective_lines.append(
            "Given the severity of presentation, broad-spectrum intravenous antibiotics were initiated "
            "in the emergency department for empiric treatment of suspected bacterial pneumonia."
        )

    if objective_lines:
        paragraphs.append(" ".join(objective_lines))

    # ---------------------------------------------------
    # 5️⃣ Medical Necessity Summary
    # ---------------------------------------------------

    summary_components = []

    if lowest_spo2 is not None and lowest_spo2 < 90:
        summary_components.append("documented hypoxemia requiring supplemental oxygen")

    if imaging:
        summary_components.append("radiographic evidence of pneumonia")

    if labs.get("wbc") is not None:
        summary_components.append("laboratory evidence of bacterial infection")

    if summary_components:
        paragraphs.append(
            "In summary, this elderly patient demonstrates "
            + ", ".join(summary_components)
            + ", in the setting of progressive respiratory symptoms. "
            "These findings collectively support the need for inpatient-level monitoring and management."
        )

    clinical_summary = "\n\n".join(paragraphs)

    # ---------------------------------------------------
    # Conclusion
    # ---------------------------------------------------

    if total_score is not None:
        conclusion = (
            f"Overall admission severity score is estimated at {total_score}%. "
            "Based on objective clinical findings and risk profile, inpatient admission is medically appropriate."
        )
    else:
        conclusion = (
            "Based on the combination of objective respiratory compromise, imaging findings, "
            "and laboratory abnormalities, inpatient-level care is medically appropriate."
        )

    return {
        "clinicalSummary": clinical_summary,
        "medicalNecessityJustification": "",
        "riskStratification": "",
        "conclusion": conclusion,
    }