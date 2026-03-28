import requests
import feedparser
import random
import os
import time

TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

def get_science_news(limit=3):
    keywords = "discovery+space+astronomy+archaeology+biology+physics"
    url = f"https://news.google.com/rss/search?q={keywords}+when:7d&hl=en-US&gl=US&ceid=US:en"
    feed = feedparser.parse(url)
    
    results = []
    boring_words = ["fund", "proposals", "meeting", "faculty", "grant", "workshop"]
    
    for entry in feed.entries:
        if not any(word in entry.title.lower() for word in boring_words):
            # Tạo link rút gọn kiểu HTML
            short_msg = f"🔬 <b>KHÁM PHÁ KHOA HỌC</b>\n📌 {entry.title}\n👉 <a href='{entry.link}'>Xem chi tiết tại đây</a>"
            results.append(short_msg)
        if len(results) >= limit:
            break
    return results

def get_art_news(limit=3):
    results = []
    try:
        # Tăng limit lấy dữ liệu để tránh hụt tin
        response = requests.get("https://api.artic.edu/api/v1/artworks?limit=80", timeout=20).json()
        art_list = [item for item in response['data'] if item.get('image_id')]
        
        selected_art = random.sample(art_list, k=min(limit, len(art_list)))
        
        for artwork in selected_art:
            title = artwork.get('title', 'Vô danh')
            artist = artwork.get('artist_display', 'Ẩn danh')
            image_id = artwork['image_id']
            img_url = f"https://www.artic.edu/iiif/2/{image_id}/full/843,/0/default.jpg"
            # Chú thích rút gọn
            caption = f"🎨 <b>NGHỆ THUẬT MỖI NGÀY</b>\n🖼 <b>{title}</b>\n👨‍🎨 {artist}"
            results.append((caption, img_url))
    except Exception as e:
        print(f"Lỗi Art: {e}")
    return results

def send_telegram(message, image=None):
    # Dùng parse_mode='HTML' để link trông gọn hơn
    base_url = f"https://api.telegram.org/bot{TOKEN}/"
    try:
        if image:
            data = {'chat_id': CHAT_ID, 'caption': message, 'parse_mode': 'HTML'}
            # Gửi link ảnh trực tiếp thay vì tải file để tránh lỗi timeout
            params = {'photo': image}
            requests.get(base_url + "sendPhoto", params={**data, **params}, timeout=30)
        else:
            data = {'chat_id': CHAT_ID, 'text': message, 'parse_mode': 'HTML', 'disable_web_page_preview': False}
            requests.post(base_url + "sendMessage", data=data, timeout=30)
    except Exception as e:
        print(f"Lỗi gửi tin: {e}")

if __name__ == "__main__":
    # Gửi tin Khoa học
    sci_news = get_science_news(limit=3)
    for msg in sci_news:
        send_telegram(msg)
        time.sleep(2) # Nghỉ lâu hơn xíu để Telegram không chặn

    # Gửi tin Nghệ thuật
    art_news = get_art_news(limit=3)
    for caption, img in art_news:
        send_telegram(caption, img)
        time.sleep(2)
