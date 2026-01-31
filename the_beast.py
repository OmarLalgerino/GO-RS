import cloudscraper
import re
import csv
from bs4 import BeautifulSoup

scraper = cloudscraper.create_scraper(browser={'browser': 'chrome','platform': 'android','desktop': False})

def get_streaming_player(url):
    """البحث عن روابط المشغل (Embed) داخل الصفحة"""
    try:
        res = scraper.get(url, timeout=10)
        # البحث عن سيرفرات: Dood, Uqload, Upstream, Vidoza
        pattern = r'https?://(?:doodstream\.com|dood\.to|dood\.so|uqload\.com|uqload\.co|upstream\.to|vidoza\.net)/[e|embed][^\s\'"<>]+'
        matches = re.findall(pattern, res.text)
        return matches[0] if matches else ""
    except:
        return ""

def update_big_database():
    # قائمة بـ "مناطق الصيد" (أقسام المسلسلات التركية في مواقع مختلفة)
    hunting_zones = [
        "https://wecima.show/category/%d9%85%d8%b3%d9%84%d8%b3%d9%84%d8%a7%d8%aa-%d8%aa%d8%b1%d9%83%d9%8a%d8%a9/",
        "https://arabseed.show/category/مسلسلات-تركية/",
        "https://esheeq.org/",
        "https://4helau.tv/category/%d9%85%d8%b3%d9%84%d8%b3%d9%84%d8%a7%d8%aa-%d8%aa%d8%b1%d9%83%d9%8a%d8%a9-1/"
    ]
    
    all_episodes = []
    db_file = 'database.csv'

    for zone in hunting_zones:
        print(f"🌍 جاري مسح المنطقة: {zone}")
        try:
            res = scraper.get(zone, timeout=15)
            soup = BeautifulSoup(res.text, 'html.parser')
            
            # محاولة العثور على جميع الروابط في الصفحة التي قد تكون حلقات
            links = soup.find_all('a', href=True)
            
            count = 0
            for link in links:
                if count >= 30: break # سحب 30 حلقة من كل موقع (الإجمالي 120 حلقة)
                
                href = link['href']
                title = link.text.strip()
                
                # التأكد أن الرابط يخص حلقة (تصفية الروابط غير المهمة)
                if "حلقة" in title or "episode" in title.lower():
                    print(f"🔍 فحص السيرفر لـ: {title}")
                    player = get_streaming_player(href)
                    
                    if player:
                        all_episodes.append({'name': title, 'player_url': player})
                        count += 1
                        print(f"✅ تم القنص!")

        except Exception as e:
            print(f"⚠️ فشل دخول المنطقة {zone}: {e}")

    # حفظ كل الصيد في ملف CSV واحد
    if all_episodes:
        with open(db_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['name', 'player_url'])
            writer.writeheader()
            writer.writerows(all_episodes)
        print(f"✨ مبروك! قمت بصيد {len(all_episodes)} حلقة بنجاح.")

if __name__ == "__main__":
    update_big_database()
