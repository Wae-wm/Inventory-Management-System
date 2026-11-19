import { useCallback, useEffect, useState } from "react";
import { api } from "../api.js";
import { useAuth } from "../auth.jsx";
import Modal from "../components/Modal.jsx";
import { money, num } from "../format.js";

const EMPTY = {
  sku: "",
  product_name: "",
  category_id: "",
  unit: "piece",
  cost_price: "0",
  selling_price: "0",
  reorder_level: "10",
  description: "",
};

function ProductForm({ product, categories, onSaved, onClose }) {
  const [form, setForm] = useState(
    product
      ? {
          sku: product.sku,
          product_name: product.product_name,
          category_id: String(product.category_id),
          unit: product.unit,
          cost_price: product.cost_price,
          selling_price: product.selling_price,
          reorder_level: String(product.reorder_level),
          description: product.description ?? "",
        }
      : EMPTY
  );
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const set = (k) => (e) => setForm({ ...form, [k]: e.target.value });

  async function submit(e) {
    e.preventDefault();
    setError("");
    setBusy(true);
    const body = {
      sku: form.sku.trim(),
      product_name: form.product_name.trim(),
      category_id: Number(form.category_id),
      unit: form.unit.trim(),
      cost_price: form.cost_price,
      selling_price: form.selling_price,
      reorder_level: Number(form.reorder_level),
      description: form.description.trim() || null,
    };
    try {
      if (product) await api(`/products/${product.product_id}`, { method: "PATCH", body });
      else await api("/products", { method: "POST", body });
      onSaved();
    } catch (err) {
      setError(err.message);
      setBusy(false);
    }
  }

  return (
    <Modal title={product ? "แก้ไขสินค้า" : "เพิ่มสินค้า"} onClose={onClose}>
      <form onSubmit={submit} className="form-grid">
        <label>
          SKU
          <input value={form.sku} onChange={set("sku")} maxLength={50} required />
        </label>
        <label>
          ชื่อสินค้า
          <input value={form.product_name} onChange={set("product_name")} maxLength={150} required />
        </label>
        <label>
          หมวดหมู่
          <select value={form.category_id} onChange={set("category_id")} required>
            <option value="">เลือกหมวดหมู่</option>
            {categories.map((c) => (
              <option key={c.category_id} value={c.category_id}>
                {c.category_name}
              </option>
            ))}
          </select>
        </label>
        <label>
          หน่วยนับ
          <input value={form.unit} onChange={set("unit")} maxLength={30} required />
        </label>
        <label>
          ราคาทุน (บาท)
          <input type="number" min="0" step="0.01" value={form.cost_price} onChange={set("cost_price")} required />
        </label>
        <label>
          ราคาขาย (บาท)
          <input type="number" min="0" step="0.01" value={form.selling_price} onChange={set("selling_price")} required />
        </label>
        <label>
          จุดสั่งซื้อ (เตือนเมื่อเหลือไม่เกินค่านี้)
          <input type="number" min="0" step="1" value={form.reorder_level} onChange={set("reorder_level")} required />
        </label>
        <label className="span-2">
          รายละเอียด
          <textarea rows={2} value={form.description} onChange={set("description")} />
        </label>
        {error && <p className="error span-2">{error}</p>}
        <div className="form-actions span-2">
          <button type="button" className="btn btn-secondary" onClick={onClose}>
            ยกเลิก
          </button>
          <button className="btn" disabled={busy}>
            {busy ? "กำลังบันทึก..." : "บันทึก"}
          </button>
        </div>
      </form>
    </Modal>
  );
}

