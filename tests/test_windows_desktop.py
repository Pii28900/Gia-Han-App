"""Exercise real Tk forms and selection on the Windows build runner."""
import os
import sys
import tempfile
import unittest
from unittest.mock import patch

@unittest.skipUnless(sys.platform == 'win32', 'Windows GUI integration test')
class WindowsDesktopTests(unittest.TestCase):
    def test_add_and_delete_account_in_gui(self):
        import app
        import tkinter as tk
        from pathlib import Path
        with tempfile.TemporaryDirectory() as tmp:
            with patch.dict(os.environ, {'LOCALAPPDATA': tmp}):
                import desktop
            old_db=app.DB
            app.DB=Path(tmp)/'accounts.db'
            root=tk.Tk();root.withdraw()
            try:
                ui=desktop.Desktop(root)
                ui.add()
                form=next(w for w in root.winfo_children() if isinstance(w,tk.Toplevel))
                entries=[w for w in form.winfo_children() if isinstance(w,desktop.ttk.Entry)]
                values=['test@example.com','Youtube',app.today().isoformat(),'165000','PC']
                for widget,value in zip(entries,values):widget.delete(0,'end');widget.insert(0,value)
                save=next(w for w in form.winfo_children() if isinstance(w,desktop.ttk.Button))
                with patch.object(desktop.messagebox,'showinfo'):save.invoke()
                items=ui.table.get_children()
                self.assertEqual(len(items),1)
                self.assertEqual(app.due_accounts()[0]['email'],'test@example.com')
                ui.table.selection_set(items)
                with patch.object(desktop.messagebox,'askyesno',return_value=True),patch.object(desktop.messagebox,'showinfo'):
                    ui.delete()
                self.assertEqual(ui.table.get_children(),())
                self.assertEqual(app.due_accounts(),[])
            finally:
                root.destroy();app.DB=old_db
    def test_windows_schedule_updates_to_18(self):
        import desktop
        from types import SimpleNamespace
        with patch.object(desktop.subprocess,'run',return_value=SimpleNamespace(returncode=0)) as run:
            desktop.enable_schedule()
        command=run.call_args.args[0][-1]
        self.assertIn("-Daily -At '18:00'",command)
        self.assertIn('-Force',command)
