import requests
import feedparser
import random
import os

TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

def get_science_news():
    # Sử dụng link RSS dự phòng của Phys.org
    feed = feedparser.parse("https://phys.org/rss-feeds/top-news/")
    
    # Kiểm tra nếu có tin mới lấy, không thì báo lỗi nhẹ nhàng
    if len(feed.entries) > 0:
        entry = random.choice(feed.entries[:10])
        return f"🔬 **KHOA HỌC HÔM NAY**\n\nTiêu đề: {entry.title}\nLink: {entry.link}"
    return "🔬 Hiện tại không lấy được tin khoa học mới, Bé Bi đợi xíu nhé!"

def get_art_news():
    try:
        # Lấy từ danh sách 100 tác phẩm mới nhất
        response = requests.get("https://api.artic.edu/api/v1/artworks?limit=50", timeout=10).json()
        art_list = [item for item in response['data'] if item['image_id']]
        artwork = random.choice(art_list)
        
        title = artwork.get('title', 'Không rõ tiêu đề')
        artist = artwork.get('artist_display', 'Ẩn danh')
        image_id = artwork['image_id']
        image_url = f"https://www.artic.edu/iiif/2/{image_id}/full/843,/0/default.jpg"
        
        return f"🎨 **NGHỆ THUẬT MỖI NGÀY**\n\nTác phẩm: {title}\nNghệ sĩ: {artist}", image_url
    except Exception:
        return "🎨 Hôm nay bảo tàng nghỉ ngơi một chút rồi!", None

def send_telegram(message, image=None):
    base_url = f"https://api.telegram.org/bot{TOKEN}/"
    try:
        if image:
            requests.post(base_url + "sendPhoto", data={'chat_id': CHAT_ID, 'caption': message, 'parse_mode': 'Markdown'}, files={'photo': requests.get(image).content}, timeout=20)
        else:
            requests.post(base_url + "sendMessage", data={'chat_id': CHAT_ID, 'text': message, 'parse_mode': 'Markdown'}, timeout=20)
    except Exception as e:
        print(f"Lỗi gửi tin: {e}")

if __name__ == "__main__":
    # Gửi tin khoa học
    sci_msg = get_science_news()
    send_telegram(sci_msg)
    
    # Gửi tin nghệ thuật
    art_msg, art_img = get_art_news()
    send_telegram(art_msg, art_img)
