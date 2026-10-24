import json
import pytest
from fastapi.testclient import TestClient
import main
@pytest.fixture
def client(monkeypatch):
 monkeypatch.delenv('GEMINI_API_KEY',raising=False)
 monkeypatch.delenv('AI_ACCESS_TOKEN',raising=False)
 main._ai_calls.clear()
 return TestClient(main.app)
def test_health_and_security_headers(client):
 r=client.get('/');assert r.status_code==200;assert 'frame-ancestors' in r.headers['content-security-policy']
 assert client.get('/health').json()['ai_available'] is False
 assert client.get('/static/app.js').status_code==200
def test_ai_unconfigured_preserves_template(client):
 assert client.post('/api/refine',json=payload()).status_code==503
 assert client.post(ENDPOINT,json=payload()).status_code==200
def test_ai_requires_owner_token(client,monkeypatch):
 monkeypatch.setenv('GEMINI_API_KEY','test-key');monkeypatch.setenv('AI_ACCESS_TOKEN','a'*24)
 assert client.post('/api/refine',json=payload()).status_code==401
 assert client.post('/api/refine',json=payload(),headers={'X-AI-Token':'wrong'}).status_code==401
def test_ai_validated_and_budgeted(client,monkeypatch):
 monkeypatch.setenv('GEMINI_API_KEY','test-key');monkeypatch.setenv('AI_ACCESS_TOKEN','a'*24)
 class Fake:
  def __enter__(self):return self
  def __exit__(self,*a):pass
  def read(self,*a):return json.dumps({'candidates':[{'content':{'parts':[{'text':json.dumps({'summary':'A summary grounded in supplied inputs.'})}]}}]}).encode()
 monkeypatch.setattr(main,'urlopen',lambda *a,**k:Fake())
 r=client.post('/api/refine',json=payload(),headers={'X-AI-Token':'a'*24});assert r.status_code==200;assert r.json()['summary']
 main._ai_calls[:]=[main.time.time()]*10
 assert client.post('/api/refine',json=payload(),headers={'X-AI-Token':'a'*24}).status_code==429
def test_ai_failure_does_not_expose_exception(client,monkeypatch):
 monkeypatch.setenv('GEMINI_API_KEY','private-test-secret');monkeypatch.setenv('AI_ACCESS_TOKEN','a'*24)
 def fail(*a,**k):raise RuntimeError('private-test-secret')
 monkeypatch.setattr(main,'urlopen',fail)
 r=client.post('/api/refine',json=payload(),headers={'X-AI-Token':'a'*24});assert r.status_code==502;assert 'private-test-secret' not in r.text
ENDPOINT='/api/research'
def payload():return {'topic':'Knowledge management options','question':'What should the team validate before buying a tool?','sources':[{'title':'Team notes','url':'https://example.com/notes','excerpt':'The team needs searchable documents with clear ownership and periodic review.'}]}
def test_sources_preserved_and_linked(client):
 p=payload();d=client.post(ENDPOINT,json=p).json();assert d['sections'][0]['text']==p['sources'][0]['excerpt'];assert d['sections'][0]['citations']==['S1'];assert len(d['warnings'])==3;assert d['status']=='draft'
def test_duplicate_sources_rejected(client):
 p=payload();p['sources']*=2;assert client.post(ENDPOINT,json=p).status_code==422
@pytest.mark.parametrize('url',['javascript:alert(1)','http://example.com','https://user:password@example.com','file:///tmp/data'])
def test_unsafe_source_urls_rejected(client,url):
 p=payload();p['sources'][0]['url']=url;assert client.post(ENDPOINT,json=p).status_code==422
def test_empty_or_blank_input(client):
 p=payload();p['sources']=[];assert client.post(ENDPOINT,json=p).status_code==422
 p=payload();p['topic']=' '*10;assert client.post(ENDPOINT,json=p).status_code==422

def test_mounted_proposal_application(client):
 assert client.get('/scopecraft/').status_code==200
 assert client.get('/scopecraft/static/app.js').status_code==200
 r=client.post('/scopecraft/api/proposal',json={'client':'Demo Company','title':'Website automation','objective':'Capture and validate all customer enquiries.','rate':'25','currency':'USD','items':[{'name':'Implementation','hours':'4'}]})
 assert r.status_code==200
 assert r.json()['total']=='100.00'
