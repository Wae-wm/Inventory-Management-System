import { Navigate, Outlet, Route, Routes } from "react-router-dom";
import { useAuth } from "./auth.jsx";
import Layout from "./components/Layout.jsx";
import Dashboard from "./pages/Dashboard.jsx";
import Login from "./pages/Login.jsx";
import Movements from "./pages/Movements.jsx";
import Products from "./pages/Products.jsx";
import Stock from "./pages/Stock.jsx";

// หน้าที่ต้องล็อกอินก่อนเท่านั้น ถ้ายังไม่ล็อกอินให้ไปหน้า Login
function RequireAuth() {
  const { user, loading } = useAuth();
  if (loading) return <p className="center-msg">กำลังโหลด...</p>;
  return user ? <Outlet /> : <Navigate to="/login" replace />;
}

export default function App() {
  const { user } = useAuth();
  return (
    <Routes>
      <Route path="/login" element={user ? <Navigate to="/" replace /> : <Login />} />
      <Route element={<RequireAuth />}>
        <Route element={<Layout />}>
          <Route index element={<Dashboard />} />
          <Route path="products" element={<Products />} />
          <Route path="stock" element={<Stock />} />
          <Route path="movements" element={<Movements />} />
        </Route>
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
