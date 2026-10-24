from fastapi.testclient import TestClient
from .main import app
c=TestClient(app)
def payload(rows):return {'csv_text':'timestamp,voltage,current_a,power_factor\n'+rows}
def test_irregular_timestamp_integration_and_pf():
 p=payload('2026-01-01T00:00:00Z,200,5,0.5\n2026-01-01T00:02:00Z,200,5,0.5\n2026-01-01T00:10:00Z,200,5,0.5')
 r=c.post('/api/analyze',json=p);assert r.status_code==200;d=r.json()['summary'];assert d['energy_kwh']==0.083333;assert d['time_weighted_avg_watts']==500;assert d['coverage_percent']==100
def test_long_gap_is_not_extrapolated():
 p=payload('2026-01-01T00:00:00Z,200,5,1\n2026-01-01T01:00:00Z,200,5,1');d=c.post('/api/analyze',json=p).json()['summary'];assert d['energy_kwh']==0;assert d['gap_count']==1;assert d['time_weighted_avg_watts'] is None
def test_unsorted_samples_and_voltage_events():
 p=payload('2026-01-01T00:05:00Z,260,1,1\n2026-01-01T00:00:00Z,190,1,1');d=c.post('/api/analyze',json=p).json();assert d['readings'][0]['voltage']==190;assert len(d['events'])==2;assert d['summary']['energy_kwh']==0.01875
def test_duplicates_and_nonfinite_values_rejected():
 for rows in ['2026-01-01T00:00:00Z,200,1,1\n2026-01-01T00:00:00Z,200,1,1','2026-01-01T00:00:00Z,NaN,1,1\n2026-01-01T00:01:00Z,200,1,1','2026-01-01T00:00:00,200,1,1\n2026-01-01T00:01:00Z,200,1,1']:
  assert c.post('/api/analyze',json=payload(rows)).status_code==422
def test_schema_and_threshold_validation():
 assert c.post('/api/analyze',json={'csv_text':'timestamp,voltage\ninvalid,3'}).status_code==422
 p=payload('2026-01-01T00:00:00Z,200,1,1\n2026-01-01T00:01:00Z,200,1,1');p['low_voltage']=300;p['high_voltage']=200;assert c.post('/api/analyze',json=p).status_code==422
