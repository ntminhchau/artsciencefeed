import requests
import feedparser
import random
import os

TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

def get_science_news():
    # Sử dụng Google News RSS cho chủ đề Science - Rất ổn định
    url = "https://news.google.com/rss/search?q=science+discovery+when:7d&hl=en-US&gl=US&ceid=US:en"
    feed = feedparser.parse(url)
    
    if len(feed.entries) > 0:
        # Lấy ngẫu nhiên 1 trong 5 tin hàng đầu
        entry = random.choice(feed.entries[:5])
        title = entry.title
        link = entry.link
        return f"🔬 **KHÁM PHÁ KHOA HỌC**\n\n📌 **Tiêu đề:** {title}\n\n🔗 Xem chi tiết: {link}"
    
    # Nếu Google News cũng lỗi, dùng ScienceDaily làm dự phòng
    backup_feed = feedparser.parse("https://www.sciencedaily.com/rss/top/science.xml")
    if len(backup_feed.entries) > 0:
        entry = random.choice(backup_feed.entries[:5])
        return f"🔬 **TIN KHOA HỌC (Dự phòng)**\n\n📌 {entry.title}\n\n🔗 {entry.link}"
        
    return "🔬 Hiện tại các trang tin đang bận, Bé Bi đợi lần tới nhé!"

def get_art_news():
    try:
        # Lấy từ Art Institute of Chicago
        response = requests.get("https://api.artic.edu/api/v1/artworks?limit=60", timeout=15).json()
        # Lọc các tác phẩm có ảnh và có thông tin nghệ sĩ
        art_list = [item for item in response['data'] if item.get('image_id') and item.get('artist_display')]
        artwork = random.choice(art_list)
        
        title = artwork.get('title', 'Tác phẩm vô danh')
        artist = artwork.get('artist_display', 'Nghệ sĩ ẩn danh')
        image_id = artwork['image_id']
        image_url = f"https://www.artic.edu/iiif/2/{image_id}/full/843,/0/default.jpg"
        
        return f"🎨 **NGHỆ THUẬT MỖI NGÀY**\n\n🖼 **Tác phẩm:** {title}\n👨‍🎨 **Nghệ sĩ:** {artist}", image_url
    except Exception as e:
        print(f"Lỗi lấy tin nghệ thuật: {e}")
        return "🎨 Hôm nay các bức tranh đang được bảo trì rồi!", None

def send_telegram(message, image=None):
    base_url = f"https://api.telegram.org/bot{TOKEN}/"
    try:
        if image:
            # Gửi ảnh kèm chú thích
            requests.post(base_url + "sendPhoto", data={'chat_id': CHAT_ID, 'caption': message, 'parse_mode': 'Markdown'}, files={'photo': requests.get(image).content}, timeout=30)
        else:
            # Gửi tin nhắn văn bản
            requests.post(base_url + "sendMessage", data={'chat_id': CHAT_ID, 'text': message, 'parse_mode': 'Markdown'}, timeout=30)
    except Exception as e:
        print(f"Lỗi gửi tin lên Telegram: {e}")

if __name__ == "__main__":
    # 1. Gửi tin khoa học
    sci_msg = get_science_news()
    send_telegram(sci_msg)
    
    # 2. Gửi tin nghệ thuật (kèm ảnh)
    art_msg, art_img = get_art_news()
    send_telegram(art_msg, art_img)
