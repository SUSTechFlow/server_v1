import smtplib
from email.header import Header
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr
from email.mime.multipart import MIMEMultipart


class EmailSender():
    def _format_addr(self, s):
        name, addr = parseaddr(s)
        return formataddr((Header(name, 'utf-8').encode(), addr))

    def __init__(self):
        self.from_addr = 'verification@auto.sustechflow.top'
        self.password = '{{ I KNOW WHAT YOU ARE LOOKING FOR. }}'
        self.smtp_server = 'smtpdm.aliyun.com'

    def send_msg(self, msg_text, to_addr):
        msg = MIMEMultipart()
        msg.attach(MIMEText(msg_text, 'plain', 'utf-8'))
        msg['From'] = self._format_addr(f'SUSTechFlow: {self.from_addr}')
        msg['To'] = self._format_addr(to_addr)
        msg['Subject'] = Header('Sent by SUSTechFlow', 'utf-8').encode()

        server = smtplib.SMTP(self.smtp_server, 80)
        server.set_debuglevel(1)
        server.login(self.from_addr, self.password)
        server.sendmail(self.from_addr, to_addr, msg.as_string())
        server.quit()