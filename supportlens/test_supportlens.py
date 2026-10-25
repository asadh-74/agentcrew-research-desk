from fastapi.testclient import TestClient
from supportlens.main import app
c=TestClient(app)
def report(id='1',**kw): return dict(id=id,project='Demo',title='Mobile menu hides button',evidence='Open mobile menu and the save button becomes hidden',**kw)
def test_duplicates_same_project():
 r=c.post('/api/analyze',json={'reports':[report(),report('2')]});assert r.status_code==200;assert r.json()['duplicates'][0]['similarity']==100

def test_cross_project_not_grouped():
 b=report('2');b['project']='Other';assert c.post('/api/analyze',json={'reports':[report(),b]}).json()['duplicates']==[]
def test_invalid_status_rejected(): assert c.post('/api/validate',json={'reports':[report(status='sent')]}).status_code==422
def test_fixed_needs_evidence(): assert c.post('/api/validate',json={'reports':[report(status='fixed')]}).status_code==422
def test_duplicate_ids_rejected(): assert c.post('/api/validate',json={'reports':[report(),report()]}).status_code==422
def test_restore_preserves_evidence():
 r=c.post('/api/validate',json={'reports':[report(status='verified',resolution='Retested on a narrow screen; button is accessible.')]});assert r.status_code==200;assert r.json()['reports'][0]['status']=='verified'
def test_whitespace_rejected():
 r=report();r['title']='     ';assert c.post('/api/validate',json={'reports':[r]}).status_code==422
