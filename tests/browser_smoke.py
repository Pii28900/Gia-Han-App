"""Run with a real headless Chromium/Chrome; no private account data."""
import os
from pathlib import Path
import sys
import tempfile
import threading
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import app
from playwright.sync_api import sync_playwright, expect
from test_app import MoneyAndImportTests

def main():
 with tempfile.TemporaryDirectory() as folder:
  app.DB=Path(folder)/'accounts.db'
  server=app.ThreadingHTTPServer(('127.0.0.1',0),app.Handler)
  thread=threading.Thread(target=server.serve_forever);thread.start()
  try:
   with sync_playwright() as p:
    executable=os.getenv('CHROME_PATH')
    options={'headless':True}
    if executable:options['executable_path']=executable
    else:options['channel']='chrome'
    browser=p.chromium.launch(**options)
    page=browser.new_page(viewport={'width':1440,'height':1000})
    errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
    page.goto(f'http://127.0.0.1:{server.server_port}')
    expect(page.locator('#rows')).to_contain_text('Bắt đầu với danh sách')
    page.locator('#add').click()
    form=page.locator('#form')
    form.locator('[name=email]').fill('demo@example.com')
    form.locator('[name=app]').fill('ChatGPT')
    form.locator('[name=due]').fill(app.today().isoformat())
    form.locator('[name=amount]').fill('165000')
    form.locator('[name=device]').fill('Laptop cá nhân')
    page.locator('#save').click()
    expect(page.locator('#rows')).to_contain_text('demo@example.com')
    expect(page.locator('#rows')).to_contain_text('165.000')
    page.locator('[data-edit]').click()
    form.locator('[name=amount]').fill('175000');page.locator('#save').click()
    expect(page.locator('#rows')).to_contain_text('175.000')
    page.on('dialog',lambda dialog:dialog.accept())
    page.locator('[data-paid]').click()
    expect(page.locator('#soon')).to_have_text('0')
    fixture=Path(folder)/'HSD.xlsx';fixture.write_bytes(MoneyAndImportTests().workbook(True))
    page.locator('#file').set_input_files(fixture)
    expect(page.locator('#total')).to_have_text('2')
    page.locator('#file').set_input_files(fixture)
    expect(page.locator('#toast')).to_contain_text('0 tài khoản mới')
    page.locator('#search').fill('test@example.com')
    expect(page.locator('#rows tr')).to_have_count(1)
    page.locator('#search').fill('')
    if os.getenv('SCREENSHOT_OUT'):page.screenshot(path=os.environ['SCREENSHOT_OUT'],full_page=True)
    page.locator('#select-all').check();page.locator('#bulk-delete').click()
    expect(page.locator('#total')).to_have_text('0')
    # Verify layout remains usable on a narrow window.
    page.set_viewport_size({'width':390,'height':850})
    page.locator('#add').click();expect(page.locator('#editor')).to_be_visible()
    page.locator('#cancel').click()
    assert not errors,errors
    browser.close()
    print('PASS: Chrome add, edit, renew, Excel import/dedup, search, bulk delete and mobile layout; no JS errors')
  finally:
   server.shutdown();server.server_close();thread.join()
if __name__=='__main__':main()
