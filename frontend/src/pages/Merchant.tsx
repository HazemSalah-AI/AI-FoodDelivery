import { useState } from "react";
import { Package, Plus, Search, Store } from "lucide-react";
import { api, money } from "../api";
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
import type { Category, Merchant, Page, Product, User } from "../types";

export function Products({ user }: { user: User }) {
  const [page, setPage] = useState(1),
    [q, setQ] = useState(""),
    [editing, setEditing] = useState<Product | null | undefined>(),
    [category, setCategory] = useState<Category | null | undefined>();
  const products = useData<Page<Product>>(
    `/products?managed=true&page=${page}&page_size=12&q=${encodeURIComponent(q)}`,
  );
  const categories = useData<Page<Category>>(
    "/categories?page_size=100" +
      (user.role === "Merchant" ? "&merchant_id=" + user.id : ""),
  );
  const merchants = useData<Page<Merchant>>(
    user.role === "Admin" ? "/admin/merchants?page_size=100" : null,
  );
  const action = useAction(() => void products.reload());
  return (
    <>
      <Header
        eyebrow="كتالوج المتجر"
        title="المنتجات والتصنيفات"
        description="حدّث الأسعار والمخزون والتوفر. السعر النهائي يُحسب عند تأكيد الطلب."
        action={
          <button className="primary" onClick={() => setEditing(null)}>
            <Plus size={18} />
            إضافة منتج
          </button>
        }
      />
      <div className="panel" style={{ marginBottom: 22 }}>
        <div className="section-heading" style={{ margin: 0 }}>
          <h3>التصنيفات</h3>
          <button onClick={() => setCategory(null)}>
            <Plus size={15} />
            تصنيف جديد
          </button>
        </div>
        <div className="chips">
          {categories.data?.items.map((c) => (
            <button
              key={c.id}
              onClick={() => setCategory(c)}
              title="تعديل التصنيف"
            >
              {c.name}
            </button>
          ))}
        </div>
        {categories.error && (
          <p role="alert" className="error">
            {categories.error}
          </p>
        )}
      </div>
      <div className="filters">
        <label className="search">
          <Search size={18} />
          <input
            aria-label="البحث في المنتجات"
            value={q}
            onChange={(e) => {
              setQ(e.target.value);
              setPage(1);
            }}
            placeholder="ابحث عن منتج…"
          />
        </label>
      </div>
      {action.error && (
        <div role="alert" className="error">
          {action.error}
        </div>
      )}
      <State
        loading={products.loading}
        error={products.error}
        retry={products.reload}
        empty={!products.data?.items.length}
      >
        <section className="panel table-wrap">
          <table className="table">
            <thead>
              <tr>
                <th>المنتج</th>
                <th>السعر</th>
                <th>المتاح بالمخزون</th>
                <th>التوفر</th>
                <th>الإجراءات</th>
              </tr>
            </thead>
            <tbody>
              {products.data?.items.map((p) => (
                <tr key={p.id}>
                  <td>
                    <strong>{p.name}</strong>
                    <small>
                      {categories.data?.items.find(
                        (c) => c.id === p.category_id,
                      )?.name ?? "بدون تصنيف"}
                    </small>
                  </td>
                  <td>{money(p.price)}</td>
                  <td>{p.stock_quantity}</td>
                  <td>
                    <span
                      className={
                        "badge " +
                        (p.is_available
                          ? "status-Delivered"
                          : "status-Cancelled")
                      }
                    >
                      {p.is_available ? "متاح" : "مخفي"}
                    </span>
                  </td>
                  <td>
                    <div className="row-actions" style={{ margin: 0 }}>
                      <button onClick={() => setEditing(p)}>تعديل</button>
                      <button
                        disabled={action.busy}
                        onClick={() =>
                          void action.run(() =>
                            api("/products/" + p.id, "PATCH", {
                              merchant_id: p.merchant_id,
                              category_id: p.category_id,
                              name: p.name,
                              description: p.description,
                              price: p.price,
                              stock_quantity: p.stock_quantity,
                              is_available: !p.is_available,
                            }),
                          )
                        }
                      >
                        {p.is_available ? "إخفاء" : "إظهار"}
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>
        <Pages
          page={page}
          total={products.data?.total ?? 0}
          onChange={setPage}
        />
      </State>
      {editing !== undefined && (
        <Modal
          title={editing ? "تعديل المنتج" : "منتج جديد"}
          onClose={() => setEditing(undefined)}
        >
          <ProductForm
            user={user}
            product={editing}
            categories={categories.data?.items ?? []}
            merchants={merchants.data?.items ?? []}
            saved={() => {
              setEditing(undefined);
              void products.reload();
            }}
          />
        </Modal>
      )}
      {category !== undefined && (
        <Modal
          title={category ? "تعديل التصنيف" : "تصنيف جديد"}
          onClose={() => setCategory(undefined)}
        >
          <Form
            onSubmit={async (data) => {
              await api(
                "/categories" + (category ? "/" + category.id : ""),
                category ? "PATCH" : "POST",
                category
                  ? { name: val(data, "name") }
                  : {
                      name: val(data, "name"),
                      merchant_id:
                        user.role === "Admin"
                          ? Number(val(data, "merchant"))
                          : user.id,
                    },
              );
              setCategory(undefined);
              void categories.reload();
            }}
          >
            {user.role === "Admin" && !category && (
              <Field label="المتجر">
                <select name="merchant" required defaultValue="">
                  <option value="" disabled>
                    اختر المتجر
                  </option>
                  {merchants.data?.items.map((m) => (
                    <option key={m.id} value={m.id}>
                      {m.business_name}
                    </option>
                  ))}
                </select>
              </Field>
            )}
            <Field label="اسم التصنيف">
              <input
                name="name"
                required
                minLength={2}
                maxLength={100}
                defaultValue={category?.name}
              />
            </Field>
          </Form>
        </Modal>
      )}
    </>
  );
}
function ProductForm({
  user,
  product,
  categories,
  merchants,
  saved,
}: {
  user: User;
  product: Product | null;
  categories: Category[];
  merchants: Merchant[];
  saved: () => void;
}) {
  const [merchant, setMerchant] = useState(
    product?.merchant_id ?? (user.role === "Merchant" ? user.id : 0),
  );
  return (
    <Form
      onSubmit={async (data) => {
        await api(
          "/products" + (product ? "/" + product.id : ""),
          product ? "PATCH" : "POST",
          {
            merchant_id: merchant,
            category_id: Number(val(data, "category")) || null,
            name: val(data, "name"),
            description: val(data, "description"),
            price: val(data, "price"),
            stock_quantity: Number(val(data, "stock")),
            is_available: data.get("available") === "on",
          },
        );
        saved();
      }}
    >
      {user.role === "Admin" && (
        <Field label="المتجر">
          <select
            required
            value={merchant || ""}
            disabled={!!product}
            onChange={(e) => setMerchant(Number(e.target.value))}
          >
            <option value="" disabled>
              اختر المتجر
            </option>
            {merchants.map((m) => (
              <option key={m.id} value={m.id}>
                {m.business_name}
              </option>
            ))}
          </select>
        </Field>
      )}
      <Field label="اسم المنتج">
        <input
          name="name"
          required
          minLength={2}
          maxLength={150}
          defaultValue={product?.name}
        />
      </Field>
      <Field label="الوصف">
        <textarea
          name="description"
          maxLength={3000}
          defaultValue={product?.description}
        />
      </Field>
      <Field label="التصنيف">
        <select
          name="category"
          defaultValue={product?.category_id ?? 0}
          key={merchant}
        >
          <option value={0}>بدون تصنيف</option>
          {categories
            .filter((c) => c.merchant_id === merchant)
            .map((c) => (
              <option key={c.id} value={c.id}>
                {c.name}
              </option>
            ))}
        </select>
      </Field>
      <div className="form-grid">
        <Field label="السعر بالجنيه">
          <input
            name="price"
            type="number"
            required
            min="0.01"
            step="0.01"
            max="9999999"
            defaultValue={product?.price}
            dir="ltr"
          />
        </Field>
        <Field label="الكمية المتاحة">
          <input
            name="stock"
            type="number"
            required
            min={0}
            max={1000000}
            step={1}
            defaultValue={product?.stock_quantity ?? 0}
          />
        </Field>
      </div>
      <label className="check">
        <input
          type="checkbox"
          name="available"
          defaultChecked={product?.is_available ?? true}
        />
        المنتج متاح للعملاء
      </label>
    </Form>
  );
}
export function Business() {
  const profile = useData<Merchant>("/merchant/profile");
  const [saved, setSaved] = useState(false);
  return (
    <>
      <Header
        eyebrow="هوية متجرك"
        title="إعدادات المتجر"
        description="عرّف الناس بمتجرك وتحكّم في استقبال الطلبات."
      />
      <State
        loading={profile.loading}
        error={profile.error}
        retry={profile.reload}
      >
        {profile.data && (
          <section className="panel narrow">
            <div className="business-preview">
              <Store size={40} />
              <div>
                <h2>{profile.data.business_name}</h2>
                <p>
                  {profile.data.is_open
                    ? "المتجر يستقبل الطلبات"
                    : "المتجر مغلق حاليًا"}
                </p>
              </div>
            </div>
            <Form
              onSubmit={async (data) => {
                await api("/merchant/profile", "PATCH", {
                  business_name: val(data, "business_name"),
                  description: val(data, "description"),
                  is_open: data.get("open") === "on",
                });
                await profile.reload();
                setSaved(true);
              }}
            >
              <Field label="اسم المتجر">
                <input
                  name="business_name"
                  defaultValue={profile.data.business_name}
                  required
                  minLength={2}
                  maxLength={150}
                />
              </Field>
              <Field label="نبذة عن المتجر">
                <textarea
                  name="description"
                  defaultValue={profile.data.description}
                  maxLength={2000}
                />
              </Field>
              <label className="check">
                <input
                  name="open"
                  type="checkbox"
                  defaultChecked={profile.data.is_open}
                />
                المتجر مفتوح لاستقبال طلبات جديدة
              </label>
            </Form>
            {saved && (
              <p role="status" className="success">
                <Package size={17} />
                تم حفظ إعدادات المتجر.
              </p>
            )}
          </section>
        )}
      </State>
    </>
  );
}
