"""Check the actual Windows EXE serves assets and persists API changes."""
import datetime
import json
import os
from pathlib import Path
import subprocess
import tempfile
import time
import urllib.request

def main():
 opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
 url='http://127.0.0.1:8000/'
 with tempfile.TemporaryDirectory() as tmp:
  env=dict(os.environ,LOCALAPPDATA=tmp)
  process=subprocess.Popen([str(Path('dist/SoGiaHan.exe').resolve()),'--serve-only'],env=env)
  try:
   for attempt in range(60):
    try:
     with opener.open(url+'api/health',timeout=2) as r:
      if json.load(r).get('version')==2:break
    except OSError:pass
    if process.poll() is not None:raise AssertionError('Packaged EXE exited before ready')
    time.sleep(.5)
   else:raise AssertionError('EXE did not become ready')
   with opener.open(url) as r:page=r.read()
   assert b'id="theme-toggle"' in page and 'Sổ Gia Hạn'.encode() in page
   def post(path,data):
    request=urllib.request.Request(url+path,json.dumps(data).encode(),{'Content-Type':'application/json'})
    with opener.open(request) as r:return json.load(r)
   post('api/add',dict(email='exe-test@example.com',app='Test',due=datetime.date.today().isoformat(),amount='165000'))
   with opener.open(url+'api/accounts') as r:accounts=json.load(r)['accounts']
   assert len(accounts)==1 and accounts[0]['amount']=='165000'
   with opener.open(url+'api/calendar.ics') as r:calendar=r.read()
   assert calendar.count(b'BEGIN:VEVENT')==1 and b'TRIGGER:-P3D' in calendar
   post('api/delete',dict(ids=[accounts[0]['id']]))
   assert (Path(tmp)/'SoGiaHan/accounts.db').is_file()
   print('PASS: packaged Windows EXE startup, embedded web interface, add/delete API and data storage')
  finally:
   subprocess.run(['taskkill','/PID',str(process.pid),'/T','/F'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
   process.wait(timeout=20)
if __name__=='__main__':main()
