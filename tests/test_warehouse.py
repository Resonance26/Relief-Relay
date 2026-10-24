"""Run: python tests/test_warehouse.py -- exercises real warehouse application with temporary DB"""
import importlib.util
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('rr',ROOT/'warehouse/server.py')
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

with TemporaryDirectory() as p:
 mod.DB_PATH=Path(p)/'test.sqlite3'
 mod.init_db()
 assert mod.decode('RR1|RABC123|YEL03|4|1|FLOOD')==('RABC123','YEL03',4,1,'FLOOD')
 for invalid in ['RR1|X|YEL03|4|1|FLOOD','RR1|RABC456|YEL03|4|5|FLOOD','RR1|RABC456|YEL03|4|1|TORNADO','RR1|RABC456|YEL03|0|0|FLOOD']:
  try:mod.decode(invalid)
  except ValueError:pass
  else:raise AssertionError('Should reject '+invalid)
 assert mod.decode('RR1|RNEW001|YEL03|4|1|FLOOD|2|REGULAR|INHALER')==('RNEW001','YEL03',4,1,'FLOOD',2,'REGULAR','INHALER')
 for invalid_med in ['RR1|RNEW002|YEL03|4|1|FLOOD|8|URGENT|TEST','RR1|RNEW002|YEL03|4|1|FLOOD|1|BAD|TEST','RR1|RNEW002|YEL03|4|1|FLOOD|1|URGENT|BAD*NOTE']:
  try:mod.decode(invalid_med)
  except ValueError:pass
  else:raise AssertionError('Should reject '+invalid_med)
 assert mod.ingest('RR1|RNEW001|YEL03|4|1|FLOOD|2|REGULAR|INHALER')
 assert not mod.ingest('RR1|RNEW001|YEL03|4|1|FLOOD|2|REGULAR|INHALER')
 extra=next(r for r in mod.state()['requests'] if r['id']=='RNEW001')
 assert extra['seniors']==2 and extra['medicine']=='REGULAR'
 assert extra['proposed']['senior_support']==2
 assert 'medicine' not in extra['proposed']
 assert mod.ingest('RR1|RABC123|YEL03|4|1|FLOOD')
 assert not mod.ingest('RR1|RABC123|YEL03|4|1|FLOOD')
 assert len(mod.state()['requests'])==2
 status,payload=mod.assign('RABC123')
 assert status==200,(status,payload)
 assert payload['expected_g']>0
 status,payload=mod.verify('RABC123',{'checklist_confirmed':True})
 assert status==409
 mod.record_weight(10,'SIMULATED')
 status,payload=mod.verify('RABC123',{'checklist_confirmed':True})
 assert status==409,'Wrong weight must fail'
 mod.record_weight(next(r for r in mod.state()['requests'] if r['id']=='RABC123')['expected_g'],'SIMULATED')
 status,payload=mod.verify('RABC123',{'checklist_confirmed':False})
 assert status==400,'Missing checklist must fail'
 status,payload=mod.verify('RABC123',{'checklist_confirmed':True})
 assert status==200,(status,payload)
 assert mod.advance('RABC123')[1]['status']=='DISPATCHED'
 assert mod.advance('RABC123')[1]['status']=='DELIVERED'
 assert mod.advance('RABC123')[0]==409
 assert (ROOT/'warehouse/templates/index.html').exists()
 assert (ROOT/'warehouse/templates/driver.html').exists()
 print('PASS: packet validation, duplicate suppression, allocation, stock, weight checks, dispatch and delivery')
