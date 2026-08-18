# Laptop Store — Odoo 17

Dự án học tập Odoo: module quản lý cửa hàng laptop chạy trên Docker, kèm CI tự động kiểm tra lỗi bằng GitHub Actions.

> Module: `addons/laptop_store` · Phiên bản Odoo: **17** · License: LGPL-3

## Tính năng

- **Danh mục laptop** — sản phẩm, đơn giá, giá vốn, tồn kho.
- **Đơn bán** — tạo đơn → xác nhận (trừ tồn kho) → hoàn thành → hủy (cộng lại tồn kho); gửi email PDF hóa đơn.
- **Phiếu nhập kho** — nhập hàng cộng tồn kho, hủy phiếu trừ lại.
- **Phân quyền** — 2 nhóm: **Nhân viên** (không xóa dữ liệu) và **Quản lý** (kế thừa nhân viên, xem được giá vốn).
- **Tổng quan** — dashboard OWL: doanh thu, số đơn, tồn kho, giá trị kho.
- **Badge tồn kho** — OWL widget đổi màu theo số lượng (đỏ 0 / vàng 1-5 / xanh >5).
- **CI/CD** — GitHub Actions tự cài module trên DB sạch để bắt lỗi mỗi khi push.

## Kiến trúc

```
laptop_store/
├── models/                  # Model Python
│   ├── product_laptop.py    # laptop.product (kèm API dashboard)
│   ├── sale_order.py        # laptop.sale.order + .line (kèm quản lý tồn kho)
│   ├── stock_receipt.py     # laptop.stock.receipt + .line (phiếu nhập kho)
│   └── partner.py           # inherit res.partner
├── views/                   # Giao diện XML
├── reports/                 # PDF hóa đơn + email template
├── security/                # Nhóm, ACL, record rules
├── static/src/              # OWL: JS + template (badge, dashboard)
└── __manifest__.py
```

## Chạy với Docker

Yêu cầu: Docker Desktop + extension **Docker Compose v2**.

```bash
# 1. Bật các container (db, odoo, mailhog)
docker compose up -d

# 2. Mở http://localhost:8069, tạo database rồi cài module "Laptop Store"

# 3. Mỗi lần sửa code:
docker compose exec odoo odoo -c /etc/odoo/odoo.conf -d <tên_db> -u laptop_store --stop-after-init
```

Quy tắc nhanh:

| Thay đổi | Lệnh |
|---|---|
| Sửa file `.py` | `docker compose restart odoo` |
| Sửa file XML | `-u laptop_store` |
| Thêm model/view MỚI | cả restart **lẫn** `-u` |

MailHog (email thật tạm): web **http://localhost:8025** · SMTP port **1025**.

## Phân quyền

| Quyền | ACL | Record rule |
|---|---|---|
| **Nhân viên** | đọc/ghi/tạo, **không xóa** | chỉ thấy dữ liệu của chính mình (theo rule) |
| **Quản lý** | đầy đủ + giá vốn (`cost_price`) | thấy tất cả |

## CI (GitHub Actions)

Mỗi lần push nhánh `main`, workflow `.github/workflows/ci.yml` chạy trên máy Ubuntu sạch:

1. `actions/checkout@v5` — tải code về.
2. `docker compose up -d` — dựng môi trường.
3. Chờ Odoo khởi động (curl port 8069).
4. `odoo -i laptop_store --stop-after-init` — cài module trên **DB mới** để bắt lỗi code.

> CI dùng `-i` (cài mới) vì DB luôn trống, không phải `-u` (upgrade) như máy nhà. `docker compose exec` thêm `-T` vì GitHub Actions không có TTY.

## Ghi chú học tập

- Dự án mang tính học tập, áp dụng dần: model → view → security → OWL → CI/CD.
- Xem `AGENTS.md` để biết quy tắc vàng đã đúc kết trong quá trình học.