import feedparser
import csv
import os
import requests
import re
import cloudscraper

SOURCES = [
    "https://nyaa.si/?page=rss",
    "https://www.tokyotosho.info/rss.php"
]
DB_FILE = 'database.csv'

def get_clean_hash_link(entry):
    """استخراج الـ Hash من الرابط وتحويله لرابط مشاهدة"""
    # البحث عن رابط الماغنيت في الإضافات (الماغنيت يحتوي على الـ Hash)
    link = entry.link
    if hasattr(entry, 'nyaa_infohash'): # خاص بموقع Nyaa
        return f"https://webtor.io/player/embed/{entry.nyaa_infohash}"
    
    # محاولة إيجاد الـ Hash داخل الرابط نفسه إذا كان ماغنيت
    hash_match = re.search(r'btih:([a-fA-F0-9]{40})', link)
    if hash_match:
        return f"https://webtor.io/player/embed/{hash_match.group(1).lower()}"
    
    return link

def translate_to_arabic(text):
    try:
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&tl=ar&dt=t&q={requests.utils.quote(text)}"
        res = requests.get(url, timeout=5)
        return res.json()[0][0][0]
    except:
        return text

def start_bot():
    database = {}
    # ملاحظة: لن نقرأ الملف القديم هذه المرة لضمان تحويل كل الروابط لـ Hash
    scraper = cloudscraper.create_scraper()
    print("🚀 جاري استخراج الروابط وتحويلها إلى Hash للمشاهدة المباشرة...")

    for rss_url in SOURCES:
        try:
            resp = scraper.get(rss_url, timeout=15)
            feed = feedparser.parse(resp.text)
            
            for entry in feed.entries[:30]:
                name_en = entry.title
                # تحويل الرابط إلى Hash Link فوراً
                streaming_link = get_clean_hash_link(entry)
                
                if "webtor.io" in streaming_link: # نأخذ فقط الروابط التي نجح تحويلها
                    name_ar = translate_to_arabic(name_en)
                    database[name_en] = {
                        'name_ar': name_ar,
                        'name_en': name_en,
                        'torrent_url': streaming_link,
                        'status': 'جاهز للمشاهدة 🍿'
                    }
        except Exception as e:
            print(f"❌ خطأ: {e}")

    with open(DB_FILE, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['name_ar', 'name_en', 'torrent_url', 'status']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(database.values())
    print(f"✅ تم التحديث! الملف الآن يحتوي على روابط Hash فقط.")

if __name__ == "__main__":
    start_bot()
