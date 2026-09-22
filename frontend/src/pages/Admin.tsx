import { useState } from "react";
import { MapPin, Plus, Search, Truck } from "lucide-react";
import { api, date } from "../api";
import {
  Field,
  Form,
  Header,
  Modal,
  Pages,
  State,
  useAction,
  useData,
  val,
} from "../components/ui";
import type { Driver, Merchant, Named, Page, Role, User } from "../types";
const roles: Record<Role, string> = {
  Admin: "مدير",
  Merchant: "تاجر",
  Driver: "سائق",
  Customer: "عميل",
};
export function UsersPage({ current }: { current: User }) {
  const [page, setPage] = useState(1),
    [role, setRole] = useState(""),
    [q, setQ] = useState(""),
    [creating, setCreating] = useState(false);
  const users = useData<Page<User>>(
    `/admin/users?page=${page}&page_size=12&q=${encodeURIComponent(q)}${role ? "&role=" + role : ""}`,
  );
  const merchants = useData<Page<Merchant>>("/admin/merchants?page_size=100");
  const action = useAction(() => {
    void users.reload();
    void merchants.reload();
  });
  return (
    <>
      <Header
        eyebrow="إدارة المنصة"
        title="إدارة الحسابات"
        description="إنشاء حسابات السائقين والمتاجر، وتفعيل أو إيقاف الحسابات."
        action={
          <button className="primary" onClick={() => setCreating(true)}>
            <Plus size={18} />
            إنشاء حساب
          </button>
        }
      />
      <div className="filters">
        <label className="search">
          <Search size={18} />
          <input
            aria-label="البحث عن حساب"
            value={q}
            onChange={(e) => {
              setQ(e.target.value);
              setPage(1);
            }}
            placeholder="ابحث بالاسم…"
          />
        </label>
        <select
          aria-label="نوع الحساب"
          value={role}
          onChange={(e) => {
            setRole(e.target.value);
            setPage(1);
          }}
        >
          <option value="">كل الحسابات</option>
          {Object.entries(roles).map(([r, n]) => (
            <option key={r} value={r}>
              {n}
            </option>
          ))}
        </select>
      </div>
      {action.error && (
        <div role="alert" className="error">
          {action.error}
        </div>
      )}
      <State
        loading={users.loading}
        error={users.error}
        retry={users.reload}
        empty={!users.data?.items.length}
      >
        <div className="panel table-wrap">
          <table className="table">
            <thead>
              <tr>
                <th>الحساب</th>
                <th>الدور</th>
                <th>الحالة</th>
                <th>إدارة الحساب</th>
              </tr>
            </thead>
            <tbody>
              {users.data?.items.map((u) => (
                <tr key={u.id}>
                  <td>
                    <strong>{u.name}</strong>
                    <small dir="ltr">{u.email}</small>
                    <small dir="ltr">{u.phone}</small>
                  </td>
                  <td>{roles[u.role]}</td>
                  <td>
                    <span
                      className={
                        "badge " +
                        (u.is_active ? "status-Delivered" : "status-Rejected")
                      }
                    >
                      {u.is_active ? "نشط" : "موقوف"}
                    </span>
                  </td>
                  <td>
                    <div className="row-actions" style={{ margin: 0 }}>
                      <button
                        disabled={action.busy || u.id === current.id}
                        className={u.is_active ? "danger" : ""}
                        onClick={() =>
                          void action.run(() =>
                            api("/admin/users/" + u.id, "PATCH", {
                              is_active: !u.is_active,
                            }),
                          )
                        }
                      >
                        {u.is_active ? "إيقاف الحساب" : "تفعيل الحساب"}
                      </button>
                      {u.role === "Merchant" && (
                        <select
                          aria-label={"اعتماد متجر " + u.name}
                          disabled={action.busy}
                          value={
                            merchants.data?.items.find((m) => m.id === u.id)
                              ?.status ?? "Pending"
                          }
                          onChange={(e) =>
                            void action.run(() =>
                              api("/admin/merchants/" + u.id, "PATCH", {
                                status: e.target.value,
                              }),
                            )
                          }
                        >
                          <option value="Pending">بانتظار الاعتماد</option>
                          <option value="Approved">معتمد</option>
                          <option value="Rejected">مرفوض</option>
                        </select>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <Pages page={page} total={users.data?.total ?? 0} onChange={setPage} />
      </State>
      {creating && (
        <Modal title="إنشاء حساب جديد" onClose={() => setCreating(false)}>
          <CreateUser
            saved={() => {
              setCreating(false);
              void users.reload();
              void merchants.reload();
            }}
          />
        </Modal>
      )}
    </>
  );
}
function CreateUser({ saved }: { saved: () => void }) {
  const [role, setRole] = useState("Driver");
  return (
    <Form
      submit="إنشاء الحساب"
      onSubmit={async (data) => {
        await api("/admin/users", "POST", {
          name: val(data, "name"),
          email: val(data, "email"),
          phone: val(data, "phone"),
          password: val(data, "password"),
          role,
          ...(role === "Merchant"
            ? { business_name: val(data, "business_name") }
            : {}),
        });
        saved();
      }}
    >
      <Field label="نوع الحساب">
        <select value={role} onChange={(e) => setRole(e.target.value)}>
          <option value="Driver">سائق</option>
          <option value="Merchant">تاجر</option>
          <option value="Customer">عميل</option>
        </select>
      </Field>
      <Field label="الاسم">
        <input
          name="name"
          required
          minLength={2}
          maxLength={100}
          autoComplete="off"
        />
      </Field>
      {role === "Merchant" && (
        <Field label="اسم المتجر">
          <input name="business_name" required minLength={2} maxLength={150} />
        </Field>
      )}
      <Field label="البريد الإلكتروني">
        <input
          name="email"
          type="email"
          required
          dir="ltr"
          autoComplete="off"
        />
      </Field>
      <Field label="رقم الموبايل">
        <input
          name="phone"
          type="tel"
          required
          pattern="\+?[0-9]{10,15}"
          dir="ltr"
          autoComplete="off"
        />
      </Field>
      <Field label="كلمة المرور">
        <input
          name="password"
          type="password"
          required
          minLength={12}
          maxLength={128}
          autoComplete="new-password"
          dir="ltr"
        />
      </Field>
      <small>اختر كلمة مرور قوية وشاركها مع صاحب الحساب بطريقة آمنة.</small>
    </Form>
  );
}
export function Drivers() {
  const [page, setPage] = useState(1),
    [selected, setSelected] = useState<number | null>(null);
  const list = useData<Page<Driver>>(
    `/admin/drivers?page=${page}&page_size=12`,
    10000,
  );
  const driver = list.data?.items.find((d) => d.id === selected);
  const lat = Number(driver?.latitude),
    lng = Number(driver?.longitude);
  const hasLocation = driver?.latitude != null && driver?.longitude != null;
  const mapUrl = hasLocation
    ? `https://www.openstreetmap.org/export/embed.html?bbox=${lng - 0.008},${lat - 0.006},${lng + 0.008},${lat + 0.006}&layer=mapnik&marker=${lat},${lng}`
    : "";
  return (
    <>
      <Header
        eyebrow="للإدارة فقط"
        title="السائقون والمواقع"
        description="آخر موقع أرسله السائق. التحديث تلقائي كل 10 ثوانٍ، ووقت آخر إرسال ظاهر بوضوح."
      />
      <State
        loading={list.loading}
        error={list.error}
        retry={list.reload}
        empty={!list.data?.items.length}
      >
        <div className="dashboard-grid">
          <section className="panel">
            <h2>متابعة المواقع</h2>
            <p style={{ marginBottom: 15 }}>
              {driver ? driver.name : "اختار سائقًا لعرض آخر موقع أرسله."}
            </p>
            <div className="map">
              {hasLocation ? (
                <iframe
                  title={"آخر موقع للسائق " + driver?.name}
                  src={mapUrl}
                  referrerPolicy="no-referrer"
                />
              ) : (
                <>
                  <div className="map-grid" />
                  <div className="map-empty">
                    <MapPin size={40} />
                    <strong>
                      {driver
                        ? "السائق لم يرسل موقعه بعد"
                        : "اختار سائقًا من القائمة"}
                    </strong>
                  </div>
                </>
              )}
            </div>
            {hasLocation && (
              <div className="list-row">
                <MapPin size={20} />
                <div>
                  <strong>
                    آخر إرسال:{" "}
                    {driver?.location_updated_at
                      ? date(driver.location_updated_at)
                      : "غير معروف"}
                  </strong>
                  <a
                    href={`https://www.openstreetmap.org/?mlat=${lat}&mlon=${lng}#map=16/${lat}/${lng}`}
                    target="_blank"
                    rel="noreferrer"
                  >
                    فتح الخريطة في نافذة جديدة
                  </a>
                  <small>الخريطة تتطلب اتصالًا بخدمة OpenStreetMap.</small>
                  <small dir="ltr">
                    {driver?.latitude}, {driver?.longitude}
                  </small>
                  <small>
                    هذه البيانات لا تظهر للعملاء أو التجار أو السائقين الآخرين.
                  </small>
                </div>
              </div>
            )}
          </section>
          <section className="panel">
            <h2>
              السائقون <span className="count">{list.data?.total ?? 0}</span>
            </h2>
            <div className="scroll-list">
              {list.data?.items.map((d) => (
                <div className="list-row" key={d.id}>
                  <div className="item-avatar">
                    <Truck size={18} />
                  </div>
                  <div className="grow">
                    <strong>{d.name}</strong>
                    <small>
                      <span
                        className={
                          "status-dot " +
                          (d.is_available && d.is_active ? "on" : "")
                        }
                      />
                      {!d.is_active
                        ? "الحساب موقوف"
                        : d.busy
                          ? "في توصيلة"
                          : d.is_available
                            ? "متاح"
                            : "غير متاح"}
                    </small>
                    <small>
                      {d.last_seen
                        ? "آخر نشاط " + date(d.last_seen)
                        : "لم يتصل بعد"}
                    </small>
                  </div>
                  <button onClick={() => setSelected(d.id)}>عرض الموقع</button>
                </div>
              ))}
            </div>
            <Pages
              page={page}
              total={list.data?.total ?? 0}
              onChange={setPage}
            />
          </section>
        </div>
      </State>
    </>
  );
}
export function Places() {
  const cities = useData<Page<Named>>("/cities?page_size=100"),
    areas = useData<Page<Named>>("/areas?page_size=100");
  const [creating, setCreating] = useState<"city" | "area" | null>(null);
  return (
    <>
      <Header
        eyebrow="بيانات التوصيل"
        title="المدن والمناطق"
        description="حدد المدن والمناطق التي تظهر عند إضافة عنوان التوصيل."
      />
      <div className="dashboard-grid">
        <section className="panel">
          <div className="section-heading" style={{ marginTop: 0 }}>
            <h2>المدن</h2>
            <button onClick={() => setCreating("city")}>
              <Plus size={16} />
              إضافة مدينة
            </button>
          </div>
          <State
            loading={cities.loading}
            error={cities.error}
            retry={cities.reload}
            empty={!cities.data?.items.length}
          >
            {cities.data?.items.map((c) => (
              <div className="list-row" key={c.id}>
                <MapPin size={18} />
                <strong>{c.name}</strong>
              </div>
            ))}
          </State>
        </section>
        <section className="panel">
          <div className="section-heading" style={{ marginTop: 0 }}>
            <h2>المناطق</h2>
            <button onClick={() => setCreating("area")}>
              <Plus size={16} />
              إضافة منطقة
            </button>
          </div>
          <State
            loading={areas.loading}
            error={areas.error}
            retry={areas.reload}
            empty={!areas.data?.items.length}
          >
            {areas.data?.items.map((a) => (
              <div className="list-row" key={a.id}>
                <div className="grow">
                  <strong>{a.name}</strong>
                  <small>
                    {cities.data?.items.find((c) => c.id === a.city_id)?.name}
                  </small>
                </div>
              </div>
            ))}
          </State>
        </section>
      </div>
      {creating && (
        <Modal
          title={creating === "city" ? "مدينة جديدة" : "منطقة جديدة"}
          onClose={() => setCreating(null)}
        >
          <Form
            onSubmit={async (data) => {
              await api(creating === "city" ? "/cities" : "/areas", "POST", {
                name: val(data, "name"),
                ...(creating === "area"
                  ? { city_id: Number(val(data, "city")) }
                  : {}),
              });
              setCreating(null);
              void cities.reload();
              void areas.reload();
            }}
          >
            {creating === "area" && (
              <Field label="المدينة">
                <select name="city" required defaultValue="">
                  <option value="" disabled>
                    اختر مدينة
                  </option>
                  {cities.data?.items.map((c) => (
                    <option key={c.id} value={c.id}>
                      {c.name}
                    </option>
                  ))}
                </select>
              </Field>
            )}
            <Field label="الاسم">
              <input name="name" required minLength={2} maxLength={100} />
            </Field>
          </Form>
        </Modal>
      )}
    </>
  );
}
