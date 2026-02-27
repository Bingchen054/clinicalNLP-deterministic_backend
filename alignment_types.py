from dataclasses import dataclass, field
from typing import List, Dict, Optional


CriterionCategory = str  # "Respiratory"|"Imaging"|"Laboratory"|"Outpatient"|"Comorbidity"|"General"


@dataclass
class ExtractedCriterion:
    id: str
    text: str
    category: CriterionCategory


@dataclass
class ClinicalData:
    age: Optional[int] = None
    gender: Optional[str] = None

    # Use default_factory to avoid Python 3.14 type inference errors
    symptoms: List[str] = field(default_factory=list)
    vitals: Dict[str, float] = field(default_factory=dict)
    labs: Dict[str, float] = field(default_factory=dict)
    imagingFindings: List[str] = field(default_factory=list)
    comorbidities: List[str] = field(default_factory=list)

    oxygenRequirement: bool = False
    hypoxemia: bool = False
    lowest_spo2: Optional[int] = None
    iv_antibiotics: bool = False
    outpatientFailure: bool = False


@dataclass
class EvaluatedCriterion:
    criterionId: str
    criterionText: str
    category: CriterionCategory
    status: str  # "Met" | "Partial" | "Missing"
    evidenceFound: str
    suggestedLanguage: str
    scoreContribution: int


@dataclass
class AdmissionDecision:
    totalScore: int
    maxPossibleScore: int
    percentage: int
    admissionRecommended: bool


@dataclass
class AlignmentResult:
    extractedCriteria: List[ExtractedCriterion]
    revisedNotes: Dict[str, str]
    missingCriteria: List[EvaluatedCriterion]
    overallScore: int
    admissionRecommended: bool