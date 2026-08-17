/** @odoo-module **/

import { useService } from "@web/core/utils/hooks";
import { registry } from "@web/core/registry";
import { Component, useState, onMounted } from "@odoo/owl";

class LaptopDashboard extends Component {
  static template = "laptop_store.LaptopDashboard";

  setup() {
    this.orm = useService("orm");
    this.state = useState({ loading: true, stats: null });

    onMounted(() => this.loadData());
  }

  async loadData() {
    this.state.stats = await this.orm.call(
      "laptop.product",
      "get_dashboard_data",
      [],
    );
    this.state.loading = false;
  }

  formatMoney(value){
    return value.toLocaleString("vi-VN");
  }

  get cards() {
    if (!this.state.stats) {
      return [];
    }

    const s = this.state.stats;

    return [
      {
        label: "Số laptop",
        value: s.product_count,
      },
      {
        label: "Tồn kho (cái)",
        value: s.total_stock,
      },
      {
        label: "Giá trị kho (VNĐ)",
        value: this.formatMoney(s.stock_value),
      },
      {
        label: "Đã bán (cái)",
        value: s.qty_sold,
      },
      {
        label: "Số đơn đã chốt",
        value: s.order_count,
      },
      {
        label: "Doanh thu (VNĐ)",
        value: this.formatMoney(s.revenue),
      },
    ];
  }
}

registry.category("actions").add("laptop_store.Dashboard", LaptopDashboard);
