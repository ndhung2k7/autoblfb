# Facebook Comment Assistant

Tool quản lý và hỗ trợ bình luận Facebook Page tự động, tuân thủ chính sách của Facebook.

## Tính năng

- 🔌 Kết nối tối đa 10 Facebook Page qua Facebook Graph API
- 📝 Lấy danh sách bài viết và bình luận mới nhất
- 🤖 Tự động phản hồi thông minh với delay ngẫu nhiên (30-120s)
- 🎯 Phân tích nội dung bình luận (hỗ trợ AI)
- 📊 Dashboard quản lý trực quan
- ⚡ Rate limiting để tránh spam
- 📝 Log đầy đủ hoạt động

## Yêu cầu

- Python 3.11+
- MongoDB
- Facebook App với quyền quản lý Page
- (Tùy chọn) OpenAI API Key cho tính năng AI

## Cài đặt

### 1. Clone repository

```bash
git clone https://github.com/yourusername/facebook-comment-assistant.git
cd facebook-comment-assistant
