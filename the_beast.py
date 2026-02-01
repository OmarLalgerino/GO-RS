import feedparser
import csv
import requests
import re
import cloudscraper
import os

# مصادر الأنمي المترجم للعربية
SOURCES = [
    "https://nyaa.si/?page=rss&q=Arabic+1080p",
    "https://nyaa.si/?page=rss&q=Arabic+720p",
    "https://nyaa.si/?page=rss&q=Arabic+480p",
    "https://www.tokyotosho.info/rss.php?filter=1,11&z=Arabic"
]

DB_FILE = 'database.csv'

def translate_to_arabic_only(text):
    """تنظيف الاسم من الشوائب الإنجليزية وترجمته"""
    # حذف الكلمات التقنية والرموز
    clean_text = re.sub(r'\[.*?\]|\(.*?\)|1080p|720p|480p|HEVC|x264|x265|AAC|Vostfr|Multi', '', text).strip()
    try:
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl=ar&dt=t&q={requests.utils.quote(clean_text)}"
        res = requests.get(url, timeout=5)
        return res.json()[0][0][0]
    except:
        return clean_text

def get_clean_hash_link(entry):
    """استخراج رابط المشغل المباشر"""
    if hasattr(entry, 'nyaa_infohash'):
        return f"https://webtor.io/player/embed/{entry.nyaa_infohash}"
    link = getattr(entry, 'link', '')
    hash_match = re.search(r'btih:([a-fA-F0-9]{40})', link)
    if hash_match:
        return f"https://webtor.io/player/embed/{hash_match.group(1).lower()}"
    return None

def start_bot():
    scraper = cloudscraper.create_scraper()
    print("🧹 تنظيف القائمة القديمة وجلب أحدث الحلقات...")

    # نستخدم dictionary لمنع التكرار (الاسم هو المفتاح)
    fresh_database = {}

    for rss_url in SOURCES:
        try:
            resp = scraper.get(rss_url, timeout=15)
            feed = feedparser.parse(resp.text)
            
            # نأخذ أول 15 حلقة فقط من كل مصدر لضمان أنها "جديدة جداً"
            for entry in feed.entries[:15]:
                link = get_clean_hash_link(entry)
                if link:
                    arabic_title = translate_to_arabic_only(entry.title)
                    
                    # جودة الفيديو بالعربي
                    if "1080p" in entry.title: q = "1080p - FHD"
                    elif "720p" in entry.title: q = "720p - HD"
                    else: q = "480p - SD"
                    
                    # حفظ بأسماء أعمدة عربية
                    fresh_database[entry.title] = {
                        'اسم_الأنمي': arabic_title,
                        'رابط_المشاهدة': link,
                        'الجودة': q
                    }
        except:
            continue

    # حفظ الملف بوضعية 'w' لمسح القديم ووضع الجديد لضمان عمل الروابط
    with open(DB_FILE, 'w', newline='', encoding='utf-8') as f:
        columns = ['اسم_الأنمي', 'رابط_المشاهدة', 'الجودة']
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        writer.writerows(fresh_database.values())
    
    print(f"✅ تم تحديث المكتبة بـ {len(fresh_database)} حلقة جديدة تعمل الآن!")

if __name__ == "__main__":
    start_bot()
