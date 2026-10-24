"""RFC 5545 export for a personal iPad calendar, with 18:00 ICT reminders."""
import datetime as dt
import hashlib


def text(value):
    return str(value or '').replace('\\','\\\\').replace('\r\n','\n').replace('\r','\n').replace('\n','\\n').replace(';','\\;').replace(',','\\,')


def fold(line):
    # RFC 5545 limits lines to 75 octets, not 75 Unicode characters.
    pieces=[];part='';size=0
    for ch in line:
        encoded=len(ch.encode('utf-8'))
        if size+encoded>75:
            pieces.append(part);part=' ';size=1
        part+=ch;size+=encoded
    pieces.append(part)
    return '\r\n'.join(pieces)


def export_calendar(accounts,now=None):
    now=now or dt.datetime.now(dt.timezone.utc)
    stamp=now.astimezone(dt.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    lines=['BEGIN:VCALENDAR','VERSION:2.0','PRODID:-//So Gia Han//Renewal Calendar//VI','CALSCALE:GREGORIAN',
           'METHOD:PUBLISH','X-WR-CALNAME:Sổ Gia Hạn','X-WR-TIMEZONE:Asia/Ho_Chi_Minh',
           'BEGIN:VTIMEZONE','TZID:Asia/Ho_Chi_Minh','BEGIN:STANDARD','DTSTART:19700101T000000',
           'TZOFFSETFROM:+0700','TZOFFSETTO:+0700','TZNAME:ICT','END:STANDARD','END:VTIMEZONE']
    for a in accounts:
        due=dt.date.fromisoformat(a['due']);anchor=int(a['anchor'])
        if not 1<=anchor<=31:raise ValueError('Ngày gốc không hợp lệ')
        uid=hashlib.sha256(f"{a['id']}|{a['email']}|{a['app']}".encode()).hexdigest()[:32]
        # Choosing the last available date among 28..anchor avoids skipping February.
        monthdays=','.join(str(day) for day in range(min(anchor,28),anchor+1))
        rule=f'FREQ=MONTHLY;BYMONTHDAY={monthdays}'+(';BYSETPOS=-1' if anchor>28 else '')
        amount=f"{int(a['amount']):,} VNĐ".replace(',','.')
        description=f"Tài khoản: {a['email']}\nSố tiền: {amount}\nThiết bị: {a.get('device','')}\nLịch nhắc riêng trên iPad, không tự đồng bộ hoặc xác nhận thanh toán trong app Windows."
        lines += ['BEGIN:VEVENT',f'UID:sgh-{uid}@sogiahan.local',f'DTSTAMP:{stamp}',
                  f'DTSTART;TZID=Asia/Ho_Chi_Minh:{due:%Y%m%d}T180000',
                  f'DTEND;TZID=Asia/Ho_Chi_Minh:{due:%Y%m%d}T181500',f'RRULE:{rule}',
                  'SUMMARY:'+text('Gia hạn '+a['app']), 'DESCRIPTION:'+text(description),'TRANSP:TRANSPARENT',
                  'BEGIN:VALARM','ACTION:DISPLAY','TRIGGER:-P3D','DESCRIPTION:'+text('Nhắc gia hạn '+a['app']+' · '+a['email']),
                  'END:VALARM','END:VEVENT']
    lines+=['END:VCALENDAR']
    return ('\r\n'.join(fold(line) for line in lines)+'\r\n').encode('utf-8')
