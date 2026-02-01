import os
import subprocess
import sys

# خطوة إجبارية: تثبيت مكتبة requests تلقائياً إذا كانت مفقودة
try:
    import requests
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
    import requests

import re
import csv

def run_update():
    # رابط جلب القنوات العربية من GitHub
    source_url = "https://raw.githubusercontent.com/iptv-org/iptv/master/streams/ar.m3u"
    channels = []
    
    print("جاري جلب الروابط وفحصها...")
    try:
        response = requests.get(source_url, timeout=15)
        # استخراج الاسم والرابط (URL)
        matches = re.findall(r'#EXTINF:.*?,(.*?)\n(http.*?\.m3u8)', response.text)
        
        for name, url in matches[:40]: # جلب 40 قناة
            channels.append({
                'id': len(channels) + 1,
                'title': name.strip(),
                'image': 'https://via.placeholder.com/150?text=TV',
                'url': url.strip()
            })
            
        # إنشاء ملف database.csv (سيتم إنشاؤه حتى لو حذفته)
        with open('database.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['id', 'title', 'image', 'url'])
            writer.writeheader()
            writer.writerows(channels)
        print("✅ تم تحديث الجدول بنجاح!")
    except Exception as e:
        print(f"❌ حدث خطأ: {e}")

if __name__ == "__main__":
    run_update()
