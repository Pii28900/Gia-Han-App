import json
from pathlib import Path
import sqlite3
import tempfile
import threading
import unittest
import urllib.request
import urllib.error
import app

class HTTPTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.old=app.DB;app.DB=Path(self.tmp.name)/'accounts.db'
  self.server=app.ThreadingHTTPServer(('127.0.0.1',0),app.Handler)
  self.thread=threading.Thread(target=self.server.serve_forever);self.thread.start()
  self.url=f'http://127.0.0.1:{self.server.server_port}'
 def tearDown(self):
  self.server.shutdown();self.server.server_close();self.thread.join();app.DB=self.old;self.tmp.cleanup()
 def get(self,path):
  with urllib.request.urlopen(self.url+path) as r:return json.load(r)
 def post(self,path,obj,headers=None):
  req=urllib.request.Request(self.url+path,json.dumps(obj).encode(),headers or {'Content-Type':'application/json'})
  with urllib.request.urlopen(req) as r:return json.load(r)
 def test_crud_and_backup(self):
  self.post('/api/add',dict(email='test@example.com',app='Youtube',due=app.today().isoformat(),amount='165000'))
  row=self.get('/api/accounts')['accounts'][0]
  self.post('/api/edit',dict(row,app='YouTube Premium',amount='175000'))
  edited=self.get('/api/accounts')['accounts'][0]
  self.assertEqual((edited['app'],edited['amount']),('YouTube Premium','175000'))
  self.post('/api/paid',{'id':row['id']})
  current=self.get('/api/accounts')['accounts'][0]
  self.assertGreater(current['days'],0)
  self.assertGreater(current['next_due'],current['due'])
  with urllib.request.urlopen(self.url+'/api/backup') as r:data=r.read()
  backup=Path(self.tmp.name)/'backup.db';backup.write_bytes(data)
  with app.ClosingConnection(backup) as c:self.assertEqual(c.execute('SELECT count(*) FROM accounts').fetchone()[0],1)
  self.post('/api/delete',{'ids':[row['id']]})
  self.assertEqual(self.get('/api/accounts')['accounts'],[])
 def test_foreign_origin_and_host_rejected(self):
  with self.assertRaises(urllib.error.HTTPError) as e:self.post('/api/add',{}, {'Origin':'https://example.com'})
  self.assertEqual(e.exception.code,403)
  req=urllib.request.Request(self.url+'/api/accounts',headers={'Host':'evil.example'})
  with self.assertRaises(urllib.error.HTTPError) as e:urllib.request.urlopen(req)
  self.assertEqual(e.exception.code,403)
 def test_invalid_input_rolls_back(self):
  with self.assertRaises(urllib.error.HTTPError) as e:self.post('/api/add',dict(email='test@example.com',app='Test',due='bad',amount='1'))
  self.assertEqual(e.exception.code,400)
  self.assertEqual(self.get('/api/accounts')['accounts'],[])
