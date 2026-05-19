# XOGame

Trò chơi XO (Caro 9x9) tích hợp AI với các thuật toán **Minimax** và **Alpha-Beta Pruning**.

## Yêu cầu
- Python 3.10+

## Cài đặt

Clone project:

```bash
git clone https://github.com/taclna/23020703_23020662_23020661_23020651_CaroAI
cd 23020703_23020662_23020661_23020651_CaroAI
```

Cài thư viện cần thiết:

```bash
pip install -r requirements.txt
```

## Chạy chương trình

```bash
python main.py
```

## Cấu trúc thư mục

```bash
XOGame/
│── ai/            # Thuật toán AI
│── core/          # Logic trò chơi
│── ui/            # Giao diện
│── assets/        # Hình ảnh, tài nguyên
│── screenshots/   # Ảnh thực nghiệm
│── main.py        # File chạy chính
```

## Chức năng
- Chơi XO trên bàn cờ 9x9
- Chế độ Player vs AI
- Minimax / Alpha-Beta
- Đánh giá trạng thái bàn cờ
- Hỗ trợ nhiều độ sâu tìm kiếm