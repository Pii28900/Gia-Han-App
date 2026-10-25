import datetime as d
import unittest
from app import next_month
class CalendarTests(unittest.TestCase):
 def test_short_month_preserves_anchor(self):
  feb=next_month(d.date(2026,1,31),31)
  self.assertEqual(feb,d.date(2026,2,28))
  self.assertEqual(next_month(feb,31),d.date(2026,3,31))
 def test_leap_and_year(self):
  self.assertEqual(next_month(d.date(2024,1,31),31),d.date(2024,2,29))
  self.assertEqual(next_month(d.date(2026,12,15),15),d.date(2027,1,15))

class MoneyAndImportTests(unittest.TestCase):
 def test_money_units(self):
  from app import to_vnd
  self.assertEqual(to_vnd('165',thousands=True),'165000')
  self.assertEqual(to_vnd('165000'),'165000')
  for value in ['-1','NaN','Infinity','abc','0.2']:
   with self.assertRaises(ValueError):to_vnd(value)
 def workbook(self,extended):
  import io,zipfile
  from xml.sax.saxutils import escape
  headers=['Stt','Địa chỉ mail','Ngày gia hạn sắp tới']
  row=['1','test@example.com','30/11/2026']
  if extended:headers+=['Quy cách gia hạn'];row+=['Hàng Tháng']
  headers+=['giá tiền ','App','Mail đang login ở'];row+=['165','Youtube','laptop']
  xml='<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData>'
  for n,values in enumerate([headers,row],1):
   xml+='<row>'+''.join(f'<c r="{chr(65+i)}{n}" t="inlineStr"><is><t>{escape(v)}</t></is></c>' for i,v in enumerate(values))+'</row>'
  xml+='</sheetData></worksheet>';out=io.BytesIO()
  with zipfile.ZipFile(out,'w') as z:z.writestr('xl/worksheets/sheet1.xml',xml)
  return out.getvalue()
 def test_both_excel_layouts(self):
  from app import rows_from_xlsx
  for extended in (False,True):
   a=rows_from_xlsx(self.workbook(extended))[0]
   self.assertEqual(a,dict(email='test@example.com',due='2026-11-30',amount='165000',app='Youtube',device='laptop'))

class ReminderListTests(unittest.TestCase):
 def setUp(self):
  import app, tempfile
  from pathlib import Path
  self.app=app;self.tmp=tempfile.TemporaryDirectory();self.old=app.DB
  app.DB=Path(self.tmp.name)/'accounts.db'
 def tearDown(self):
  self.app.DB=self.old;self.tmp.cleanup()
 def add(self,email,days=3,app_name='ChatGPT'):
  with self.app.connect() as c:
   self.app.insert(c,dict(email=email,due=(self.app.today()+d.timedelta(days=days)).isoformat(),app=app_name,amount='165000'))
   return c.execute('SELECT last_insert_rowid()').fetchone()[0]
 def test_added_account_is_due_and_persists(self):
  key=self.add('new@example.com')
  self.assertEqual([r['id'] for r in self.app.due_accounts()],[key])
  with self.app.connect() as c:
   row=c.execute('SELECT * FROM accounts WHERE id=?',(key,)).fetchone()
   self.assertEqual(row['amount'],'165000')
 def test_bulk_delete_stops_reminders_and_preserves_other_accounts(self):
  first=self.add('first@example.com');second=self.add('second@example.com')
  keep=self.add('keep@example.com');future=self.add('future@example.com',4)
  with self.app.connect() as c:c.execute('INSERT INTO notices VALUES(?,?)',(first,'2026-01-01'))
  self.app.delete_accounts([first,second])
  self.assertEqual([r['id'] for r in self.app.due_accounts()],[keep])
  with self.app.connect() as c:
   self.assertEqual({r['id'] for r in c.execute('SELECT id FROM accounts')},{keep,future})
   self.assertEqual(c.execute('SELECT count(*) FROM notices').fetchone()[0],0)


class YouTubeReminderTests(unittest.TestCase):
 def test_name_variants_and_boundaries(self):
  import app
  day=d.date(2026,10,25)
  for name in ('Youtube','YouTube Premium','YOUTUBE MUSIC',' You Tube '):
   self.assertEqual(app.reminder_lead_days(name),0)
   for offset,expected in [(4,False),(3,False),(1,False),(0,True),(-1,True)]:
    self.assertEqual(app.is_reminder_due(dict(app=name,due=(day+d.timedelta(days=offset)).isoformat()),day),expected)
  for offset,expected in [(4,False),(3,True),(1,True),(0,True),(-1,True)]:
   self.assertEqual(app.is_reminder_due(dict(app='ChatGPT',due=(day+d.timedelta(days=offset)).isoformat()),day),expected)
