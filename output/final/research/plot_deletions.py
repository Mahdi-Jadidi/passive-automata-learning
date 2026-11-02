from pathlib import Path
import csv
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

root=Path(__file__).parent
rows=list(csv.DictReader((root/'extension_experiments.csv').open(encoding='utf8')))
plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False})
fig,axes=plt.subplots(2,2,figsize=(11,7))
for n,ax in enumerate(axes.flat,1):
    rr=[r for r in rows if r['category']=='deletion_path' and r['n']==str(n) and r['order']=='lex']
    rr.sort(key=lambda r:int(r['removed']))
    x=[int(r['removed']) for r in rr]
    ax.plot(x,[int(r['WG']) for r in rr],color='#176B65',label='Global work',linewidth=2)
    ax.plot(x,[int(r['WS']) for r in rr],color='#244A73',label='Split work',linewidth=2)
    ax.plot(x,[int(r['H'])+int(r['WS']) for r in rr],color='#B56B20',label='Selection + Split',linestyle='--',linewidth=1.7)
    good=[r for r in rr if r['decision']=='NET_SPLIT_EQUAL']
    ax.scatter([int(r['removed']) for r in good],[int(r['H'])+int(r['WS']) for r in good],color='#176B65',s=15,zorder=5)
    ax.set_yscale('log');ax.grid(axis='y',alpha=.2)
    ax.set_title(f'n={n}; complete family has {rr[0]["complete_size"]} positives')
    ax.set_xlabel('Positives removed (lexicographic order)')
    ax.set_ylabel('Reference loop events (log scale)')
    if n==1:ax.set_xticks(x)
handles,labels=axes[0,0].get_legend_handles_labels()
fig.legend(handles,labels,loc='lower center',ncol=3,bbox_to_anchor=(.5,.045),frameon=False)
fig.suptitle('Removing positives from a complete balanced family',fontsize=15,y=.98)
fig.text(.5,.015,'Negative set = {c}. Dots mark a pre-training net Split + equality certificate. Curves are subsequent reference checks.',ha='center',fontsize=8)
fig.tight_layout(rect=(0,.09,1,.95))
fig.savefig(root/'deletion_paths.png',dpi=160)
fig.savefig(root/'deletion_paths.pdf')
