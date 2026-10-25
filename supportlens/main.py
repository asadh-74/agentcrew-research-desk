from pathlib import Path
import re
from typing import Literal
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, ConfigDict

app = FastAPI(title='SupportLens')
BASE = Path(__file__).parent
app.mount('/static', StaticFiles(directory=BASE/'static'), name='static')
@app.get('/')
def index(): return FileResponse(BASE/'static/index.html')
@app.get('/health')
def health(): return {'status':'ok','mode':'rules','storage':'browser-local'}
class Report(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra='forbid')
    id: str = Field(min_length=1,max_length=80)
    project: str = Field(min_length=2,max_length=80)
    title: str = Field(min_length=5,max_length=180)
    evidence: str = Field(min_length=10,max_length=4000)
    impact: Literal['low','medium','high','critical'] = 'medium'
    status: Literal['new','investigating','fixed','verified'] = 'new'
    resolution: str = Field(default='',max_length=2000)
    history: list[str] = Field(default_factory=list,max_length=100)
class Workspace(BaseModel):
    reports: list[Report] = Field(max_length=200)

def validate(w):
    ids=[r.id for r in w.reports]
    if len(ids)!=len(set(ids)): raise HTTPException(422,'Duplicate report IDs')
    for r in w.reports:
        if any(len(h)>500 for h in r.history): raise HTTPException(422,'History entry too long')
        if r.status in ('fixed','verified') and not r.resolution.strip(): raise HTTPException(422,'Fixed and verified reports need resolution evidence')
    return w
@app.post('/api/validate')
def restore(w:Workspace): return validate(w)
@app.post('/api/analyze')
def analyze(w:Workspace):
    validate(w)
    pairs=[]
    tokens=lambda r:set(re.findall(r'[a-z0-9]+',(r.title+' '+r.evidence).lower()))-{'the','a','is','and','to','in','of','on','it','for','with'}
    for i,a in enumerate(w.reports):
        for b in w.reports[i+1:]:
            if a.project.casefold()!=b.project.casefold(): continue
            x,y=tokens(a),tokens(b); shared=x&y
            score=len(shared)/max(len(x|y),1)
            if score>=.3: pairs.append({'a':a.id,'b':b.id,'similarity':round(score*100),'shared':sorted(shared)[:8]})
    return {'duplicates':sorted(pairs,key=lambda p:-p['similarity'])[:30], 'method':'Same-project word overlap (Jaccard ≥ 30%). Suggestions require human review.'}
