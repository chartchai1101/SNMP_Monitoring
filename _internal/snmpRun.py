import asyncio
from pysnmp.hlapi.asyncio import (
    SnmpEngine,
    CommunityData,
    UdpTransportTarget,
    ContextData,
    ObjectType,
    ObjectIdentity,
    getCmd
)


async def snmp_get(oid, ip, community='orion', port=161):
    # ต้องใช้ await เพื่อเรียก create() ในการสร้าง UdpTransportTarget
    transport = await UdpTransportTarget.create((ip, port))

    iterator = getCmd(
        SnmpEngine(),
        CommunityData(community),
        transport,  # ใช้ตัวแปร transport ที่สร้างจาก .create()
        ContextData(),
        ObjectType(ObjectIdentity(oid))
    )

    # ต้องใช้ await สำหรับการดำเนินการของ getCmd
    errorIndication, errorStatus, errorIndex, varBinds = await iterator

    if errorIndication:
        print(f"Error: {errorIndication}")
        return None  # คืนค่า None เมื่อเกิดข้อผิดพลาด
    elif errorStatus:
        print(f"{errorStatus.prettyPrint()}")
        return None  # คืนค่า None หากเกิดข้อผิดพลาดในการดึงข้อมูล
    else:
        for varBind in varBinds:
            result = f'{varBind[1]}'  # คืนค่าที่ดึงได้
            return result  # คืนผลลัพธ์ที่ได้จาก OID

