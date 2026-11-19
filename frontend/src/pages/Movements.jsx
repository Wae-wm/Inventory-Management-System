import { useCallback, useEffect, useState } from "react";
import { api } from "../api.js";
import { dateTime, num } from "../format.js";

const PAGE = 50;
const TYPE = {
  IN: { label: "รับเข้า", cls: "badge-green" },
  OUT: { label: "เบิกออก", cls: "badge-red" },
  ADJUSTMENT: { label: "ปรับยอด", cls: "badge-amber" },
};

// IN เป็น +, OUT เป็น − ส่วน ADJUSTMENT ระบบเก็บเครื่องหมายมาแล้ว
function signedQty(m) {
  if (m.movement_type === "OUT") return `−${num(m.quantity)}`;
  return m.quantity > 0 ? `+${num(m.quantity)}` : `−${num(Math.abs(m.quantity))}`;
}

export default function Movements() {
  const [rows, setRows] = useState([]);
  const [products, setProducts] = useState([]);
  const [warehouses, setWarehouses] = useState([]);
  const [filters, setFilters] = useState({ product_id: "", warehouse_id: "", movement_type: "", date_from: "", date_to: "" });
  const [hasMore, setHasMore] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  const fetchPage = useCallback(
    async (skip) => {
      const params = new URLSearchParams({ limit: String(PAGE), skip: String(skip) });
      Object.entries(filters).forEach(([k, v]) => v && params.set(k, v));
      const data = await api(`/stock/movements?${params}`);
      setHasMore(data.length === PAGE);
      return data;
    },
    [filters]
  );

  useEffect(() => {
    api("/products?limit=200&include_inactive=true").then(setProducts).catch(() => {});
    api("/warehouses?limit=200&include_inactive=true").then(setWarehouses).catch(() => {});
  }, []);

  useEffect(() => {
    setLoading(true);
    fetchPage(0)
      .then((d) => {
        setRows(d);
        setError("");
      })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [fetchPage]);

  async function loadMore() {
    try {
      const more = await fetchPage(rows.length);
      setRows([...rows, ...more]);
    } catch (e) {
      setError(e.message);
    }
  }

  const set = (k) => (e) => setFilters({ ...filters, [k]: e.target.value });

  return (
    <>
      <h2>ประวัติการเคลื่อนไหว</h2>

      <div className="toolbar">
        <select value={filters.product_id} onChange={set("product_id")}>
          <option value="">ทุกสินค้า</option>
          {products.map((p) => (
            <option key={p.product_id} value={p.product_id}>
              {p.sku} — {p.product_name}
            </option>
          ))}
        </select>
        <select value={filters.warehouse_id} onChange={set("warehouse_id")}>
          <option value="">ทุกคลัง</option>
          {warehouses.map((w) => (
            <option key={w.warehouse_id} value={w.warehouse_id}>
              {w.warehouse_code}
            </option>
          ))}
        </select>
        <select value={filters.movement_type} onChange={set("movement_type")}>
          <option value="">ทุกประเภท</option>
          {Object.entries(TYPE).map(([k, v]) => (
            <option key={k} value={k}>
              {v.label}
            </option>
          ))}
        </select>
        <label className="inline-check">
          ตั้งแต่
          <input type="date" value={filters.date_from} onChange={set("date_from")} />
        </label>
        <label className="inline-check">
          ถึง
          <input type="date" value={filters.date_to} onChange={set("date_to")} />
        </label>
      </div>

      {error && <p className="error">{error}</p>}

      <div className="card table-wrap">
        <table>
          <thead>
            <tr>
              <th>เวลา</th>
              <th>ประเภท</th>
              <th>สินค้า</th>
              <th>คลัง</th>
              <th className="num">จำนวน</th>
              <th>ผู้ทำรายการ</th>
              <th>อ้างอิง</th>
              <th>หมายเหตุ</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((m) => (
              <tr key={m.movement_id}>
                <td>{dateTime(m.created_at)}</td>
                <td>
                  <span className={`badge ${TYPE[m.movement_type].cls}`}>{TYPE[m.movement_type].label}</span>
                </td>
                <td>
                  {m.product_sku} — {m.product_name}
                </td>
                <td>{m.warehouse_code}</td>
                <td className="num">{signedQty(m)}</td>
                <td>{m.user_full_name}</td>
                <td>{m.reference_no ?? "-"}</td>
                <td>{m.note ?? "-"}</td>
              </tr>
            ))}
            {!loading && rows.length === 0 && (
              <tr>
                <td colSpan={8} className="muted empty">
                  ไม่พบรายการ
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {hasMore && (
        <div className="more">
          <button className="btn btn-secondary" onClick={loadMore}>
            โหลดเพิ่ม
          </button>
        </div>
      )}
    </>
  );
}
