import { useEffect, useState } from "react";
import { api } from "../api.js";

const money = (v) => Number(v).toLocaleString("th-TH", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
const num = (v) => Number(v).toLocaleString("th-TH");

function Stat({ label, value, warn }) {
  return (
    <div className={`card stat ${warn ? "stat-warn" : ""}`}>
      <div className="stat-label">{label}</div>
      <div className="stat-value">{value}</div>
    </div>
  );
}

export default function Dashboard() {
  const [summary, setSummary] = useState(null);
  const [low, setLow] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    Promise.all([api("/dashboard/summary"), api("/stock/low-stock")])
      .then(([s, l]) => {
        setSummary(s);
        setLow(l);
      })
      .catch((e) => setError(e.message));
  }, []);

  if (error) return <p className="error">{error}</p>;
  if (!summary) return <p className="muted">กำลังโหลด...</p>;

  return (
    <>
      <h2>ภาพรวมคลังสินค้า</h2>
      <div className="stats">
        <Stat label="สินค้าที่ใช้งานอยู่" value={num(summary.active_products)} />
        <Stat label="จำนวนชิ้นรวมทุกคลัง" value={num(summary.total_units)} />
        <Stat label="มูลค่าสต็อก (บาท)" value={money(summary.total_stock_value)} />
        <Stat label="เคลื่อนไหว 7 วันล่าสุด" value={num(summary.movements_last_7_days)} />
        <Stat label="สินค้าใกล้หมด" value={num(summary.low_stock_count)} warn={summary.low_stock_count > 0} />
      </div>

      <h3>สินค้าใกล้หมด</h3>
      {low.length === 0 ? (
        <p className="muted">ไม่มีสินค้าที่ต่ำกว่าจุดสั่งซื้อ</p>
      ) : (
        <div className="card table-wrap">
          <table>
            <thead>
              <tr>
                <th>SKU</th>
                <th>ชื่อสินค้า</th>
                <th className="num">คงเหลือรวม</th>
                <th className="num">จุดสั่งซื้อ</th>
              </tr>
            </thead>
            <tbody>
              {low.map((p) => (
                <tr key={p.product_id}>
                  <td>{p.sku}</td>
                  <td>{p.product_name}</td>
                  <td className="num warn-text">{num(p.total_on_hand)}</td>
                  <td className="num">{num(p.reorder_level)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </>
  );
}
