import asyncio
from snmpRun import snmp_get  # นำเข้าเฉพาะฟังก์ชัน snmp_get
from datetime import datetime

# ฟังก์ชันเพื่อให้ได้เวลาปัจจุบันในรูปแบบที่กำหนด
def get_current_time():
    now = datetime.now()
    formatted_time = now.strftime("%A, %B %d, %Y %I:%M %p")
    return formatted_time

# สร้างลิสต์สำหรับเก็บข้อมูล
devices_list = []
snmp_list = []
results = {}  # สร้าง dictionary เพื่อเก็บผลลัพธ์

# เปิดไฟล์และอ่านข้อมูล
with open('data/device.txt', 'r') as file:
    for line in file:
        devices_list.append(line.strip())  # ลบช่องว่างและ newline ก่อนเก็บในลิสต์

with open('data/snmp.txt', 'r') as file:
    for line in file:
        snmp_list.append(line.strip())  # ลบช่องว่างและ newline ก่อนเก็บในลิสต์

# ฟังก์ชันหลัก
async def main():
    tasks = []  # ลิสต์สำหรับเก็บ tasks
    for ip in devices_list:
        for oid in snmp_list:
            # สร้าง task สำหรับแต่ละ snmp_get()
            tasks.append(asyncio.create_task(fetch_and_store_result(oid, ip)))
    # รันทุก tasks พร้อมกัน
    await asyncio.gather(*tasks)

# ฟังก์ชันสำหรับการดึงข้อมูลและเก็บผลลัพธ์ลงใน object
async def fetch_and_store_result(oid, ip):
    result = await snmp_get(oid, ip)  # เรียก snmp_get และรับค่าที่ดึงมา
    
    if ip not in results:
        results[ip] = {}
    
    results[ip][oid] = result  # เก็บผลลัพธ์ใน dictionary

    # print(f"Stored result for {ip}, OID {oid}: {result}")
    # print(results["10.3.199.101"])
# ฟังก์ชันทำงานซ้ำตามเวลา interval ที่กำหนด
async def run_periodically(interval):
    while True:
        await main()  # เรียกฟังก์ชันหลัก
        # print(f"Current results: {results}")  # แสดงผลลัพธ์ที่เก็บใน object
        for ip_device in devices_list:
            # ตรวจสอบว่ามี status หรือไม่ ถ้าไม่มีให้ใส่ค่าเป็น 'normal'
            if 'status' not in results[ip_device]:
                results[ip_device]['status'] = 'normal'    
            # ถ้า status เป็น 'waitClear' ข้ามการทำงานไป (ไม่ทำอะไร)
            elif results[ip_device]['status'] == 'waitClear':
                pass  # ไม่ต้องทำอะไรเมื่อสถานะเป็น waitClear
            
            # ถ้าค่า OID ไม่ใช่ค่าว่าง เปลี่ยนสถานะเป็น 'alert'
            elif results[ip_device]['1.3.6.1.4.1.9.9.719.1.1.1.1.11.167773054'] != '':
                if results[ip_device]['status'] != 'waitClear':
                    print(results[ip_device]['1.3.6.1.4.1.9.9.719.1.1.1.1.11.167773054'])
                    results[ip_device]['status'] = 'alert'
            
            # ถ้าค่า OID เป็นค่าว่าง เปลี่ยนสถานะเป็น 'clear'
            elif results[ip_device]['1.3.6.1.4.1.9.9.719.1.1.1.1.11.167773054'] == '':
                if results[ip_device]['status'] != 'normal':
                    results[ip_device]['status'] = 'clear'
            print(f'Monitoring is : [{ip_device}] Power supply status is {results[ip_device]['status']}')
        print(f"[{get_current_time()}] Waiting for 10 Minute before next run...")
        await asyncio.sleep(interval)  # รอเป็นเวลา interval (วินาที)
        return results
# เรียกใช้งาน async function โดยให้ทำซ้ำทุกๆ 10 วินาที
# asyncio.run(run_periodically(10))

