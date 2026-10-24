"""Windows desktop entry point. No web server or email needed."""
import datetime as dt
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import app

BASE = Path(getattr(sys, '_MEIPASS', Path(__file__).resolve().parent))
STORE = Path(os.getenv('LOCALAPPDATA', str(Path.home()))) / 'SoGiaHan'
STORE.mkdir(parents=True, exist_ok=True)
app.DB = STORE / 'accounts.db'
seed = BASE / 'seed' / 'accounts.db'
if not app.DB.exists() and seed.exists(): shutil.copy2(seed, app.DB)

def records():
    with app.connect() as c: return [dict(r) for r in c.execute('SELECT * FROM accounts ORDER BY due')]

def reminder():
    due = app.due_accounts()
    if not due: return
    root=tk.Tk(); root.withdraw()
    summary='\n'.join(f"{r['app']} · {r['email']} · {r['due']} · {int(r['amount']):,}đ" for r in due)
    messagebox.showwarning('Nhắc gia hạn trước 3 ngày', summary + '\n\nMở Sổ Gia Hạn để kiểm tra và xác nhận đã gia hạn.', parent=root)
    root.destroy()

def enable_schedule(entrypoint=None):
    if sys.platform != 'win32': raise ValueError('Lịch nhắc này dành cho Windows')
    if getattr(sys,'frozen',False):
        exe=sys.executable; args='--remind'
    else:
        exe=str(Path(sys.executable).with_name('pythonw.exe'))
        args='"'+str(Path(entrypoint or __file__).resolve())+'" --remind'
    # Escape PowerShell literals independently of shell quoting.
    quote=lambda s: "'"+s.replace("'","''")+"'"
    command=(f"$a=New-ScheduledTaskAction -Execute {quote(exe)} -Argument {quote(args)};"
             "$t=New-ScheduledTaskTrigger -Daily -At '18:00';"
             "$s=New-ScheduledTaskSettingsSet -StartWhenAvailable;"
             "$u=[System.Security.Principal.WindowsIdentity]::GetCurrent().Name;"
             "$p=New-ScheduledTaskPrincipal -UserId $u -LogonType Interactive -RunLevel Limited;"
             "Register-ScheduledTask -TaskName 'SoGiaHanReminder' -Action $a -Trigger $t -Settings $s -Principal $p -Force -ErrorAction Stop | Out-Null")
    result=subprocess.run(['powershell.exe','-NoProfile','-NonInteractive','-Command',command],capture_output=True,text=True,creationflags=0x08000000)
    if result.returncode: raise ValueError('Windows chưa lưu được lịch nhắc. Kiểm tra quyền Task Scheduler.')

