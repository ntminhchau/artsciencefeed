import requests
import feedparser
import random
import os
import time

TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

def get_science_news(limit=3):
    # Mở rộng danh sách từ khóa để tin tức đa dạng hơn
    # Bao gồm: Vũ trụ, Vật lý, Sinh học, AI, Khảo cổ, Môi trường
    keywords = "discovery+OR+breakthrough+AND+(space+OR+physics+OR+biology+OR+AI+OR+archaeology+OR+climate)"
    url = f"https://news.google.com/rss/search?q={keywords}+when:7d&hl=en-US&gl=US&ceid=US:en"
    feed = feedparser.parse(url)
    
    results = []
    # Loại bỏ các tin có tiêu đề chứa từ khóa nhàm chán
    boring_words = ["fund", "proposals", "meeting", "faculty", "grant", "workshop", "webinar", "course"]
    
    # Lấy danh sách tin hợp lệ
    valid_entries = []
    for entry in feed.entries:
        if not any(word in entry.title.lower() for word in boring_words):
            valid_entries.append(entry)
            
    # Lấy ngẫu nhiên 'limit' tin từ danh sách tin hợp lệ để đa dạng chủ đề mỗi ngày
    selected_entries = random.sample(valid_entries, k=min(limit, len(valid_entries)))
    
    for entry in selected_entries:
        # Tạo tin nhắn kiểu HTML với link "Xem chi tiết tại đây"
        short_msg = f"🔬 <b>KHÁM PHÁ KHOA HỌC</b>\n📌 {entry.title}\n👉 <a href='{entry.link}'>Xem chi tiết tại đây</a>"
        results.append(short_msg)
        
    return results

def get_art_news(limit=3):
    results = []
    try:
        # Lấy danh sách tác phẩm từ Art Institute of Chicago
        response = requests.get("https://api.artic.edu/api/v1/artworks?limit=100", timeout=25).json()
        # Lọc các tác phẩm có ảnh
        art_list = [item for item in response['data'] if item.get('image_id')]
        
        # Lấy ngẫu nhiên 'limit' tác phẩm khác nhau
        selected_art = random.sample(art_list, k=min(limit, len(art_list)))
        
        for artwork in selected_art:
            title = artwork.get('title', 'Tác phẩm vô danh')
            artist = artwork.get('artist_display', 'Nghệ sĩ ẩn danh')
            # Lấy thêm thông tin chi tiết
            date = artwork.get('date_display', 'Không rõ năm sáng tác')
            medium = artwork.get('medium_display', 'Không rõ chất liệu')
            
            image_id = artwork['image_id']
            img_url = f"https://www.artic.edu/iiif/2/{image_id}/full/843,/0/default.jpg"
            
            # Tạo chú thích HTML chi tiết
            caption = f"🎨 <b>NGHỆ THUẬT MỖI NGÀY</b>\n🖼 <b>{title}</b>\n👨‍🎨 {artist}\n📅 <b>Năm:</b> {date}\n⚒ <b>Chất liệu:</b> {medium}"
            results.append((caption, img_url))
    except Exception as e:
        print(f"Lỗi Art: {e}")
    return results

def send_telegram(message, image=None):
    # Dùng parse_mode='HTML' để tin nhắn gọn gàng
    base_url = f"https://api.telegram.org/bot{TOKEN}/"
    try:
        if image:
            # Gửi link ảnh trực tiếp
            data = {'chat_id': CHAT_ID, 'caption': message, 'parse_mode': 'HTML'}
            params = {'photo': image}
            requests.get(base_url + "sendPhoto", params={**data, **params}, timeout=35)
        else:
            data = {'chat_id': CHAT_ID, 'text': message, 'parse_mode': 'HTML', 'disable_web_page_preview': False}
            requests.post(base_url + "sendMessage", data=data, timeout=35)
    except Exception as e:
        print(f"Lỗi gửi tin: {e}")

if __name__ == "__main__":
    # Gửi 3 tin Khoa học (Đa dạng chủ đề hơn)
    sci_news = get_science_news(limit=3)
    for msg in sci_news:
        send_telegram(msg)
        time.sleep(2) # Nghỉ lâu hơn xíu để Telegram không chặn

    # Gửi 3 tin Nghệ thuật (Chi tiết hơn)
    art_news = get_art_news(limit=3)
    for caption, img in art_news:
        send_telegram(caption, img)
        time.sleep(2)
