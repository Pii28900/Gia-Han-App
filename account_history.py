"""Bounded, transactional undo history for the shared account list only."""
import hashlib
import json

class HistoryConflict(ValueError):pass

LABELS={'/api/add':'thêm tài khoản','/api/edit':'sửa tài khoản','/api/delete':'xóa tài khoản',
        '/api/paid':'xác nhận gia hạn','/api/import':'nhập Excel'}

def snapshot(c):
    return json.dumps([dict(row) for row in c.execute('SELECT id,email,due,amount,app,device,anchor,paid FROM accounts ORDER BY id')],ensure_ascii=False,sort_keys=True,separators=(',',':'))
def digest(value):return hashlib.sha256(value.encode()).hexdigest()
def available(c):
    row=c.execute('SELECT id,label,after_digest FROM account_history ORDER BY id DESC LIMIT 1').fetchone()
    if not row or row['after_digest']!=digest(snapshot(c)):return None
    return {'id':row['id'],'label':row['label']}
def record(c,before,path):
    after=snapshot(c)
    if before==after or path not in LABELS:return
    c.execute('INSERT INTO account_history(before_json,after_digest,label) VALUES(?,?,?)',(before,digest(after),LABELS[path]))
    c.execute('DELETE FROM account_history WHERE id NOT IN (SELECT id FROM account_history ORDER BY id DESC LIMIT 20)')
def undo(c,expected_id):
    row=c.execute('SELECT * FROM account_history ORDER BY id DESC LIMIT 1').fetchone()
    if not row or row['id']!=int(expected_id) or row['after_digest']!=digest(snapshot(c)):
        raise HistoryConflict('Danh sách đã thay đổi. Hãy tải lại và kiểm tra thao tác trước khi hoàn tác.')
    rows=json.loads(row['before_json'])
    c.execute('DELETE FROM accounts');c.execute('DELETE FROM notices')
    c.executemany('INSERT INTO accounts(id,email,due,amount,app,device,anchor,paid) VALUES(?,?,?,?,?,?,?,?)',
                  [(r['id'],r['email'],r['due'],r['amount'],r['app'],r['device'],r['anchor'],r['paid']) for r in rows])
    c.execute('DELETE FROM account_history WHERE id=?',(row['id'],))
