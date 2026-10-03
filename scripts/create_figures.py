"""Generate clearly labelled model-only charts from local illustrative outputs."""
import csv
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
def load(file):
    with (ROOT/'outputs'/file).open(newline='',encoding='utf-8') as f:
        return list(csv.DictReader(f))
def export(fig,name):
    fig.text(.01,.012,'SCENARIO DATA ONLY  |  No observed project outcome or validated compliance',size=8)
    fig.tight_layout(rect=(0,.025,1,1))
    dest=ROOT/'figures'/name
    fig.savefig(dest,format='svg',metadata={'Title':name,'Date':'2026-10-04'})
    plt.close(fig)
    print('Wrote reproducible figure',dest)
def main():
    rows=load('ILLUSTRATIVE_freight_fx_sensitivity.csv')
    groups=sorted(set(float(r['hypothetical_eur_per_usd']) for r in rows))
    fig,ax=plt.subplots(figsize=(9.5,5.6))
    for fx in groups:
        z=sorted([r for r in rows if float(r['hypothetical_eur_per_usd'])==fx],key=lambda r:float(r['hypothetical_freight_eur']))
        ax.plot([float(r['hypothetical_freight_eur']) for r in z],[float(r['landed_eur_per_kg']) for r in z],marker='o',label=f'EUR per USD {fx:.2f}')
    ax.set(xlabel='Assumed shipping cost (EUR)',ylabel='Landed unit cost (EUR / kg)',title='ILLUSTRATIVE | FX / freight sensitivity — no real price quotes')
    ax.legend();export(fig,'ILLUSTRATIVE_shipping_fx.svg')

if __name__ == "__main__":main()
