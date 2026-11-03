"""One consistent phase-active wall clock, including capture and harness work."""
import json,time
from pathlib import Path
A=Path(__file__).resolve().parent
class Budget:
    def __init__(self,kind,phase):
        self.kind=kind;self.phase=phase;self.start=time.perf_counter();self.records=[json.loads(p.read_text()) for p in A.glob('*_active_budget_v2.json')]
    def used(self):return sum(x['active_seconds'] for x in self.records)+time.perf_counter()-self.start
    def preparation_used(self):return sum(x['active_seconds'] for x in self.records if x['kind']=='preparation')+time.perf_counter()-self.start
    def close(self):
        with (A/f'{self.phase}_{self.kind}_active_budget_v2.json').open('x') as f:json.dump({'kind':self.kind,'phase':self.phase,'active_seconds':time.perf_counter()-self.start,'calendar_epoch_end':time.time(),'scope':'phase wall time including captures and harness; interphase approval/codewriting excluded'},f)
