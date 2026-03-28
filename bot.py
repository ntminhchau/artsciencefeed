import requests
import feedparser
import random
import os

# Cấu hình từ GitHub Secrets
TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

def get_science_news():
    feed = feedparser.parse("https://phys.org/rss-feeds/main-feed/")
    entry = random.choice(feed.entries[:10]) # Lấy ngẫu nhiên 1 trong 10 tin mới nhất
    return f"🔬 **KHOA HỌC HÔM NAY**\n\nTiêu đề: {entry.title}\nLink: {entry.link}"

def get_art_news():
    # Lấy ngẫu nhiên một tác phẩm nghệ thuật
    response = requests.get("https://api.artic.edu/api/v1/artworks?limit=100").json()
    artwork = random.choice(response['data'])
    title = artwork['title']
    artist = artwork['artist_display']
    image_id = artwork['image_id']
    image_url = f"https://www.artic.edu/iiif/2/{image_id}/full/843,/0/default.jpg"
    return f"🎨 **NGHỆ THUẬT MỖI NGÀY**\n\nTác phẩm: {title}\nNghệ sĩ: {artist}", image_url

def send_telegram(message, image=None):
    base_url = f"https://api.telegram.org/bot{TOKEN}/"
    if image:
        requests.post(base_url + "sendPhoto", data={'chat_id': CHAT_ID, 'caption': message, 'parse_mode': 'Markdown'}, files={'photo': requests.get(image).content})
    else:
        requests.post(base_url + "sendMessage", data={'chat_id': CHAT_ID, 'text': message, 'parse_mode': 'Markdown'})

if __name__ == "__main__":
    # Ở đây bạn có thể tùy chỉnh logic: 
    # Ví dụ: Sáng thứ 2,4,6 gửi Science, thứ 3,5,7 gửi Art
    # Hoặc gửi cả hai:
    sci_msg = get_science_news()
    send_telegram(sci_msg)
    
    art_msg, art_img = get_art_news()
    send_telegram(art_msg, art_img)