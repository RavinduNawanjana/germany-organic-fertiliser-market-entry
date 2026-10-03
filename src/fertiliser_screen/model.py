"""Illustrative international unit economics and regulatory evidence gates."""
from __future__ import annotations
from dataclasses import dataclass,replace
from math import isfinite


def nonnegative(x,name):
    if not isfinite(float(x)) or x < 0:raise ValueError(name+' must be finite and nonnegative')
    return float(x)

@dataclass(frozen=True)
class ImportCase:
    volume_kg:float
    production_cost_usd_kg:float
    eur_per_usd:float
    freight_and_insurance_eur_total:float
    port_handling_eur_total:float
    customs_duty_fraction:float
    testing_and_conformity_eur_total:float
    warehousing_eur_kg:float
    wholesale_price_eur_kg:float
    fixed_market_launch_eur:float
    data_status:str='ILLUSTRATIVE'

    def __post_init__(self):
        for key in ('volume_kg','production_cost_usd_kg','eur_per_usd',
                    'freight_and_insurance_eur_total','port_handling_eur_total',
                    'customs_duty_fraction','testing_and_conformity_eur_total',
                    'warehousing_eur_kg','wholesale_price_eur_kg','fixed_market_launch_eur'):
            nonnegative(getattr(self,key),key)
        if self.volume_kg<=0 or self.eur_per_usd<=0:raise ValueError('Volume and FX must be positive')
        if self.customs_duty_fraction>1:raise ValueError('Duty scenario must be a fraction')
        if self.data_status!='ILLUSTRATIVE':raise ValueError('Scenario is not a real quotation')


def calculate(c:ImportCase)->dict:
    """Hypothetical non-tax landed cash cost, not a customs classification assessment."""
    product_eur = c.volume_kg * c.production_cost_usd_kg * c.eur_per_usd
    cif_proxy_eur=product_eur+c.freight_and_insurance_eur_total
    # Demonstration only: actual customs valuation and duties depend on product code and facts.
    duty=cif_proxy_eur*c.customs_duty_fraction
    landed=(cif_proxy_eur+duty+c.port_handling_eur_total+
            c.testing_and_conformity_eur_total+c.volume_kg*c.warehousing_eur_kg)
    unit_cost=landed/c.volume_kg
    contribution=c.wholesale_price_eur_kg-unit_cost
    # Break-even at variable unit contribution, with one shipment's fixed costs
    # counted once. Allocating fixed costs into unit_cost is appropriate at
    # current volume but NOT for solving the break-even volume.
    variable_unit=(c.production_cost_usd_kg*c.eur_per_usd*
                   (1+c.customs_duty_fraction)+c.warehousing_eur_kg)
    fixed_ship=(c.freight_and_insurance_eur_total*(1+c.customs_duty_fraction)+
                c.port_handling_eur_total+c.testing_and_conformity_eur_total)
    variable_contribution=c.wholesale_price_eur_kg-variable_unit
    breakeven=None if variable_contribution<=0 else (c.fixed_market_launch_eur+fixed_ship)/variable_contribution
    gross_contribution=c.volume_kg*contribution
    scenario_profit=gross_contribution-c.fixed_market_launch_eur
    return dict(data_status=c.data_status,volume_kg=c.volume_kg,
                cif_proxy_eur=cif_proxy_eur,illustrative_duty_eur=duty,
                landed_eur_total=landed,landed_eur_per_kg=unit_cost,
                wholesale_price_eur_kg=c.wholesale_price_eur_kg,
                unit_contribution_eur_kg=contribution,
                variable_cost_eur_kg=variable_unit,
                fixed_shipment_costs_eur=fixed_ship,
                incremental_contribution_eur_kg=variable_contribution,
                contribution_eur=gross_contribution,
                launch_cost_eur=c.fixed_market_launch_eur,
                illustrative_operating_result_eur=scenario_profit,
                breakeven_kg_at_given_unit_contribution=breakeven,
                regulatory_status='NOT ASSESSED — NO COMPLIANCE DECISION')


def freight_fx_grid(case:ImportCase,freight_factors,fx_rates)->list[dict]:
    out=[]
    for freight in freight_factors:
        for fx in fx_rates:
            variant=replace(case,freight_and_insurance_eur_total=nonnegative(float(freight),'freight'),
                            eur_per_usd=nonnegative(float(fx),'fx'))
            out.append(calculate(variant)|{'hypothetical_freight_eur':freight,
                                          'hypothetical_eur_per_usd':fx})
    return out
