import requests
from bs4 import BeautifulSoup
import csv
import os

# إعدادات الموقع والمخرجات
BASE_URL = "https://mycima.rip"
DB_FILE = "database.csv"

def get_video_sources(movie_page_url):
    """استخراج روابط السيرفرات والجودات من صفحة الفيلم"""
    sources = {"1080p": "", "720p": "", "480p": ""}
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        response = requests.get(movie_page_url, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # البحث عن روابط المشاهدة (تعدل حسب هيكل الموقع الحالي)
        # ملاحظة: MyCima غالباً يستخدم سيرفرات خارجية مثل MyStream أو Upstream
        watch_servers = soup.select('.WatchServersList li')
        
        for server in watch_servers:
            btn = server.find('btn')
            if btn:
                quality = btn.text.strip()
                link = btn.get('data-url') # الرابط المباشر للمشغل
                
                if "1080" in quality: sources["1080p"] = link
                elif "720" in quality: sources["720p"] = link
                elif "480" in quality: sources["480p"] = link
        
        return sources
    except:
        return sources

def update_database():
    """قراءة الأفلام الجديدة وتحديث قاعدة البيانات مع الحفاظ على القديم"""
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(BASE_URL, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # جلب قائمة الأفلام من الصفحة الرئيسية
    movie_items = soup.select('.GridItem')
    
    # قراءة البيانات القديمة لتجنب التكرار
    existing_movies = {}
    if os.path.exists(DB_FILE):
        with open(DB_FILE, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                existing_movies[row['Name']] = row

    new_data = []
    for item in movie_items:
        name = item.find('strong').text.strip()
        link = item.find('a')['href']
        
        # إذا كان الفيلم موجوداً، نفحص صلاحية الرابط، إذا لم يكن موجوداً نسحبه
        if name not in existing_movies:
            print(f"جلب فيلم جديد: {name}")
            sources = get_video_sources(link)
            new_data.append({
                "Name": name,
                "URL_1080": sources["1080p"],
                "URL_720": sources["720p"],
                "URL_480": sources["480p"],
                "Status": "Active"
            })
        else:
            # تحديث الفيلم القديم إذا كان الرابط معطلاً (هنا تضع منطق الفحص)
            new_data.append(existing_movies[name])

    # حفظ النتائج في ملف CSV
    keys = ["Name", "URL_1080", "URL_720", "URL_480", "Status"]
    with open(DB_FILE, mode='w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(new_data)

if __name__ == "__main__":
    update_database()
