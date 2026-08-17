/** @odoo-module **/
import { IntegerField } from "@web/views/fields/integer/integer_field";
import { registry } from "@web/core/registry";

class StockBadge extends IntegerField {
  static template = "laptop_store.StockBadge";
  get getBadgeColor() {
    const qty = this.props.record.data.stock_qty;
    if (qty <= 0) {
      return "text-bg-danger";
    }
    if (qty <= 5) {
      return "text-bg-warning";
    }
    return "text-bg-success";
  }

  get getLabel() {
    const qty = this.props.record.data.stock_qty;
    if (qty <= 0) {
      return "Hết hàng!!!";
    }
    if (qty <= 5) {
      return "Sắp hết hàng!";
    }
    return "Còn hàng";
  }
}

export const laptopStockBadge = {
    component: StockBadge,
};

registry.category("fields").add("laptop_stock_badge", laptopStockBadge);
