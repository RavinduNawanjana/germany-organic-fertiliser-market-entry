from dataclasses import replace
from math import isclose,nan
import pytest
from fertiliser_screen.model import ImportCase,calculate,freight_fx_grid
from fertiliser_screen.evidence import Requirement,screen_evidence,REQUIREMENTS

@pytest.fixture
def case():return ImportCase(10000,1,.9,2000,500,.04,1000,.1,1.7,3000)

def test_cost_math(case):
    x=calculate(case)
    assert isclose(x['cif_proxy_eur'],11000)
    assert isclose(x['illustrative_duty_eur'],440)
    assert isclose(x['landed_eur_total'],13940)
    assert isclose(x['unit_contribution_eur_kg'],1.7-1.394)
    assert x['breakeven_kg_at_given_unit_contribution']>0
    assert isclose(x['fixed_shipment_costs_eur'],3580)
    assert isclose(x['variable_cost_eur_kg'],1.036)
    assert isclose(x['breakeven_kg_at_given_unit_contribution'],6580/(1.7-1.036))

def test_negative_margin_is_no_break_even(case):
    x=calculate(replace(case,wholesale_price_eur_kg=.1))
    assert x['breakeven_kg_at_given_unit_contribution'] is None

def test_zero_duty(case):
    a=calculate(replace(case,customs_duty_fraction=0))
    b=calculate(case)
    assert b['landed_eur_total']>a['landed_eur_total']

@pytest.mark.parametrize('field,number',[('volume_kg',0),('volume_kg',-1),
    ('eur_per_usd',0),('eur_per_usd',nan),('customs_duty_fraction',1.2),
    ('freight_and_insurance_eur_total',-1),('data_status','VERIFIED')])
def test_bad_economics(case,field,number):
    with pytest.raises(ValueError):replace(case,**{field:number})

def test_no_compliance_claim(case):
    assert calculate(case)['regulatory_status'].startswith('NOT ASSESSED')

def test_fx_grid(case):
    assert len(freight_fx_grid(case,[1,2],[.9,1]))==4

def test_evidence_gaps():
    z=screen_evidence([Requirement('market_route','unreviewed')])
    assert 'product_function_category' in z['missing_requirements']
    assert not z['ready_for_regulatory_specialist_review']

def test_review_evidence_needed():
    with pytest.raises(ValueError):Requirement('market_route','expert_reviewed')

def test_duplicate_evidence():
    with pytest.raises(ValueError):screen_evidence([Requirement('market_route','unreviewed')]*2)

def test_no_false_compliance_even_fully_reviewed():
    rows=[Requirement(r,'expert_reviewed','evidence://record','specialist','2026-10-03') for r in REQUIREMENTS]
    x=screen_evidence(rows)
    assert x['ready_for_regulatory_specialist_review']
    assert x['legal_conformity'].startswith('UNDETERMINED')
