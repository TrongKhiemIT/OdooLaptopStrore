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
│   ├── product_laptop.py   # laptop.product (cost_price chỉ Quản lý thấy)
│   ├── partner.py          # inherit res.partner (is_laptop_customer)
│   ├── sale_order.py       # laptop.sale.order + laptop.sale.order.line
│   └── stock_receipt.py    # laptop.stock.receipt + laptop.stock.receipt.line
├── views/
│   ├── laptop_product_views.xml
│   ├── laptop_sale_order_views.xml
│   └── laptop_stock_receipt_views.xml
├── reports/
│   ├── laptop_sale_order_email.xml  # mail.template
│   └── laptop_sale_order_report.xml
└── security/
    ├── ir.model.access.csv          # ACL theo nhóm (10 dòng)
    └── laptop_security.xml          # res.groups + ir.module.category
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
- `laptop.stock.receipt`: name (Char, default "/"), date (Date, default today), state (Selection: draft/done, default draft), line_ids (One2many).
- `laptop.stock.receipt.line`: receipt_id (Many2one, ondelete cascade), product_id (Many2one laptop.product, required), qty (Integer default 1).
- `laptop.product`: thêm `cost_price` (Float, `groups="laptop_store.group_laptop_store_manager"` — chỉ Quản lý đọc/ghi).
- Nhập kho = cộng `stock_qty` (`action_confirm`), Hủy = trừ lại (`action_cancel`) — đối xứng với bán hàng.

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
13. File security XML (nhóm `res.groups`) phải khai báo TRƯỚC `ir.model.access.csv` trong `data` của manifest — CSV tham chiếu group.
14. Tạo group mới ⇒ user cũ "Access Error" là BÌNH THƯỜNG (đúng thiết kế): phải gán user vào group mới qua Settings → Users → Access Rights.
15. ACL mỗi model 1 dòng/group; cột `id` của CSV là XMLID PHẢI duy nhất. Quyền nhân viên thường `1,1,1,0` (không xóa), quản lý `1,1,1,1`.
16. Field `groups=` bảo vệ 2 tầng: model (ORM chặn đọc/ghi) + view (không hiển thị cho người khác).
17. Model mới (file Python) + view mới ⇒ cần CẢ `docker compose restart odoo` LẪN `-u laptop_store`.
18. OWL: template trong `static/src/xml` phải dùng `<t t-name="addon.ClassName">` làm CON TRỰC TIẾP của `<odoo>` (không bọc `<template>` — đó là cú pháp QWeb server). Tên t-name phải khớp CHÍNH XÁC chuỗi trong `static template` của class JS.
19. OWL widget field: đăng ký bằng OBJECT `{ component: X }` (không phải class trần): `registry.category("fields").add("ten_widget", { component: X })`. Import `IntegerField` từ `@web/views/fields/integer/integer_field`.
20. File JS/template phải khai trong `"assets": { "web.assets_backend": [...] }` của manifest. Lỗi giao diện trắng thường do asset compile fail — đọc `docker compose logs odoo` để thấy "Parsing asset bundle ... has failed".

## Trạng thái hiện tại (sau Bước 10)
- ✅ Bước 7: gửi email hóa đơn kèm PDF qua MailHog (template `{{ }}` + `report_template_ids`).
- ✅ Bước 8: quản lý kho — đơn bán Xác nhận trừ stock, Hủy cộng lại (button `invisible` + `UserError`).
- ✅ Bước 9: phiếu nhập kho — Xác nhận cộng stock, Hủy trừ lại (pattern lặp lại như Bước 8).
- ✅ Bước 10: phân quyền — 2 group (Nhân viên `1,1,1,0` / Quản lý `1,1,1,1`, quản lý kế thừa nhân viên), field `cost_price` chỉ Quản lý. Admin (nguyentrongkhiem010117@gmail.com) nằm cả 2 nhóm; có user test `nhanvien@test.com` chỉ nhóm Nhân viên.
- ✅ Bước 11: OWL widget `laptop_stock_badge` — badge màu theo `stock_qty` (đỏ 0 / vàng 1-5 / xanh >5), reactive đổi màu ngay khi sửa. Đăng ký `{component}` + `static template`.
- ✅ Bước 12: dashboard "Tổng quan" — client action (`ir.actions.client` + `tag`), `@api.model` method trả dict, JS gọi bằng `orm.call`, `onMounted` + `useState`, `t-foreach`/`t-key`, format tiền `toLocaleString("vi-VN")`.
- Việc kế tiếp: Bước 13 — CI/CD GitHub Actions.

## Lộ trình sắp tới (đã cam kết với người học)
1. CI/CD (GitHub Actions) — tự kiểm tra lỗi khi push.
2. Deploy VPS.
3. Nâng cao: record rules (ir.rule), trường `_check`, action server, ...

## Ghi chú khác
- Học viên là người mới Python/Odoo, thích giải thích từng dòng, không so sánh với Prisma/NestJS/React (đã yêu cầu dừng so sánh).
- Nói chuyện bằng tiếng Việt, kiên nhẫn, có ví dụ cụ thể.
- Học viên TỰ TAY làm mọi thay đổi; AI hướng dẫn từng bước, không tự sửa file thay người.
- Git: repo GitHub `TrongKhiemIT/OdooLaptopStrore` (tên bị typo, chưa đổi), branch `main`.