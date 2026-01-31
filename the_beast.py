import cloudscraper
from bs4 import BeautifulSoup
import csv
import os
import requests

# إعداد القناص لتجاوز الحماية
scraper = cloudscraper.create_scraper()

def check_link_status(url):
    """يفحص إذا كان الرابط لا يزال يعمل"""
    try:
        response = requests.head(url, timeout=5)
        return response.status_code == 200
    except:
        return False

def get_video_links(page_url):
    """يسحب روابط الجودات من قلب الصفحة"""
    links = {"1080p": "", "720p": "", "480p": ""}
    try:
        res = scraper.get(page_url)
        soup = BeautifulSoup(res.content, 'html.parser')
        
        # البحث عن الروابط المباشرة (mp4, m3u8)
        # ملاحظة: يتم تخصيص البحث حسب بنية الموقع المستهدف
        all_a = soup.find_all('a', href=True)
        for a in all_a:
            href = a['href']
            if any(ext in href for ext in ['.mp4', '.m3u8', '.mkv']):
                if "1080" in href or "fhd" in href.lower(): links["1080p"] = href
                elif "720" in href or "hd" in href.lower(): links["720p"] = href
                elif "480" in href or "sd" in href.lower(): links["480p"] = href
        
        # إذا لم يجد روابط مباشرة، يأخذ رابط المشغل (Iframe) كخيار بديل
        if not links["720p"]:
            iframe = soup.find('iframe', src=True)
            if iframe: links["720p"] = iframe['src']
            
        return links
    except:
        return links

def update_database():
    source_url = "https://arabseed.show/category/مسلسلات-تركية/" # مثال لموقع مضمون
    db_file = 'database.csv'
    temp_data = []

    # 1. قراءة البيانات القديمة لفحصها
    if os.path.exists(db_file):
        with open(db_file, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # فحص الرابط (إذا كان معطلاً سيتم تحديثه لاحقاً)
                if check_link_status(row['url_720p']):
                    temp_data.append(row)

    # 2. سحب الحلقات الجديدة والقديمة من الموقع
    res = scraper.get(source_url)
    soup = BeautifulSoup(res.content, 'html.parser')
    items = soup.find_all('div', class_='MovieBlock') # تخصيص حسب الموقع

    for item in items[:20]: # سحب آخر 20 حلقة
        name = item.find('h2').text.strip()
        link = item.find('a')['href']
        
        # تجنب التكرار: إذا كان الاسم موجوداً والرابط يعمل، تخطاه
        if any(d['name'] == name for d in temp_data):
            continue
            
        v_links = get_video_links(link)
        temp_data.append({
            'name': name,
            'url_1080p': v_links['1080p'],
            'url_720p': v_links['720p'],
            'url_480p': v_links['480p']
        })

    # 3. حفظ الجدول النهائي (الاسم ثم الروابط)
    with open(db_file, mode='w', newline='', encoding='utf-8') as f:
        fieldnames = ['name', 'url_1080p', 'url_720p', 'url_480p']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(temp_data)
    
    print("✅ تم تحديث القاعدة وفحص الروابط بنجاح.")

if __name__ == "__main__":
    update_database()
