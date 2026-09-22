import { Dashboard } from "./pages/Dashboard";
import { Products, Business } from "./pages/Merchant";
import { useEffect, useState } from "react";
import {
  Bell,
  LayoutDashboard,
  LogOut,
  MapPin,
  Menu,
  Package,
  ShoppingBag,
  Store,
  Truck,
  UserRound,
  Users,
  X,
} from "lucide-react";
import { api } from "./api";
import { State, useData } from "./components/ui";
import { Auth } from "./pages/Auth";
import { Addresses, Browse, CartPage } from "./pages/Customer";
import { Notifications, Orders, Profile } from "./pages/Common";
import type { Cart, Notice, Page, User } from "./types";
import "./style.css";
const roleName = {
  Customer: "حساب العميل",
  Merchant: "لوحة المتجر",
  Driver: "حساب السائق",
  Admin: "إدارة المنصة",
};
export default function App() {
  const [user, setUser] = useState<User | null>(null),
    [loading, setLoading] = useState(true),
    [sessionError, setSessionError] = useState(""),
    [path, setPath] = useState(location.hash.slice(2) || "browse"),
    [mobile, setMobile] = useState(false),
    [logoutError, setLogoutError] = useState("");
  const cart = useData<Cart>(user?.role === "Customer" ? "/cart" : null);
  const notices = useData<Page<Notice>>(
    user ? "/notifications?unread=true&page_size=1" : null,
    15000,
  );
  function navigate(value: string) {
    location.hash = "/" + value;
    setPath(value);
    setMobile(false);
  }
  useEffect(() => {
    const handler = () => setPath(location.hash.slice(2) || "browse");
    window.addEventListener("hashchange", handler);
    void api<User>("/auth/me")
      .then(setUser)
      .catch((e) => {
        if (e.status !== 401) setSessionError(e.message);
      })
      .finally(() => setLoading(false));
    return () => window.removeEventListener("hashchange", handler);
  }, []);
  useEffect(() => {
    if (user && user.role !== "Customer" && path === "browse")
      navigate("dashboard");
  }, [user, path]);
  const nav =
    user?.role === "Customer" || !user
      ? [
          ["browse", "اكتشف المتاجر", Store],
          ["cart", "سلة المشتريات", ShoppingBag],
          ["orders", "طلباتي", Package],
          ["addresses", "عناويني", MapPin],
        ]
      : user.role === "Merchant"
        ? [
            ["dashboard", "نظرة عامة", LayoutDashboard],
            ["orders", "الطلبات", Package],
            ["products", "إدارة المنتجات", ShoppingBag],
            ["business", "إعدادات المتجر", Store],
          ]
        : user.role === "Driver"
          ? [
              ["dashboard", "نظرة عامة", LayoutDashboard],
              ["orders", "توصيلاتي", Truck],
            ]
          : [
              ["dashboard", "نظرة عامة", LayoutDashboard],
              ["orders", "الطلبات", Package],
              ["users", "إدارة الحسابات", Users],
              ["drivers", "السائقون والمواقع", MapPin],
              ["products", "المنتجات والتصنيفات", ShoppingBag],
              ["places", "المدن والمناطق", Store],
            ];
  if (loading)
    return (
      <State loading>
        <></>
      </State>
    );
  if (path === "login" || path === "register")
    return (
      <Auth
        register={path === "register"}
        onUser={setUser}
        navigate={navigate}
      />
    );
  if (!user && path !== "browse")
    return <Auth register={false} onUser={setUser} navigate={navigate} />;
  const tab = path.split("/")[0];
  let content;
  if (!user || user.role === "Customer") {
    if (tab === "browse")
      content = (
        <Browse
          user={user}
          navigate={navigate}
          onCart={() => void cart.reload()}
        />
      );
    else if (tab === "cart")
      content = (
        <CartPage navigate={navigate} onCart={() => void cart.reload()} />
      );
    else if (tab === "addresses") content = <Addresses />;
  }
  if (user && tab === "orders")
    content = (
      <Orders
        user={user}
        navigate={navigate}
        identity={path.split("/")[1] ? Number(path.split("/")[1]) : undefined}
      />
    );
  if (user && tab === "notifications") content = <Notifications />;
  if (user && tab === "profile")
    content = <Profile user={user} onUser={setUser} />;
  if (user && user.role !== "Customer" && tab === "dashboard")
    content = <Dashboard user={user} navigate={navigate} />;
  if (
    user &&
    (user.role === "Merchant" || user.role === "Admin") &&
    tab === "products"
  )
    content = <Products user={user} />;
  if (user?.role === "Merchant" && tab === "business") content = <Business />;
  if (!content)
    content = (
      <div className="panel">
        <h1>نظرة عامة</h1>
        <p>انتقل إلى الطلبات لمتابعة وإدارة سير العمل.</p>
        <button className="primary" onClick={() => navigate("orders")}>
          عرض الطلبات
        </button>
      </div>
    );
  return (
    <div className="app">
      <aside className={"sidebar " + (mobile ? "mobile-open" : "")}>
        <a className="brand" href="#/browse">
          <div className="brand-mark">
            <Truck size={26} />
          </div>
          <div>
            <strong>
              وصلة<span> • </span>
            </strong>
            <small>أبو حماد أقرب</small>
          </div>
        </a>
        <button
          className="mobile-close icon"
          aria-label="إغلاق القائمة"
          onClick={() => setMobile(false)}
        >
          <X />
        </button>
        <div className="nav-caption">
          {user ? roleName[user.role] : "اكتشف بلدك"}
        </div>
        <nav>
          {nav.map(([route, label, Icon]) => {
            const I = Icon as typeof Store;
            return (
              <button
                key={route as string}
                className={tab === route ? "active" : ""}
                onClick={() => navigate(route as string)}
              >
                <I size={20} />
                <span>{label as string}</span>
                {route === "cart" && !!cart.data?.items.length && (
                  <b>{cart.data.items.reduce((s, i) => s + i.quantity, 0)}</b>
                )}
              </button>
            );
          })}
          {user && (
            <>
              <div className="nav-rule" />
              <button
                className={tab === "notifications" ? "active" : ""}
                onClick={() => navigate("notifications")}
              >
                <Bell size={20} />
                الإشعارات {!!notices.data?.total && <b>{notices.data.total}</b>}
              </button>
              <button
                className={tab === "profile" ? "active" : ""}
                onClick={() => navigate("profile")}
              >
                <UserRound size={20} />
                الملف الشخصي
              </button>
            </>
          )}
        </nav>
        <div className="sidebar-bottom">
          <div className="local-note">
            <MapPin size={20} />
            <strong>من هنا… ولينا</strong>
            <p>
              بنساعد متاجر بلدنا
              <br />
              توصل لناس أكتر.
            </p>
          </div>
          {user ? (
            <div className="account">
              <div className="avatar">{user.name[0]}</div>
              <div className="grow">
                <strong>{user.name}</strong>
                <small>{roleName[user.role]}</small>
              </div>
              <button
                className="icon"
                aria-label="تسجيل الخروج"
                onClick={async () => {
                  try {
                    await api("/auth/logout", "POST");
                    setUser(null);
                    navigate("login");
                  } catch (e) {
                    setLogoutError((e as Error).message);
                  }
                }}
              >
                <LogOut size={18} />
              </button>
            </div>
          ) : (
            <button className="primary" onClick={() => navigate("login")}>
              سجّل دخولك
            </button>
          )}
        </div>
      </aside>
      {mobile && (
        <button
          className="backdrop"
          aria-label="إغلاق القائمة"
          onClick={() => setMobile(false)}
        />
      )}
      <div className="main-wrap">
        <header className="topbar">
          <button
            className="mobile-menu icon"
            aria-label="فتح القائمة"
            onClick={() => setMobile(true)}
          >
            <Menu />
          </button>
          <span>
            <MapPin size={17} /> التوصيل إلى <strong>أبو حماد، الشرقية</strong>
          </span>
          <div>
            {user ? (
              <>
                <button
                  className="icon notification-bell"
                  aria-label="الإشعارات"
                  onClick={() => navigate("notifications")}
                >
                  <Bell size={20} />
                  {!!notices.data?.total && <i />}
                </button>
                <button
                  className="avatar"
                  aria-label="حسابي"
                  onClick={() => navigate("profile")}
                >
                  {user.name[0]}
                </button>
              </>
            ) : (
              <button onClick={() => navigate("login")}>
                تسجيل الدخول <UserRound size={16} />
              </button>
            )}
          </div>
        </header>
        <main>
          {(sessionError || logoutError) && (
            <div className="error" role="alert">
              {sessionError || logoutError}
              <button onClick={() => location.reload()}>إعادة المحاولة</button>
            </div>
          )}
          {content}
        </main>
        <footer>
          <strong>وصلة — أبو حماد</strong>
          <span>متاجر محلية. توصيل قريب. دفع عند الاستلام.</span>
        </footer>
      </div>
    </div>
  );
}
