# AGENTS.md — LaptopStore (Odoo 17)

Hướng dẫn ngữ cảnh cho AI khi làm việc trong repo này. Dự án do một người học Odoo tự tay xây dựng theo phương pháp "làm để học". Mọi thứ đều chạy bằng Docker.

## Ngôn ngữ
- Trao đổi / giải thích bằng **tiếng Việt**.
- Code, tên file, comment giữ nguyên tiếng Anh theo chuẩn Odoo.

## Kiến trúc
- **Odoo 17 Community** chạy trong Docker (monolithic: backend + frontend + DB).
- Database: **PostgreSQL 16**, tên DB `laptopstore`.
- Module tùy chỉnh: `addons/laptop_store`.
- UI: view XML + QWeb + OWL (framework JS riêng của Odoo). KHÔNG dùng React/Vue.

## Cấu trúc module
```
addons/laptop_store/
├── __manifest__.py
├── models/
│   ├── __init__.py
│   ├── product_laptop.py   # laptop.product
│   ├── partner.py          # inherit res.partner (is_laptop_customer)
│   └── sale_order.py       # laptop.sale.order + laptop.sale.order.line
├── views/
│   ├── laptop_product_views.xml
│   └── laptop_sale_order_views.xml
├── reports/
│   ├── laptop_sale_order_email.xml  # mail.template
│   └── laptop_sale_order_report.xml
└── security/
    └── ir.model.access.csv
```

## Mô hình quan hệ
```
res.partner ─1─< customer_id <─n── laptop.sale.order
                                        │ line_ids (1 → n, qua order_id)
                                        ▼
laptop.product ─1─< product_id <─n── laptop.sale.order.line
```
- `laptop.sale.order`: name (Char, default "/"), customer_id (Many2one res.partner, required), date (Date, default today), state (Selection: draft/confirmed/done, default draft), line_ids (One2many), total (compute = tổng subtotal).
- `laptop.sale.order.line`: order_id (Many2one, ondelete cascade), product_id (Many2one laptop.product, required), qty (Integer default 1), unit_price (Float), subtotal (compute = qty × unit_price).
- `total` / `subtotal` là compute field → KHÔNG có cột trong DB.

## Lệnh thường dùng (chạy từ `C:\Work\Code\OdooLaptopStore`)
```powershell
# Khởi động / dừng
docker compose up -d
docker compose stop

# Cài module lần đầu (thay -i bằng -u để nâng cấp sau khi sửa)
docker compose exec odoo odoo -c /etc/odoo/odoo.conf -d laptopstore -u laptop_store --stop-after-init

# Restart server (bắt buộc khi sửa file Python model)
docker compose restart odoo

# Truy vấn DB (dùng service name "db")
docker compose exec db psql -U odoo -d laptopstore -c "SELECT ...;"

# Xem log lỗi
docker compose logs odoo --since 5m
```

## Web / ports
- Odoo: http://localhost:8069 (DB `laptopstore`)
- pgAdmin / psql: port 5433 (PostgreSQL internal 5432)
- MailHog (bưu điện giả để test email): web http://localhost:8025, SMTP cổng 1025

## QUY TẮC VÀNG (từng dính lỗi)
1. **Sửa file Python (model) ⇒ `docker compose restart odoo`.** Sửa file XML ⇒ chỉ cần `-u`.
2. Tên model dùng dấu chấm `laptop.sale.order`; bảng DB tự sinh gạch dưới `laptop_sale_order`.
3. Model / field mới **bắt buộc** có access rule trong `ir.model.access.csv`, nếu không Odoo từ chối mọi truy cập.
4. Mọi file XML trong module phải khai báo trong `data` của `__manifest__.py`.
5. **KHÔNG xóa thư mục `/var/lib/odoo/filestore/` trong container** — nó chứa file dữ liệu/asset; xóa sẽ làm mất CSS và ảnh đính kèm. Muốn xóa cache chỉ cần restart.
6. Odoo 17: muốn nút **In/Print** xuất hiện trên form thì report phải khai báo bằng `<record model="ir.actions.report">` và có field `binding_model_id` (cú pháp `<report>` thẳng không còn hợp lệ).
7. Odoo 17 dùng URL hash (`/web#action=...`), không có route `/odoo/action-...` (đó là Odoo 16).
8. Sau khi website không hiện menu/nút mới: đăng xuất + đóng trình duyệt hoặc hard refresh (Ctrl+Shift+R) để xóa cache web client.
9.  Odoo 17: `mail.template` không còn field `report_template` (bỏ từ Odoo 12). Dùng `report_template_ids` (Many2many ir.actions.report) + `eval="[(6, 0, [ref(...)])]"`.
10. Email template Odoo 17: subject / email_to dùng placeholder `{{ ... }}` (not `${ }` — cú pháp Odoo 8-11). `body_html` dùng QWeb `t-esc`.
11. Thuộc tính `invisible` trên button = "điều kiện để ẨN" (ngược nghĩa thường nghĩ). Nút hiện ở state X thì ghi `invisible="state != 'X'"`.
12. Chặn nghiệp vụ bằng `raise UserError("...")` (import từ odoo.exceptions); chuỗi có biến phải là f-string `f"..."`. Kiểm tra `state` trước khi trừ stock để tránh trừ 2 lần.

## Trạng thái hiện tại (đang giữa Bước 7)
- ✅ PDF report: form đơn bán có nút In, in PDF hoạt động.
- ✅ MailHog: 3 container chạy (db, odoo, mailhog).
- ⏳ Email: chưa cấu hình Outgoing Mail Server (trỏ `mailhog:1025`), chưa tạo email template, chưa có nút Gửi email.
- Việc kế tiếp: tạo email template QWeb + nút gửi mail trên `laptop.sale.order`.

## Lộ trình sắp tới (đã cam kết với người học)
1. Bước 7 còn lại: gửi email PDF qua MailHog.
2. Bước 8: quản lý kho (nhập/xuất) hoặc phân quyền — chưa chốt, hỏi người dùng.
3. Owl widget nâng cao (OWL).
4. CI/CD (GitHub Actions) + deploy VPS.

## Ghi chú khác
- Học viên là người mới Python/Odoo, thích giải thích từng dòng, không so sánh với Prisma/NestJS/React (đã yêu cầu dừng so sánh).
- Nói chuyện bằng tiếng Việt, kiên nhẫn, có ví dụ cụ thể.
- Học viên TỰ TAY làm mọi thay đổi; AI hướng dẫn từng bước, không tự sửa file thay người.
- Git: repo GitHub `TrongKhiemIT/OdooLaptopStrore` (tên bị typo, chưa đổi), branch `main`.