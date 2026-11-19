import { useCallback, useEffect, useState } from "react";
import { api } from "../api.js";
import { useAuth } from "../auth.jsx";
import { dateTime, num } from "../format.js";

const MODES = {
  in: { label: "รับเข้า", qtyLabel: "จำนวนที่รับเข้า" },
  out: { label: "เบิกออก", qtyLabel: "จำนวนที่เบิกออก" },
  adjust: { label: "ปรับยอด (Admin)", qtyLabel: "จำนวนที่นับได้จริง" },
};

export default function Stock() {
  const { user } = useAuth();
  const [mode, setMode] = useState("in");
  const [products, setProducts] = useState([]);
  const [warehouses, setWarehouses] = useState([]);
  const [balances, setBalances] = useState([]);
  const [productId, setProductId] = useState("");
  const [warehouseId, setWarehouseId] = useState("");
  const [qty, setQty] = useState("");
  const [refNo, setRefNo] = useState("");
  const [note, setNote] = useState("");
  const [current, setCurrent] = useState(null);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [busy, setBusy] = useState(false);

  const loadBalances = useCallback(
    () => api("/stock/balances?limit=200").then(setBalances).catch((e) => setError(e.message)),
    []
  );

  useEffect(() => {
    Promise.all([api("/products?limit=200"), api("/warehouses?limit=200")])
      .then(([p, w]) => {
        setProducts(p);
        setWarehouses(w);
      })
      .catch((e) => setError(e.message));
    loadBalances();
  }, [loadBalances]);

  // แสดงยอดคงเหลือปัจจุบันของสินค้าและคลังที่เลือก จะได้รู้ก่อนเบิกว่าเหลือเท่าไหร่
  useEffect(() => {
    setCurrent(null);
    if (!productId || !warehouseId) return;
    api(`/stock/balances?product_id=${productId}&warehouse_id=${warehouseId}`)
      .then((rows) => setCurrent(rows[0]?.quantity_on_hand ?? 0))
      .catch(() => setCurrent(null));
  }, [productId, warehouseId, balances]);

  async function submit(e) {
    e.preventDefault();
    setError("");
    setSuccess("");
    setBusy(true);
    const base = {
      product_id: Number(productId),
      warehouse_id: Number(warehouseId),
      reference_no: refNo.trim() || null,
    };
    const body =
      mode === "adjust"
        ? { ...base, counted_quantity: Number(qty), note: note.trim() }
        : { ...base, quantity: Number(qty), note: note.trim() || null };
    try {
      const res = await api(`/stock/${mode}`, { method: "POST", body });
      setSuccess(`บันทึก${MODES[mode].label.split(" ")[0]}สำเร็จ ยอดคงเหลือตอนนี้ ${num(res.quantity_on_hand)}`);
      setQty("");
      setNote("");
      setRefNo("");
      loadBalances();
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  const modes = Object.keys(MODES).filter((m) => m !== "adjust" || user.role === "ADMIN");

  return (
    <>
      <h2>รับเข้า / เบิกออก</h2>

      <div className="card panel">
        <div className="tabs">
          {modes.map((m) => (
            <button
              key={m}
              type="button"
              className={`tab ${mode === m ? "tab-active" : ""}`}
              onClick={() => {
                setMode(m);
                setError("");
                setSuccess("");
              }}
            >
              {MODES[m].label}
            </button>
          ))}
        </div>

        <form onSubmit={submit} className="form-grid">
          <label>
            สินค้า
            <select value={productId} onChange={(e) => setProductId(e.target.value)} required>
              <option value="">เลือกสินค้า</option>
              {products.map((p) => (
                <option key={p.product_id} value={p.product_id}>
                  {p.sku} — {p.product_name}
                </option>
              ))}
            </select>
          </label>
          <label>
            คลังสินค้า
            <select value={warehouseId} onChange={(e) => setWarehouseId(e.target.value)} required>
              <option value="">เลือกคลัง</option>
              {warehouses.map((w) => (
                <option key={w.warehouse_id} value={w.warehouse_id}>
                  {w.warehouse_code} — {w.warehouse_name}
                </option>
              ))}
            </select>
          </label>
          <label>
            {MODES[mode].qtyLabel}
            <input
              type="number"
              min={mode === "adjust" ? 0 : 1}
              step="1"
              value={qty}
              onChange={(e) => setQty(e.target.value)}
              required
            />
            {current !== null && <span className="hint">ยอดคงเหลือปัจจุบัน {num(current)}</span>}
          </label>
          <label>
            เลขที่อ้างอิง (ถ้ามี)
            <input value={refNo} onChange={(e) => setRefNo(e.target.value)} maxLength={50} />
          </label>
          <label className="span-2">
            {mode === "adjust" ? "เหตุผลที่ปรับยอด (จำเป็น)" : "หมายเหตุ (ถ้ามี)"}
            <input value={note} onChange={(e) => setNote(e.target.value)} required={mode === "adjust"} />
          </label>
          {error && <p className="error span-2">{error}</p>}
          {success && <p className="success span-2">{success}</p>}
          <div className="form-actions span-2">
            <button className="btn" disabled={busy}>
              {busy ? "กำลังบันทึก..." : `บันทึก${MODES[mode].label.split(" ")[0]}`}
            </button>
          </div>
        </form>
      </div>

      <h3>ยอดคงเหลือแยกตามคลัง</h3>
      <div className="card table-wrap">
        <table>
          <thead>
            <tr>
              <th>SKU</th>
              <th>ชื่อสินค้า</th>
              <th>คลัง</th>
              <th className="num">คงเหลือ</th>
              <th>อัปเดตล่าสุด</th>
            </tr>
          </thead>
          <tbody>
            {balances.map((b) => (
              <tr key={b.inventory_id}>
                <td>{b.sku}</td>
                <td>{b.product_name}</td>
                <td>{b.warehouse_code}</td>
                <td className="num">{num(b.quantity_on_hand)}</td>
                <td>{dateTime(b.updated_at)}</td>
              </tr>
            ))}
            {balances.length === 0 && (
              <tr>
                <td colSpan={5} className="muted empty">
                  ยังไม่มีสินค้าในคลัง
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </>
  );
}