export default function Products() {
  const { user } = useAuth();
  const isAdmin = user.role === "ADMIN";
  const [products, setProducts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [q, setQ] = useState("");
  const [categoryId, setCategoryId] = useState("");
  const [showInactive, setShowInactive] = useState(false);
  const [editing, setEditing] = useState(undefined); // undefined = ปิด, null = เพิ่มใหม่, object = แก้ไข
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    const params = new URLSearchParams({ limit: "200" });
    if (q.trim()) params.set("q", q.trim());
    if (categoryId) params.set("category_id", categoryId);
    if (showInactive) params.set("include_inactive", "true");
    try {
      setProducts(await api(`/products?${params}`));
      setError("");
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }, [q, categoryId, showInactive]);

  useEffect(() => {
    api("/categories?limit=200&include_inactive=true").then(setCategories).catch((e) => setError(e.message));
  }, []);

  // รอ 300 ms หลังหยุดพิมพ์ค่อยค้นหา เพื่อไม่ให้ยิงคำขอทุกตัวอักษร
  useEffect(() => {
    const t = setTimeout(load, 300);
    return () => clearTimeout(t);
  }, [load]);

  const categoryName = (id) => categories.find((c) => c.category_id === id)?.category_name ?? id;
  const activeCategories = categories.filter((c) => c.is_active);

  async function setActive(p, active) {
    if (!active && !window.confirm(`ปิดใช้งานสินค้า "${p.product_name}" ?`)) return;
    try {
      if (active) await api(`/products/${p.product_id}`, { method: "PATCH", body: { is_active: true } });
      else await api(`/products/${p.product_id}`, { method: "DELETE" });
      load();
    } catch (e) {
      setError(e.message);
    }
  }

  return (
    <>
      <div className="page-head">
        <h2>สินค้า</h2>
        <button className="btn" onClick={() => setEditing(null)}>
          + เพิ่มสินค้า
        </button>
      </div>

      <div className="toolbar">
        <input placeholder="ค้นหาชื่อสินค้าหรือ SKU" value={q} onChange={(e) => setQ(e.target.value)} />
        <select value={categoryId} onChange={(e) => setCategoryId(e.target.value)}>
          <option value="">ทุกหมวดหมู่</option>
          {categories.map((c) => (
            <option key={c.category_id} value={c.category_id}>
              {c.category_name}
            </option>
          ))}
        </select>
        <label className="inline-check">
          <input type="checkbox" checked={showInactive} onChange={(e) => setShowInactive(e.target.checked)} />
          แสดงที่ปิดใช้งาน
        </label>
      </div>

      {error && <p className="error">{error}</p>}

      <div className="card table-wrap">
        <table>
          <thead>
            <tr>
              <th>SKU</th>
              <th>ชื่อสินค้า</th>
              <th>หมวดหมู่</th>
              <th>หน่วย</th>
              <th className="num">ราคาทุน</th>
              <th className="num">ราคาขาย</th>
              <th className="num">จุดสั่งซื้อ</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {products.map((p) => (
              <tr key={p.product_id} className={p.is_active ? "" : "row-inactive"}>
                <td>{p.sku}</td>
                <td>
                  {p.product_name} {!p.is_active && <span className="badge badge-gray">ปิดใช้งาน</span>}
                </td>
                <td>{categoryName(p.category_id)}</td>
                <td>{p.unit}</td>
                <td className="num">{money(p.cost_price)}</td>
                <td className="num">{money(p.selling_price)}</td>
                <td className="num">{num(p.reorder_level)}</td>
                <td className="actions">
                  <button className="link-btn" onClick={() => setEditing(p)}>
                    แก้ไข
                  </button>
                  {isAdmin &&
                    (p.is_active ? (
                      <button className="link-btn link-danger" onClick={() => setActive(p, false)}>
                        ปิดใช้งาน
                      </button>
                    ) : (
                      <button className="link-btn" onClick={() => setActive(p, true)}>
                        เปิดใช้งาน
                      </button>
                    ))}
                </td>
              </tr>
            ))}
            {!loading && products.length === 0 && (
              <tr>
                <td colSpan={8} className="muted empty">
                  ไม่พบสินค้า
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {editing !== undefined && (
        <ProductForm
          product={editing}
          categories={activeCategories}
          onClose={() => setEditing(undefined)}
          onSaved={() => {
            setEditing(undefined);
            load();
          }}
        />
      )}
    </>
  );
}
