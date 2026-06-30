import requests
import xml.etree.ElementTree as ET
from datetime import datetime
import time

# 1. กำหนดรายชื่อช่องที่ต้องการดึงข้อมูล (สามารถเพิ่ม/ลด เลขช่องตรงนี้ได้เลย)
channel_list = [2, 3, 4, 5, 7, 10, 16, 18, 22, 23, 24, 25, 27, 29, 30, 31, 32, 33, 34, 35, 36, 101, 103, 104, 105, 106, 107, 109, 110, 111, 112, 503, 521, 523, 301, 302, 303, 304, 306, 205, 206, 210, 222, 202]

# 2. สร้างโครงสร้าง XMLTV ตัวหลัก
tv = ET.Element("tv", {"generator-info-name": "3BB GigaTV Auto Generator"})

print("--- เริ่มต้นการดึงข้อมูล EPG ---")

# วนลูปดึงข้อมูลทีละช่อง
for ch_num in channel_list:
    url = f"https://gigatv.3bbtv.co.th/wp-content/themes/changwattana/epg/{ch_num}.json"
    print(f"กำลังดึงข้อมูลช่อง: {ch_num}...")
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            print(f"❌ ไม่พบข้อมูลช่อง {ch_num} (Status: {response.status_code})")
            continue
            
        data = response.json()
        if not data:
            continue

        # สร้างหัวข้อช่อง <channel> (ดึงจากไอเทมแรก)
        first_item = data[0]
        ch_id = f"3bb.ch{first_item['channelID']}"
        ch_name = first_item['channelName']
        
        channel_el = ET.SubElement(tv, "channel", id=ch_id)
        display_name = ET.SubElement(channel_el, "display-name", lang="th")
        display_name.text = ch_name

        # วนลูปใส่รายการทีวีของช่องนั้นๆ <programme>
        for item in data:
            try:
                # แปลงเวลาให้อยู่ในฟอร์แมต XMLTV
                start_fmt = datetime.strptime(item['startTime'], "%Y-%m-%d %H:%M:%S").strftime("%Y%m%d%H%M%S +0700")
                end_fmt = datetime.strptime(item['endTime'], "%Y-%m-%d %H:%M:%S").strftime("%Y%m%d%H%M%S +0700")
                
                programme = ET.SubElement(tv, "programme", start=start_fmt, stop=end_fmt, channel=ch_id)
                
                title = ET.SubElement(programme, "title", lang="th")
                title.text = item.get('programName', 'ไม่ระบุชื่อรายการ')
                
                desc = ET.SubElement(programme, "desc", lang="th")
                desc.text = item.get('programName', '')
            except Exception as e:
                continue
                
        # หน่วงเวลานิดนึงเพื่อไม่ให้ยิงเซิร์ฟเวอร์ถี่เกินไป
        time.sleep(0.5)

    except Exception as e:
        print(f"เกิดข้อผิดพลาดกับช่อง {ch_num}: {e}")

# 3. บันทึกไฟล์ทั้งหมดรวมกันเป็น 3bb_epg.xml
tree = ET.ElementTree(tv)
tree.write("3bb_epg.xml", encoding="utf-8", xml_declaration=True)
print("--- ดึงข้อมูลสำเร็จ! สร้างไฟล์ 3bb_epg.xml เรียบร้อย ---")
