from pathlib import Path
import csv,json
from fertiliser_screen.model import ImportCase,calculate,freight_fx_grid
from fertiliser_screen.evidence import Requirement,screen_evidence
ROOT=Path(__file__).resolve().parents[1]
def rows(path):
    with (ROOT/path).open(newline='',encoding='utf-8') as f:return list(csv.DictReader(f))
def write(path,x):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(x[0]));w.writeheader();w.writerows(x)
def main():
    cases=[ImportCase(**{k:(v if k=='data_status' else float(v)) for k,v in x.items()}) for x in rows('data/illustrative/import_scenarios.csv')]
    write(ROOT/'outputs/ILLUSTRATIVE_unit_economics.csv',[calculate(c) for c in cases])
    write(ROOT/'outputs/ILLUSTRATIVE_freight_fx_sensitivity.csv',freight_fx_grid(cases[0],[2500,4500,7500],[.82,.9,1.05]))
    req=[Requirement(**r) for r in rows('data/illustrative/regulatory_evidence.csv')]
    report=screen_evidence(req)
    (ROOT/'outputs/REGULATORY_GAPS.json').write_text(json.dumps(report,indent=2)+'\n')
    assert report['legal_conformity'].startswith('UNDETERMINED')
    print('Modelled illustrative unit economics; compliance status UNDETERMINED and not assessed.')
if __name__=='__main__':main()
