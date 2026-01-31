import cloudscraper
import re
import csv
from bs4 import BeautifulSoup

# إعداد المتصفح الوهمي لتجاوز حماية المواقع
scraper = cloudscraper.create_scraper(browser={'browser': 'chrome','platform': 'android','desktop': False})

def sniper_others_links(page_url):
    """هذه الدالة تدخل لصفحة المسلسل وتصطاد روابط السيرفرات التي رفعها غيرك"""
    links = {"1080p": "", "720p": "", "480p": ""}
    try:
        res = scraper.get(page_url, timeout=15)
        html = res.text
        
        # البحث عن روابط السيرفرات الجاهزة (Uqload, Dood, Upstream)
        dood = re.findall(r'https?://(?:doodstream\.com|dood\.to|dood\.so|dood\.li)/e/([a-z0-9]+)', html)
        uqload = re.findall(r'https?://(?:uqload\.com|uqload\.co)/embed-([a-z0-9]+)', html)
        upstream = re.findall(r'https?://(?:upstream\.to|upstream\.org)/embed-([a-z0-9]+)', html)

        # تحويل الأكواد المكتشفة لروابط كاملة تعمل في تطبيقك أونلاين
        if dood: links["1080p"] = f"https://dood.to/e/{dood[0]}"
        if uqload: links["720p"] = f"https://uqload.com/embed-{uqload[0]}.html"
        if upstream: links["480p"] = f"https://upstream.to/embed-{upstream[0]}.html"
        
        return links
    except:
        return links

def update_database():
    # رابط الموقع الذي سنصطاد منه (يمكنك تغييره لأي موقع يعرض مسلسلات)
    source_url = "https://wecima.show/category/%d9%85%d8%b3%d9%84%d8%b3%d9%84%d8%a7%d8%aa-%d8%aa%d8%b1%d9%83%d9%8a%d8%a9/"
    db_file = 'database.csv'
    all_data = []

    print(f"🚀 البدء في قنص روابط السيرفرات من: {source_url}")
    try:
        res = scraper.get(source_url)
        soup = BeautifulSoup(res.text, 'html.parser')
        items = soup.find_all('div', class_='GridItem')

        for item in items[:15]: # سحب آخر 15 حلقة
            name = item.find('strong').text.strip() if item.find('strong') else "حلقة جديدة"
            link = item.find('a')['href']
            
            print(f"📡 جاري فحص صفحة: {name}")
            v_links = sniper_others_links(link)
            
            all_data.append({
                'name': name,
                'url_1080p': v_links['1080p'],
                'url_720p': v_links['720p'],
                'url_480p': v_links['480p']
            })

        # حفظ النتائج في ملف CSV
        with open(db_file, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['name', 'url_1080p', 'url_720p', 'url_480p'])
            writer.writeheader()
            writer.writerows(all_data)
        print("✅ المهمة تمت! الملف جاهز الآن بالروابط.")
    except Exception as e:
        print(f"❌ خطأ: {e}")

if __name__ == "__main__":
    update_database()
