import cloudscraper
from bs4 import BeautifulSoup
import csv
import re
import os

# إعداد القناص
scraper = cloudscraper.create_scraper()

def get_video_links(page_url):
    """قناص الروابط: يبحث عن MP4, MKV, M3U8 والروابط المضمنة"""
    links = {"1080p": "", "720p": "", "480p": ""}
    try:
        res = scraper.get(page_url, timeout=10)
        content = res.text
        
        # 1. البحث الشامل عن جميع صيغ الفيديو (MP4, MKV, M3U8)
        # نستخدم Regex لمسح الكود بالكامل
        video_pattern = r'(https?://[^\s\'"]+\.(?:mp4|mkv|m3u8|webm)[^\s\'"]*)'
        found_videos = re.findall(video_pattern, content)
        
        if found_videos:
            for v_link in found_videos:
                # فلترة ذكية: إذا وجدنا mp4 و mkv لنفس الجودة، نفضل mp4 للسرعة
                v_lower = v_link.lower()
                if "1080" in v_lower or "fhd" in v_lower:
                    if not links["1080p"] or ".mp4" in v_lower: links["1080p"] = v_link
                elif "720" in v_lower or "hd" in v_lower:
                    if not links["720p"] or ".mp4" in v_lower: links["720p"] = v_link
                elif "480" in v_lower or "sd" in v_lower:
                    if not links["480p"] or ".mp4" in v_lower: links["480p"] = v_link

        # 2. الحل البديل: روابط المشاهدة أونلاين (Embed/Iframe)
        # إذا لم نجد روابط مباشرة، نسحب رابط المشغل
        if not links["720p"]:
            soup = BeautifulSoup(content, 'html.parser')
            iframes = soup.find_all('iframe', src=True)
            for ifrm in iframes:
                src = ifrm['src']
                if any(x in src for x in ['player', 'embed', 'mycima', 'vidoza']):
                    links["720p"] = src if src.startswith('http') else 'https:' + src
                    break

        return links
    except:
        return links

def update_database():
    source_url = "https://mycima.gold/category/series/%d9%85%d8%b3%d9%84%d8%b3%d9%84%d8%a7%d8%aa-%d8%aa%d8%b1%d9%83%d9%8a%d8%a9/"
    db_file = 'database.csv'
    all_data = []

    print(f"🔍 جاري فحص الموقع: {source_url}")
    try:
        res = scraper.get(source_url)
        soup = BeautifulSoup(res.content, 'html.parser')
        items = soup.find_all('div', class_='GridItem')

        for item in items[:20]: # فحص آخر 20 حلقة مضافة
            title_tag = item.find('strong') or item.find('h2')
            name = title_tag.text.strip() if title_tag else "حلقة جديدة"
            link = item.find('a')['href']
            
            print(f"📡 جاري قنص (MP4/MKV/Online) لـ: {name}")
            v_links = get_video_links(link)
            
            # إضافة وسم نوع الرابط للاسم لتمييزه في تطبيقك
            status = " (✅ MP4)" if ".mp4" in str(v_links) else " (📺 Online)"
            
            all_data.append({
                'name': name + status,
                'url_1080p': v_links['1080p'],
                'url_720p': v_links['720p'],
                'url_480p': v_links['480p']
            })

        # حفظ النتائج في الجدول
        with open(db_file, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['name', 'url_1080p', 'url_720p', 'url_480p'])
            writer.writeheader()
            writer.writerows(all_data)
        print("✨ تم تحديث جميع الروابط بنجاح!")
        
    except Exception as e:
        print(f"❌ حدث خطأ: {e}")

if __name__ == "__main__":
    update_database()
