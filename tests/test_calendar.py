import datetime as dt
import unittest
from calendar_export import export_calendar

class CalendarExportTests(unittest.TestCase):
 def account(self,**kwargs):
  return dict(dict(id=1,email='test@example.com',app='Youtube',due='2026-01-31',anchor=31,amount='165000',device='iPad'),**kwargs)
 def test_month_end_and_three_day_alarm(self):
  data=export_calendar([self.account()],dt.datetime(2026,1,1,tzinfo=dt.timezone.utc))
  text=data.decode().replace('\r\n ','')
  self.assertIn('DTSTART;TZID=Asia/Ho_Chi_Minh:20260131T180000',text)
  self.assertIn('RRULE:FREQ=MONTHLY;BYMONTHDAY=28,29,30,31;BYSETPOS=-1',text)
  self.assertIn('TRIGGER:-P3D\r\n',text)
  self.assertIn('165.000 VNĐ',text)
  self.assertEqual(text.count('BEGIN:VEVENT'),1)
  self.assertTrue(all(len(line)<=75 for line in data.split(b'\r\n')))
 def test_short_month_original_anchor_retained(self):
  text=export_calendar([self.account(due='2026-02-28')]).decode().replace('\r\n ','')
  self.assertIn('BYMONTHDAY=28,29,30,31;BYSETPOS=-1',text)
  normal=export_calendar([self.account(anchor=15,due='2026-01-15')]).decode()
  self.assertIn('RRULE:FREQ=MONTHLY;BYMONTHDAY=15\r\n',normal)
 def test_text_is_escaped_and_uid_stable(self):
  account=self.account(app='Tên app; dài, nhiều dấu '+('Việt Nam '*20)+'\nBEGIN:VEVENT')
  first=export_calendar([account]);second=export_calendar([dict(account,due='2026-02-28')])
  unfolded=first.decode().replace('\r\n ','')
  self.assertEqual(unfolded.count('\r\nBEGIN:VEVENT\r\n'),1)
  self.assertIn('\\nBEGIN:VEVENT',unfolded)
  uid=lambda data:next(line for line in data.split(b'\r\n') if line.startswith(b'UID:'))
  self.assertEqual(uid(first),uid(second))
  self.assertTrue(all(len(line)<=75 for line in first.split(b'\r\n')))
