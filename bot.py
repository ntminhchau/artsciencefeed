import requests
import feedparser
import random
import os
import time

TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

def get_science_news(limit=3):
    # Sử dụng từ khóa hấp dẫn để lọc tin trên Google News
    keywords = "discovery+space+astronomy+archaeology+biology+physics"
    url = f"https://news.google.com/rss/search?q={keywords}+when:7d&hl=en-US&gl=US&ceid=US:en"
    feed = feedparser.parse(url)
    
    results = []
    # Loại bỏ các tin có tiêu đề chứa từ khóa nhàm chán như "proposals", "fund", "meeting"
    boring_words = ["fund", "proposals", "meeting", "faculty", "grant", "workshop"]
    
    for entry in feed.entries:
        if not any(word in entry.title.lower() for word in boring_words):
            results.append(f"🔬 **KHÁM PHÁ KHOA HỌC**\n📌 {entry.title}\n🔗 {entry.link}")
        if len(results) >= limit:
            break
    return results

def get_art_news(limit=3):
    results = []
    try:
        # Lấy danh sách tác phẩm từ Art Institute of Chicago
        response = requests.get("https://api.artic.edu/api/v1/artworks?limit=100", timeout=20).json()
        art_list = [item for item in response['data'] if item.get('image_id') and item.get('artist_display')]
        
        # Lấy ngẫu nhiên 3 tác phẩm khác nhau
        selected_art = random.sample(art_list, k=min(limit, len(art_list)))
        
        for artwork in selected_art:
            title = artwork.get('title', 'Vô danh')
            artist = artwork.get('artist_display', 'Ẩn danh')
            image_id = artwork['image_id']
            img_url = f"https://www.artic.edu/iiif/2/{image_id}/full/843,/0/default.jpg"
            caption = f"🎨 **NGHỆ THUẬT MỖI NGÀY**\n🖼 **Tác phẩm:** {title}\n👨‍🎨 **Nghệ sĩ:** {artist}"
            results.append((caption, img_url))
    except Exception as e:
        print(f"Lỗi Art: {e}")
    return results

def send_telegram(message, image=None):
    base_url = f"https://api.telegram.org/bot{TOKEN}/"
    try:
        if image:
            requests.post(base_url + "sendPhoto", data={'chat_id': CHAT_ID, 'caption': message, 'parse_mode': 'Markdown'}, files={'photo': requests.get(image).content}, timeout=30)
        else:
            requests.post(base_url + "sendMessage", data={'chat_id': CHAT_ID, 'text': message, 'parse_mode': 'Markdown'}, timeout=30)
    except Exception as e:
        print(f"Lỗi gửi: {e}")

if __name__ == "__main__":
    # Gửi 3 tin Khoa học
    sci_news_list = get_science_news(limit=3)
    for news in sci_news_list:
        send_telegram(news)
        time.sleep(1) # Nghỉ 1 giây để tránh bị Telegram coi là spam

    # Gửi 3 tin Nghệ thuật
    art_news_list = get_art_news(limit=3)
    for caption, img in art_news_list:
        send_telegram(caption, img)
        time.sleep(1)
