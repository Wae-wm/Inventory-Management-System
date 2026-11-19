// ตัวกลางเรียก Backend ทุกครั้ง: ใส่ token ให้เอง และแปลง error ให้อ่านง่าย
const TOKEN_KEY = "ims_token";

export const getToken = () => localStorage.getItem(TOKEN_KEY);
export const setToken = (token) => localStorage.setItem(TOKEN_KEY, token);
export const clearToken = () => localStorage.removeItem(TOKEN_KEY);

export class ApiError extends Error {
  constructor(message, status) {
    super(message);
    this.status = status;
  }
}

// FastAPI ส่ง detail มาเป็นข้อความ (เช่น 409) หรือรายการ (กรณี 422 ข้อมูลไม่ผ่านตรวจ)
function errorMessage(detail, status) {
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail) && detail.length > 0) {
    return detail.map((d) => `${(d.loc || []).slice(1).join(".")}: ${d.msg}`).join(", ");
  }
  return `เกิดข้อผิดพลาด (รหัส ${status})`;
}

export async function api(path, { method = "GET", body, form } = {}) {
  const headers = {};
  const token = getToken();
  if (token) headers.Authorization = `Bearer ${token}`;

  let payload;
  if (form) {
    headers["Content-Type"] = "application/x-www-form-urlencoded";
    payload = new URLSearchParams(form);
  } else if (body !== undefined) {
    headers["Content-Type"] = "application/json";
    payload = JSON.stringify(body);
  }

  let res;
  try {
    res = await fetch(`/api${path}`, { method, headers, body: payload });
  } catch {
    throw new ApiError("เชื่อมต่อเซิร์ฟเวอร์ไม่ได้ ตรวจสอบว่า Backend ทำงานอยู่", 0);
  }

  if (res.status === 204) return null;
  const data = await res.json().catch(() => null);
  if (!res.ok) {
    // token หมดอายุหรือไม่ถูกต้อง: แจ้งให้ AuthProvider พากลับไปหน้า Login
    if (res.status === 401 && token) window.dispatchEvent(new Event("auth-expired"));
    throw new ApiError(errorMessage(data?.detail, res.status), res.status);
  }
  return data;
}
