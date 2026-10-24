import calendar, datetime as dt, io, json, sqlite3, zipfile
from decimal import Decimal, InvalidOperation
import xml.etree.ElementTree as ET
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DB = ROOT / 'data' / 'accounts.db'
TZ = dt.timezone(dt.timedelta(hours=7))

def today(): return dt.datetime.now(TZ).date()
def next_month(day, anchor):
    year, month = day.year + (day.month == 12), day.month % 12 + 1
    return dt.date(year, month, min(anchor, calendar.monthrange(year, month)[1]))
class ClosingConnection(sqlite3.Connection):
    def __exit__(self, *args):
        try:
            return super().__exit__(*args)
        finally:
            self.close()

def connect():
    DB.parent.mkdir(exist_ok=True)
    c = sqlite3.connect(DB, factory=ClosingConnection)
    c.row_factory = sqlite3.Row
    c.execute('CREATE TABLE IF NOT EXISTS accounts(id INTEGER PRIMARY KEY,email TEXT NOT NULL,due TEXT NOT NULL,amount TEXT,app TEXT,device TEXT,anchor INTEGER NOT NULL,paid TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS notices(account INTEGER,due TEXT,PRIMARY KEY(account,due))')
    return c

def rows_from_xlsx(raw):
    ns = {'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
    if len(raw)>5_000_000: raise ValueError('File quá lớn (tối đa 5 MB)')
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        if sum(i.file_size for i in z.infolist())>20_000_000: raise ValueError('File giải nén quá lớn')
        strings=[]
        if 'xl/sharedStrings.xml' in z.namelist():
            strings=[''.join(x.itertext()) for x in ET.fromstring(z.read('xl/sharedStrings.xml')).findall('s:si',ns)]
        result=[]
        rows = ET.fromstring(z.read('xl/worksheets/sheet1.xml')).findall('.//s:row',ns)
        columns = {}
        for index, row in enumerate(rows):
            cells={}
            for cell in row:
                key=''.join(x for x in cell.attrib.get('r','') if x.isalpha())
                val=cell.find('s:v',ns)
                text=val.text if val is not None else ''.join(cell.itertext())
                cells[key]=strings[int(text)] if cell.attrib.get('t')=='s' else text
            if index == 0:
                columns = {v.strip().casefold(): k for k,v in cells.items()}
                required = ['địa chỉ mail', 'ngày gia hạn sắp tới', 'giá tiền', 'app']
                if any(k not in columns for k in required): raise ValueError('Thiếu cột Excel')
                continue
            def field(name): return cells.get(columns.get(name,''),'').strip()
            cycle=field('quy cách gia hạn').casefold()
            if cycle and cycle not in ('hàng tháng', 'tháng', 'monthly'):
                raise ValueError('Hiện chỉ hỗ trợ gia hạn hàng tháng')
            mail=field('địa chỉ mail')
            if not mail: continue
            rawdate=field('ngày gia hạn sắp tới')
            try:
                due=(dt.date(1899,12,30)+dt.timedelta(days=float(rawdate))).isoformat()
            except ValueError:
                due=dt.datetime.strptime(rawdate,'%d/%m/%Y').date().isoformat()
            result.append(dict(email=mail,due=due,amount=to_vnd(field('giá tiền'), thousands=True),app=field('app'),device=field('mail đang login ở')))
        return result

def to_vnd(value, thousands=False):
    try:
        number = Decimal(str(value or '0').strip()) * (1000 if thousands else 1)
        if not number.is_finite() or number < 0 or number != number.to_integral_value():
            raise ValueError('Số tiền phải là số nguyên VNĐ không âm')
        return str(int(number))
    except InvalidOperation:
        raise ValueError('Số tiền không hợp lệ')

def insert(c,a):
    due=dt.date.fromisoformat(a['due'])
    if '@' not in a['email'] or not a.get('app','').strip(): raise ValueError('Cần Gmail và tên app hợp lệ')
    c.execute('INSERT INTO accounts(email,due,amount,app,device,anchor) VALUES(?,?,?,?,?,?)',(a['email'].strip(),due.isoformat(),to_vnd(a.get('amount','0')),a['app'],a.get('device',''),due.day))

def due_accounts():
    with connect() as c:
        return [dict(r) for r in c.execute('SELECT * FROM accounts ORDER BY due')
                if (dt.date.fromisoformat(r['due'])-today()).days <= 3]

def delete_accounts(ids):
    ids = [(int(key),) for key in ids]
    with connect() as c:
        c.executemany('DELETE FROM notices WHERE account=?', ids)
        c.executemany('DELETE FROM accounts WHERE id=?', ids)

class Handler(BaseHTTPRequestHandler):
    def log_message(self,*args): pass
    def send(self,status,obj):
        data=json.dumps(obj,ensure_ascii=False).encode()
        self.send_response(status); self.send_header('Content-Type','application/json; charset=utf-8'); self.send_header('Content-Length',str(len(data))); self.send_header('Cache-Control','no-store'); self.end_headers(); self.wfile.write(data)
    def do_GET(self):
        if self.path=='/api/accounts':
            with connect() as c: records=[dict(x) for x in c.execute('SELECT * FROM accounts ORDER BY due')]
            for a in records:
                due=dt.date.fromisoformat(a['due']); upcoming=due
                while upcoming<=today(): upcoming=next_month(upcoming,a['anchor'])
                a.update(days=(due-today()).days,next_due=upcoming.isoformat())
            return self.send(200,dict(accounts=records))
        if self.path!='/': return self.send(404,{'error':'Không tìm thấy'})
        data=(ROOT/'static/index.html').read_bytes()
        self.send_response(200); self.send_header('Content-Type','text/html; charset=utf-8'); self.send_header('Content-Length',str(len(data))); self.end_headers(); self.wfile.write(data)
    def do_POST(self):
        if self.headers.get('Origin') and self.headers['Origin'] != 'http://'+self.headers.get('Host',''): return self.send(403,{'error':'Origin không hợp lệ'})
        try:
            size=int(self.headers.get('Content-Length',0))
            if not 0<size<=5_000_000: raise ValueError('Kích thước yêu cầu không hợp lệ')
            raw=self.rfile.read(size)
            with connect() as c:
                if self.path=='/api/import':
                    accounts=rows_from_xlsx(raw); count=0
                    for a in accounts:
                        if not c.execute('SELECT 1 FROM accounts WHERE email=? AND app=? AND due=?',(a['email'],a['app'],a['due'])).fetchone(): insert(c,a); count+=1
                    return self.send(200,{'imported':count})
                a=json.loads(raw)
                if self.path=='/api/add': insert(c,a)
                elif self.path=='/api/paid':
                    row=c.execute('SELECT * FROM accounts WHERE id=?',(int(a['id']),)).fetchone()
                    if not row: raise ValueError('Không tìm thấy tài khoản')
                    due=next_month(dt.date.fromisoformat(row['due']),row['anchor'])
                    while due<=today(): due=next_month(due,row['anchor'])
                    c.execute('UPDATE accounts SET due=?,paid=? WHERE id=?',(due.isoformat(),today().isoformat(),row['id']))
                elif self.path=='/api/delete': c.execute('DELETE FROM accounts WHERE id=?',(int(a['id']),))
                else: return self.send(404,{'error':'Không tìm thấy'})
            self.send(200,{'ok':True})
        except (ValueError,KeyError,zipfile.BadZipFile,ET.ParseError): self.send(400,{'error':'Dữ liệu không hợp lệ. Kiểm tra ngày và cấu trúc file HSD.'})

if __name__=='__main__':
    with connect(): pass
    print('Gia Hạn App: cổng 8000, chỉ truy cập nội bộ',flush=True)
    ThreadingHTTPServer(('127.0.0.1',8000),Handler).serve_forever()
