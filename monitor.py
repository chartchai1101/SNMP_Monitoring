import asyncio
import aiosmtplib
from email.message import EmailMessage
from process import run_periodically
from process import results
from datetime import datetime

# ฟังก์ชันเพื่อให้ได้เวลาปัจจุบันในรูปแบบที่กำหนด
def get_current_time():
    now = datetime.now()
    formatted_time = now.strftime("%A, %B %d, %Y %I:%M %p")
    return formatted_time

# ฟังก์ชันส่งอีเมลแบบอะซิงโครนัส
async def send_auto_email(subject, body, to_email, cc_email, from_email, from_password):
    msg = EmailMessage()
    msg.set_content(body)
    msg['Subject'] = subject
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Cc'] = cc_email

    recipients = [to_email] + cc_email.split(",")  # แยกอีเมลใน CC ด้วยการคั่นด้วยจุลภาค
    try:
        await aiosmtplib.send(
            msg,
            hostname="smtp.gmail.com",
            port=465,
            username=from_email,
            password=from_password,
            use_tls=True,
        )
        print(f"Email sent to {to_email} with CC to {cc_email}")
    except Exception as e:
        print(f"Failed to send email: {e}")

# ฟังก์ชันหลักที่รันแบบวนลูป และเช็คค่าจาก results
async def run_and_send_email(interval, from_email, from_password, to_email, cc_email):
    while True:
        await run_periodically(interval)  # เรียกฟังก์ชันหลักที่วนลูปตรวจสอบ

        keys_to_remove = []

        for ip_device, data in results.items():
            if 'status' in data and data['status'] == 'normal':
                keys_to_remove.append(ip_device)  # เก็บคีย์ที่ต้องการลบ
            elif 'status' in data and data['status'] == 'waitClear':
                pass
            elif 'status' in data and data['status'] == 'alert':
                subject = f"Alert Power Supply from device : {data['1.3.6.1.4.1.9.9.719.1.9.6.1.6.1']}"
                body = f"""Dear Valued Customer,

Thank you for using our services. At this moment, we would like to provide you with the following notification:

[Node]: {data['1.3.6.1.4.1.9.9.719.1.9.6.1.6.1']} ({data['1.3.6.1.4.1.9.9.719.1.9.35.1.47.1']})

[Node Details]: {data['1.3.6.1.2.1.1.1.0']}
                
[IP Management]: {ip_device}

[Status]: Alarm Raised

[Alert]: {data['1.3.6.1.4.1.9.9.719.1.1.1.1.11.167773054']}

[Time Occurred]: {get_current_time()}

If you have any queries regarding the information contained in this email, please do not hesitate to contact us.

Sincerely,
True Managed Network Services
SETNET3 Staff
Phone: 02-009-9080

Developed by AIT
 """
                await send_auto_email(subject, body, to_email, cc_email, from_email, from_password)
                data['status'] = 'waitClear'
                print(f"Status for {ip_device} has been set to 'waitClear'.")
            elif 'status' in data and data['status'] == 'clear':
                subject = f"Clear Power Supply from device : {data['1.3.6.1.4.1.9.9.719.1.9.6.1.6.1']}"
                body = f"""Dear Valued Customer,

Thank you for using our services. At this moment, we would like to provide you with the following notification:

[Node]: {data['1.3.6.1.4.1.9.9.719.1.9.6.1.6.1']} ({data['1.3.6.1.4.1.9.9.719.1.9.35.1.47.1']})

[Node Details]: {data['1.3.6.1.2.1.1.1.0']}

[IP]: {ip_device}

[Status]: Alarm Clear

[Alert]: Power Supply is normal

[Time Finished]: {get_current_time()}

If you have any queries regarding the information contained in this email, please do not hesitate to contact us.

Sincerely,
True Managed Network Services
SETNET3 Staff
Phone: 02-009-9080

Developed by AIT
"""
                await send_auto_email(subject, body, to_email, cc_email, from_email, from_password)
                data['status'] = 'normal'
                print(f"Status for {ip_device} has been set to 'clear'.")

        for key in keys_to_remove:
            results.pop(key, None)  # ลบคีย์ที่มีสถานะ normal ออกจาก results

        await asyncio.sleep(interval)

# กำหนดค่าเริ่มต้นสำหรับการส่งอีเมล
from_email = "devby.ait.operation@gmail.com"
from_password = "sovr jjsx goun vmbv"  # ใช้ App Password ถ้าเป็น Gmail
to_email = "chartchai.d@ait.co.th"
cc_email = "chartchai1101@gmail.com,sangousaart@gmail.com"

# เรียกใช้งาน async function
asyncio.run(run_and_send_email(300, from_email, from_password, to_email, cc_email))
