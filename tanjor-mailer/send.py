import os, json, ssl, smtplib
from datetime import datetime
from zoneinfo import ZoneInfo
from email.message import EmailMessage
from email.utils import make_msgid
import gspread
from google.oauth2.service_account import Credentials

def run():
    creds = Credentials.from_service_account_info(json.loads(os.environ['GOOGLE_SERVICE_ACCOUNT_JSON']), scopes=['https://www.googleapis.com/auth/spreadsheets'])
    book = gspread.authorize(creds).open_by_key(os.environ['SHEET_ID'])
    sheet = book.worksheet('邮件草稿')
    values = sheet.get_all_values()
    required = ['客户ID','公司名称','收件邮箱','邮件主题','英文邮件正文','发送状态','发送时间','发送结果']
    if not values or values[0][:8] != required:
        raise RuntimeError('表头应为：' + '、'.join(required))
    dry = os.getenv('DRY_RUN','true').lower() != 'false'
    count = 0
    for number, original in enumerate(values[1:], 2):
        row = original + [''] * max(0, 8-len(original))
        if row[5] != '批准发送' or row[6] or row[7]:
            continue
        recipient = row[2].strip()
        if recipient.count('@') != 1 or any(c in recipient for c in '\r\n,; <>') or not row[3].strip() or not row[4].strip():
            print(f'{row[0]} skipped: invalid recipient or empty content')
            continue
        if count >= 5:
            break
        count += 1
        if dry:
            print(f'{row[0]} ready (simulation; no email sent)')
            continue
        # Re-read before claiming. GitHub concurrency prevents overlapping runners.
        latest = sheet.get(f'A{number}:H{number}')[0]
        latest += [''] * max(0, 8-len(latest))
        if latest != row:
            raise RuntimeError('Row changed during run; stopped')
        stamp = datetime.now(ZoneInfo('Australia/Adelaide')).isoformat(timespec='seconds')
        msg = EmailMessage()
        msg['From'] = os.environ['SMTP_USER']
        msg['To'] = recipient
        msg['Subject'] = row[3]
        msg['Message-ID'] = make_msgid(domain='tanjortapes.com')
        msg.set_content(row[4])
        # Persist claim BEFORE SMTP: uncertain results require manual reconciliation.
        sheet.update(range_name=f'F{number}:H{number}', values=[['发送中',stamp,'已锁定；中断时请先核对邮箱，不要直接重发']])
        try:
            with smtplib.SMTP_SSL(os.environ['SMTP_HOST'], int(os.getenv('SMTP_PORT','465')), context=ssl.create_default_context(), timeout=40) as server:
                server.login(os.environ['SMTP_USER'],os.environ['SMTP_PASSWORD'])
                server.send_message(msg)
        except Exception:
            sheet.update(range_name=f'F{number}:H{number}', values=[['需核查',stamp,'发送异常或结果不确定；核对邮箱后再决定，程序不会自动重试']])
            raise RuntimeError('SMTP failed; details suppressed to protect credentials') from None
        sheet.update(range_name=f'F{number}:H{number}', values=[['已发送',stamp,'SMTP服务器已接受；不代表已送达收件箱']])
        print(f'{row[0]} accepted by SMTP')

if __name__ == '__main__':
    run()
