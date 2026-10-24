"""Offline telemetry analysis. Not a control or protection system."""
import csv, io, math
from datetime import datetime, timezone
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
BASE=Path(__file__).parent
app=FastAPI(title='GridWatch Lab')
app.mount('/static',StaticFiles(directory=BASE/'static'),name='static')
@app.get('/')
def index():return FileResponse(BASE/'static/index.html')
@app.get('/health')
def health():return {'status':'ok','mode':'offline telemetry analysis','external_services':False}
class Upload(BaseModel):
 csv_text:str=Field(min_length=20,max_length=500000)
 low_voltage:float=Field(default=207,ge=0,le=500)
 high_voltage:float=Field(default=253,ge=0,le=500)
 max_gap_minutes:float=Field(default=15,gt=0,le=120)
@app.post('/api/analyze')
def analyze(b:Upload):
 if b.low_voltage>=b.high_voltage:raise HTTPException(422,'Low threshold must be below high threshold.')
 reader=csv.DictReader(io.StringIO(b.csv_text.lstrip('\ufeff')))
 required={'timestamp','voltage','current_a','power_factor'}
 if not reader.fieldnames or not required.issubset(reader.fieldnames):raise HTTPException(422,'CSV requires timestamp, voltage, current_a and power_factor columns.')
 data=[];seen=set()
 for i,row in enumerate(reader,2):
  if len(data)>=2000:raise HTTPException(422,'Maximum 2000 readings per analysis.')
  try:
   dt=datetime.fromisoformat(row['timestamp'].strip().replace('Z','+00:00'))
   if dt.tzinfo is None:raise ValueError('timezone')
   dt=dt.astimezone(timezone.utc)
   v=float(row['voltage']);a=float(row['current_a']);pf=float(row['power_factor'])
   if not all(math.isfinite(x) for x in (v,a,pf)) or not (0<=v<=500 and 0<=a<=1000 and 0<=pf<=1):raise ValueError('range')
   if dt in seen:raise ValueError('duplicate timestamp')
   seen.add(dt);data.append({'timestamp':dt.isoformat(),'seconds':dt.timestamp(),'voltage':v,'current_a':a,'power_factor':pf,'power_w':v*a*pf})
  except (ValueError,TypeError,KeyError,AttributeError):raise HTTPException(422,f'Invalid row {i}: use unique timezone-aware timestamps, 0–500 V, 0–1000 A and power factor 0–1.') from None
 if len(data)<2:raise HTTPException(422,'At least two valid readings are required.')
 data.sort(key=lambda r:r['seconds']);energy=0;covered=0;gaps=[]
 for prev,cur in zip(data,data[1:]):
  dt=cur['seconds']-prev['seconds']
  if dt>b.max_gap_minutes*60:gaps.append({'start':prev['timestamp'],'end':cur['timestamp'],'minutes':round(dt/60,2)});continue
  energy+=(prev['power_w']+cur['power_w'])/2*dt/3600000;covered+=dt
 events=[{'timestamp':r['timestamp'],'voltage':r['voltage'],'kind':'low voltage' if r['voltage']<b.low_voltage else 'high voltage'} for r in data if r['voltage']<b.low_voltage or r['voltage']>b.high_voltage]
 span=data[-1]['seconds']-data[0]['seconds']
 return {'readings':[{k:round(v,5) if isinstance(v,float) else v for k,v in r.items() if k!='seconds'} for r in data],'summary':{'count':len(data),'energy_kwh':round(energy,6),'peak_watts':round(max(r['power_w'] for r in data),2),'time_weighted_avg_watts':round(energy*3600000/covered,2) if covered else None,'coverage_percent':round(covered/span*100,1),'covered_minutes':round(covered/60,2),'gap_count':len(gaps),'voltage_events':len(events),'min_voltage':min(r['voltage'] for r in data),'max_voltage':max(r['voltage'] for r in data)},'events':events,'gaps':gaps,'method':'Single-phase real power = V × A × supplied power factor. Trapezoidal integration uses actual timestamps. Intervals above the gap limit are excluded; no energy is extrapolated before or after the readings.','limits':'Input readings are assumed representative of their intervals. This is an offline analysis aid, not a certified meter, three-phase model or protection controller.'}
