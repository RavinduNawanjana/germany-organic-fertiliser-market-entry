"""Requirement is not compliant until legally determined: software never makes that judgment."""
from dataclasses import dataclass

REQUIREMENTS={'market_route','product_function_category','component_material_category',
              'formulation_identity','nutrient_laboratory_report','contaminant_report',
              'microbiology_report','labelling','conformity_assessment_route',
              'importer_responsibility','national_requirements','organic_use_claim_support'}
ALLOWED={'unreviewed','evidence_requested','document_provided_unverified',
         'expert_reviewed'}

@dataclass(frozen=True)
class Requirement:
    requirement:str
    review_status:str
    evidence_locator:str=''
    reviewer_name:str=''
    review_date:str=''
    observation:str=''
    def __post_init__(self):
        if self.requirement not in REQUIREMENTS:raise ValueError('unknown screening requirement')
        if self.review_status not in ALLOWED:raise ValueError('unknown evidence status')
        if self.review_status in {'document_provided_unverified','expert_reviewed'} and not self.evidence_locator:
            raise ValueError('Evidence-locator required for supplied documentation')
        if self.review_status=='expert_reviewed' and not (self.reviewer_name and self.review_date):
            raise ValueError('Review status requires reviewer and date')


def screen_evidence(rows:list[Requirement])->dict:
    if len(set(x.requirement for x in rows))!=len(rows):raise ValueError('duplicate requirement')
    present={r.requirement for r in rows}
    missing=sorted(REQUIREMENTS-present)
    outstanding=sorted(r.requirement for r in rows if r.review_status!='expert_reviewed')
    # Even with complete documents, specialist legal/technical compliance signoff is NOT inferred.
    return dict(requirements_expected=len(REQUIREMENTS),requirements_registered=len(rows),
                missing_requirements=missing,not_expert_reviewed=outstanding,
                ready_for_regulatory_specialist_review=not missing and not outstanding,
                legal_conformity='UNDETERMINED — FORMAL ASSESSMENT REQUIRED')