class Desktop:
    def __init__(self, root):
        self.root=root;root.title('Sổ Gia Hạn');root.geometry('1120x650')
        ttk.Label(root,text='Sổ Gia Hạn',font=('Segoe UI',24,'bold')).pack(anchor='w',padx=20,pady=12)
        ttk.Label(root,text='Nhắc trước 3 ngày • Lưu trên máy • Số tiền VNĐ • Chu kỳ hàng tháng').pack(anchor='w',padx=20)
        bar=ttk.Frame(root);bar.pack(fill='x',padx=20,pady=15)
        for title,action in [('Thêm email cần nhắc',self.add),('Sửa',self.edit),('Nhập Excel',self.import_file),('Đã gia hạn',self.paid),('Xóa email đã chọn',self.delete),('Bật nhắc Windows',self.schedule),('Sao lưu',self.backup)]:
            ttk.Button(bar,text=title,command=lambda a=action:self.safe(a)).pack(side='left',padx=3)
        self.search=tk.StringVar();self.search.trace_add('write',lambda *args:self.refresh())
        ttk.Entry(root,textvariable=self.search).pack(fill='x',padx=20)
        ttk.Label(root,text='Tìm Gmail hoặc tên app • Giữ Ctrl hoặc Shift để chọn nhiều dòng cần xóa').pack(anchor='w',padx=20)
        frame=ttk.Frame(root);frame.pack(fill='both',expand=True,padx=20,pady=10)
        cols=('email','app','due','next','amount','device','status')
        self.table=ttk.Treeview(frame,columns=cols,show='headings',selectmode='extended')
        for key,title,width in zip(cols,['Gmail','App','Đến hạn','Kỳ tiếp dự kiến','Số tiền','Thiết bị','Trạng thái'],[230,110,100,110,100,100,130]):
            self.table.heading(key,text=title);self.table.column(key,width=width)
        self.table.tag_configure('urgent',foreground='#b13b18')
        scroll=ttk.Scrollbar(frame,orient='vertical',command=self.table.yview);self.table.configure(yscrollcommand=scroll.set)
        scroll.pack(side='right',fill='y');self.table.pack(fill='both',expand=True)
        ttk.Label(root,text='Đã gia hạn: chuyển đến kỳ tương lai gần nhất. Không tự thanh toán.\nNhắc Windows lúc 18:00 mỗi ngày; máy cần bật và bạn đang đăng nhập. Không gửi email.').pack(anchor='w',padx=20,pady=10)
        self.refresh();self.tick()
    def safe(self,fn):
        try: fn()
        except Exception as e: messagebox.showerror('Không thực hiện được',str(e),parent=self.root)
    def refresh(self):
        selected = self.table.selection()
        for item in self.table.get_children():self.table.delete(item)
        self.items={r['id']:r for r in records()}
        for r in self.items.values():
            if self.search.get().casefold() not in (r['email']+' '+r['app']).casefold():continue
            due=dt.date.fromisoformat(r['due']);days=(due-app.today()).days;following=app.next_month(due,r['anchor'])
            while following<=app.today():following=app.next_month(following,r['anchor'])
            status=f'Quá hạn {-days} ngày' if days<0 else f'Còn {days} ngày'
            self.table.insert('', 'end',iid=str(r['id']),values=(r['email'],r['app'],r['due'],following.isoformat(),f"{int(r['amount']):,}đ".replace(',','.'),r['device'],status),tags=('urgent',) if days<=3 else ())
        retained = [key for key in selected if self.table.exists(key)]
        if retained: self.table.selection_set(retained)
    def tick(self):self.refresh();self.root.after(60000,self.tick)
    def selected(self):
        selected=self.table.selection()
        if not selected:raise ValueError('Hãy chọn một tài khoản trong danh sách')
        if len(selected) != 1: raise ValueError('Hãy chọn đúng một tài khoản để sửa hoặc xác nhận gia hạn')
        return self.items[int(selected[0])]
    def add(self):self.form()
    def edit(self):self.form(self.selected())
    def form(self,record=None):
        win=tk.Toplevel(self.root);win.title('Sửa email cần nhắc' if record else 'Thêm email cần nhắc');win.transient(self.root);win.grab_set();fields={}
        for key,label in [('email','Gmail'),('app','Tên app'),('due','Ngày đến hạn (YYYY-MM-DD)'),('amount','Số tiền VNĐ, ví dụ 165000'),('device','Thiết bị / ghi chú')]:
            ttk.Label(win,text=label).pack(anchor='w',padx=20,pady=4)
            value=tk.StringVar(value=str(record[key]) if record else (app.today().isoformat() if key=='due' else ''))
            ttk.Entry(win,textvariable=value,width=45).pack(padx=20);fields[key]=value
        def save():
            a={k:v.get().strip() for k,v in fields.items()};due=dt.date.fromisoformat(a['due']);amount=app.to_vnd(a['amount'])
            if '@' not in a['email'] or not a['app']:raise ValueError('Cần Gmail và tên app')
            with app.connect() as c:
                if record:
                    anchor=record['anchor'] if record['due']==a['due'] else due.day
                    c.execute('UPDATE accounts SET email=?,app=?,due=?,amount=?,device=?,anchor=? WHERE id=?',(a['email'],a['app'],a['due'],amount,a['device'],anchor,record['id']))
                else: app.insert(c,a)
            self.search.set('');win.destroy();self.refresh()
            messagebox.showinfo('Đã lưu', 'Email đã được lưu vào danh sách nhắc trước hạn 3 ngày.', parent=self.root)
        ttk.Button(win,text='Lưu',command=lambda:self.safe(save)).pack(pady=15)
    def import_file(self):
        name=filedialog.askopenfilename(filetypes=[('Excel','*.xlsx')])
        if not name:return
        rows=app.rows_from_xlsx(Path(name).read_bytes());count=0
        with app.connect() as c:
            for a in rows:
                if not c.execute('SELECT 1 FROM accounts WHERE email=? AND app=? AND due=?',(a['email'],a['app'],a['due'])).fetchone(): app.insert(c,a);count+=1
        self.refresh();messagebox.showinfo('Nhập Excel',f'Đã thêm {count} tài khoản. Số tiền Excel được nhân 1.000.')
    def paid(self):
        r=self.selected();due=app.next_month(dt.date.fromisoformat(r['due']),r['anchor'])
        while due<=app.today():due=app.next_month(due,r['anchor'])
        if messagebox.askyesno('Xác nhận',f"Đã gia hạn {r['app']}? Chuyển hạn đến {due}."):
            with app.connect() as c:c.execute('UPDATE accounts SET due=?,paid=? WHERE id=?',(due.isoformat(),app.today().isoformat(),r['id']))
            self.refresh()
    def delete(self):
        selected=self.table.selection()
        if not selected: raise ValueError('Hãy chọn email cần xóa trong danh sách')
        rows=[self.items[int(key)] for key in selected]
        preview='\n'.join(f"• {r['email']} — {r['app']}" for r in rows[:8])
        if len(rows)>8: preview+=f'\n… và {len(rows)-8} dòng khác'
        if messagebox.askyesno('Xóa email khỏi danh sách nhắc',
                              f'Xóa {len(rows)} dòng đã chọn?\n\n{preview}\n\nCác dòng này sẽ không còn được nhắc. Tài khoản Gmail thật không bị xóa.',parent=self.root):
            app.delete_accounts([r['id'] for r in rows])
            self.refresh()
            messagebox.showinfo('Đã xóa', f'Đã xóa {len(rows)} dòng khỏi danh sách nhắc.',parent=self.root)
    def backup(self):
        name=filedialog.asksaveasfilename(defaultextension='.db',filetypes=[('SQLite backup','*.db')])
        if name:
            import sqlite3
            if Path(name).resolve()==app.DB.resolve():raise ValueError('Chọn đường dẫn khác dữ liệu đang dùng')
            with app.connect() as c,sqlite3.connect(name) as target:c.backup(target)
            messagebox.showinfo('Sao lưu','Đã lưu bản sao dữ liệu.')
    def schedule(self):
        enable_schedule();messagebox.showinfo('Đã bật nhắc','Windows đã lưu lịch nhắc mỗi ngày lúc 18:00. Có thể đóng app. Giữ nguyên thư mục app để lịch hoạt động.\nTắt nhắc: mở Task Scheduler và xóa SoGiaHanReminder.')

if __name__=='__main__':
    if '--remind' in sys.argv:reminder()
    else:
        root=tk.Tk();Desktop(root);root.mainloop()
