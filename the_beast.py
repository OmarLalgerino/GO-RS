import cloudscraper
from bs4 import BeautifulSoup
import csv
import os

def scrape_deep_link(url):
    scraper = cloudscraper.create_scraper()
    
    try:
        response = scraper.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')

        # 1. جلب الاسم
        title = soup.find('h1').text.strip() if soup.find('h1') else "مسلسل تركي"

        # 2. الغوص في "قلب" الصفحة لجلب رابط المشغل
        watch_link = ""
        
        # البحث عن المشغل في الـ Iframe (هذا هو قلب الفيديو)
        iframe = soup.find('iframe', src=True)
        if iframe:
            watch_link = iframe['src']
            # إذا كان الرابط يبدأ بـ // نضيف له https:
            if watch_link.startswith('//'):
                watch_link = 'https:' + watch_link
        
        # إذا لم يجد iframe، يبحث عن روابط السيرفرات في أزرار المشاهدة
        if not watch_link:
            server_list = soup.find('ul', class_='video-servers') # كود مشهور في قصة عشق
            if server_list:
                first_server = server_list.find('a', href=True)
                if first_server:
                    watch_link = first_server['href']

        # 3. حفظ البيانات في الملف بالترتيب المطلوب (اسم ثم رابط)
        file_name = 'database.csv'
        file_exists = os.path.isfile(file_name)
        
        with open(file_name, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            if not file_exists:
                writer.writerow(['name', 'url'])
            
            if watch_link:
                writer.writerow([title, watch_link])
                print(f"✅ تم سحب الرابط من قلب الموقع: {title}")
            else:
                print(f"❌ تعذر العثور على المشغل داخل الصفحة")

    except Exception as e:
        print(f"❌ خطأ برمي: {e}")

# الرابط المستهدف
target = "https://k.3sk.media/o5p4/"
scrape_deep_link(target)
