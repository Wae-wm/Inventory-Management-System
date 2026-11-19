import { NavLink, Outlet } from "react-router-dom";
import { useAuth } from "../auth.jsx";

export default function Layout() {
  const { user, logout } = useAuth();
  return (
    <div className="app">
      <aside className="sidebar">
        <h1 className="brand">Inventory</h1>
        <nav>
          <NavLink to="/" end>
            Dashboard
          </NavLink>
          <NavLink to="/products">สินค้า</NavLink>
          <NavLink to="/stock">รับเข้า / เบิกออก</NavLink>
          <NavLink to="/movements">ประวัติการเคลื่อนไหว</NavLink>
        </nav>
        <div className="sidebar-footer">
          <div className="user-name">{user.full_name}</div>
          <div className="user-role">{user.role}</div>
          <button className="btn btn-ghost" onClick={logout}>
            ออกจากระบบ
          </button>
        </div>
      </aside>
      <main className="content">
        <Outlet />
      </main>
    </div>
  );
}
