import { useEffect, useState } from "react";
import {
  ArrowLeft,
  Check,
  Heart,
  MapPin,
  Minus,
  Plus,
  Search,
  ShoppingBag,
  Store,
  Trash2,
  Truck,
  Wallet,
} from "lucide-react";
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
import type {
  Address,
  Cart,
  Category,
  Merchant,
  Named,
  Page,
  Product,
  User,
} from "../types";

export function Browse({
  user,
  navigate,
  onCart,
}: {
  user: User | null;
  navigate: (path: string) => void;
  onCart: () => void;
}) {
  const [search, setSearch] = useState(""),
    [query, setQuery] = useState(""),
    [merchant, setMerchant] = useState(0),
    [category, setCategory] = useState(0),
    [sort, setSort] = useState("name"),
    [page, setPage] = useState(1),
    [favoritesOnly, setFavoritesOnly] = useState(false);
  useEffect(() => {
    const t = setTimeout(() => {
      setQuery(search);
      setPage(1);
    }, 250);
    return () => clearTimeout(t);
  }, [search]);
  const merchants = useData<Page<Merchant>>(
    favoritesOnly && user
      ? "/favorites?page_size=100"
      : "/merchants?page_size=100" +
          (query ? "&q=" + encodeURIComponent(query) : ""),
  );
  const allMerchants = useData<Page<Merchant>>("/merchants?page_size=100");
  const products = useData<Page<Product>>(
    `/products?page=${page}&page_size=12&sort=${sort}&q=${encodeURIComponent(query)}${merchant ? "&merchant_id=" + merchant : ""}${category ? "&category_id=" + category : ""}`,
  );
  const categories = useData<Page<Category>>(
    "/categories?page_size=100" + (merchant ? "&merchant_id=" + merchant : ""),
  );
  const favorites = useData<Page<Merchant>>(
    user?.role === "Customer" ? "/favorites?page_size=100" : null,
  );
  const [added, setAdded] = useState<number | null>(null);
  const action = useAction();
  const selected = allMerchants.data?.items.find((m) => m.id === merchant);
  return (
    <>
      <div className="browse-top">
        <div className="eyebrow">
          <MapPin size={13} /> توصيل داخل أبو حماد
        </div>
        <span className="service-chip">
          <span /> بنقرّب لك كل حاجة
        </span>
      </div>
      <section className="hero">
        <div>
          <div className="hero-tag">
            <Truck size={17} /> من متاجر بلدك… لحد بابك
          </div>
          <h1>
            كل اللي محتاجه،
            <br />
            <em>على بُعد طلب.</em>
          </h1>
          <p>
            أكل، بقالة، ومستلزمات يومك من متاجر أبو حماد.
            <br />
            اختار طلبك وسيب التوصيل علينا.
          </p>
          <div className="hero-promises">
            <span>
              <Wallet size={16} /> الدفع عند الاستلام
            </span>
            <span>
              <Check size={16} /> متابعة كل خطوة
            </span>
          </div>
        </div>
        <div className="hero-illustration" aria-hidden="true">
          <div className="orbit" />
          <div className="parcel back">
            <Store size={48} />
          </div>
          <div className="parcel front">
            <ShoppingBag size={78} />
            <span>وصلة</span>
          </div>
          <div className="delivery-note">
            <div className="mini-icon">
              <Truck size={22} />
            </div>
            <div>
              <strong>من قلب أبو حماد</strong>
              <small>متاجر قريبة، خيارات كتير</small>
            </div>
          </div>
          <span className="spark s1">✦</span>
          <span className="spark s2">✦</span>
        </div>
      </section>
      <div className="section-heading">
        <div>
          <h2>متاجر قريبة منك</h2>
          <p>اختار متجرك وابدأ طلبك</p>
        </div>
        {user?.role === "Customer" && (
          <button
            className={favoritesOnly ? "selected" : ""}
            onClick={() => setFavoritesOnly(!favoritesOnly)}
          >
            <Heart size={17} />
            المفضلة
          </button>
        )}
      </div>
      <State
        loading={merchants.loading}
        error={merchants.error}
        retry={merchants.reload}
        empty={merchants.data?.items.length === 0}
      >
        <div className="merchant-strip">
          <button
            className={"merchant-tile " + (!merchant ? "selected" : "")}
            onClick={() => {
              setMerchant(0);
              setCategory(0);
              setPage(1);
            }}
          >
            <div className="store-icon">
              <Store />
            </div>
            <strong>كل المتاجر</strong>
            <small>اكتشف اختياراتك</small>
          </button>
          {merchants.data?.items.map((m, i) => (
            <div className={"merchant-tile-wrap tone-" + (i % 4)} key={m.id}>
              <button
                className={
                  "merchant-tile " + (merchant === m.id ? "selected" : "")
                }
                onClick={() => {
                  setMerchant(m.id);
                  setCategory(0);
                  setPage(1);
                }}
              >
                <div className="store-icon">
                  <Store />
                </div>
                <strong>{m.business_name}</strong>
                <small className={m.is_open ? "open" : "closed"}>
                  {m.is_open ? "مفتوح للطلبات" : "مغلق حاليًا"}
                </small>
              </button>
              {user?.role === "Customer" && (
                <button
                  className="favorite icon"
                  aria-label={
                    "إضافة أو إزالة " + m.business_name + " من المفضلة"
                  }
                  onClick={() =>
                    void action.run(async () => {
                      const exists = favorites.data?.items.some(
                        (f) => f.id === m.id,
                      );
                      await api(
                        "/favorites/" + m.id,
                        exists ? "DELETE" : "PUT",
                      );
                      void favorites.reload();
                      if (favoritesOnly) void merchants.reload();
                    })
                  }
                >
                  <Heart
                    size={16}
                    fill={
                      favorites.data?.items.some((f) => f.id === m.id)
                        ? "currentColor"
                        : "none"
                    }
                  />
                </button>
              )}
            </div>
          ))}
        </div>
      </State>
      <div className="section-heading">
        <div>
          <h2>{selected?.business_name ?? "اختار اللي على بالك"}</h2>
          <p>
            {selected?.description ?? "منتجات من متاجر بلدك، بأسعار واضحة."}
          </p>
        </div>
        <span className="count">{products.data?.total ?? 0} منتج</span>
      </div>
      <div className="filters">
        <label className="search">
          <Search size={19} />
          <input
            aria-label="البحث عن منتج أو متجر"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="بتدوّر على إيه النهارده؟"
          />
        </label>
        <select
          aria-label="التصنيف"
          value={category}
          onChange={(e) => {
            setCategory(Number(e.target.value));
            setPage(1);
          }}
        >
          <option value={0}>كل التصنيفات</option>
          {categories.data?.items.map((c) => (
            <option key={c.id} value={c.id}>
              {c.name}
            </option>
          ))}
        </select>
        <select
          aria-label="ترتيب المنتجات"
          value={sort}
          onChange={(e) => {
            setSort(e.target.value);
            setPage(1);
          }}
        >
          <option value="name">حسب الاسم</option>
          <option value="price">السعر: الأقل أولًا</option>
          <option value="-price">السعر: الأعلى أولًا</option>
        </select>
      </div>
      {action.error && (
        <div className="error" role="alert">
          {action.error}
        </div>
      )}
      <State
        loading={products.loading}
        error={products.error}
        empty={products.data?.items.length === 0}
        retry={products.reload}
      >
        <div className="product-grid">
          {products.data?.items.map((p, i) => (
            <article className="product-card" key={p.id}>
              <div className={"product-art tone-" + (i % 4)}>
                <ShoppingBag size={66} />
                <span className="product-category">
                  {categories.data?.items.find((c) => c.id === p.category_id)
                    ?.name ?? "من متاجر بلدك"}
                </span>
              </div>
              <div className="product-body">
                <small>
                  {
                    allMerchants.data?.items.find((m) => m.id === p.merchant_id)
                      ?.business_name
                  }
                </small>
                <h3>{p.name}</h3>
                <p>{p.description || "جودة تختارها من متجرك المفضل."}</p>
                <div className="product-bottom">
                  <strong>{money(p.price)}</strong>
                  <button
                    className="add-button"
                    disabled={
                      action.busy ||
                      p.stock_quantity < 1 ||
                      allMerchants.data?.items.find(
                        (m) => m.id === p.merchant_id,
                      )?.is_open === false
                    }
                    aria-label={"أضف " + p.name + " للسلة"}
                    onClick={() => {
                      if (!user) {
                        navigate("login");
                        return;
                      }
                      void action.run(async () => {
                        const cart = await api<Cart>("/cart");
                        const quantity =
                          (cart.items.find((item) => item.product_id === p.id)
                            ?.quantity ?? 0) + 1;
                        await api("/cart/items/" + p.id, "PUT", { quantity });
                        setAdded(p.id);
                        onCart();
                        setTimeout(() => setAdded(null), 1500);
                      });
                    }}
                  >
                    {added === p.id ? <Check size={20} /> : <Plus size={20} />}
                  </button>
                </div>
                {p.stock_quantity < 1 && (
                  <small className="closed">نفدت الكمية</small>
                )}
              </div>
            </article>
          ))}
        </div>
        <Pages
          page={page}
          total={products.data?.total ?? 0}
          onChange={setPage}
        />
      </State>
      {selected && <MerchantReviews identity={selected.id} />}
      <div className="help-strip">
        <Truck size={24} />
        <div>
          <strong>طلبك من متجر واحد، في توصيل واحد.</strong>
          <span>تابع حالة طلبك من حسابك، وادفع كاش لما يستلم.</span>
        </div>
        <button
          className="text-button"
          onClick={() => navigate(user ? "orders" : "login")}
        >
          متابعة طلباتي <ArrowLeft size={16} />
        </button>
      </div>
    </>
  );
}
function MerchantReviews({ identity }: { identity: number }) {
  const reviews = useData<
    Page<{ id: number; rating: number; comment: string }>
  >(`/merchants/${identity}/reviews?page_size=10`);
  return reviews.data?.items.length ? (
    <section className="panel">
      <h3>آراء العملاء</h3>
      {reviews.data.items.map((r) => (
        <p key={r.id}>
          ⭐ {r.rating}/5 — {r.comment}
        </p>
      ))}
    </section>
  ) : null;
}

export function CartPage({
  navigate,
  onCart,
}: {
  navigate: (path: string) => void;
  onCart: () => void;
}) {
  const cart = useData<Cart>("/cart"),
    addresses = useData<Address[]>("/addresses");
  const [address, setAddress] = useState(0),
    [key, setKey] = useState(() => crypto.randomUUID());
  const action = useAction(() => {
    void cart.reload();
    onCart();
  });
  useEffect(() => {
    if (addresses.data?.length)
      setAddress(
        addresses.data.find((a) => a.is_default)?.id ?? addresses.data[0].id,
      );
  }, [addresses.data]);
  return (
    <>
      <Header
        eyebrow="طلباتك على ذوقك"
        title="سلة المشتريات"
        description="راجع طلبك وحدد عنوان التوصيل. الدفع عند الاستلام فقط."
      />
      <State
        loading={cart.loading}
        error={cart.error}
        retry={cart.reload}
        empty={!cart.data?.items.length}
      >
        <div className="checkout-layout">
          <section className="panel">
            <h2>المنتجات</h2>
            {cart.data?.items.map((item) => (
              <div className="cart-line" key={item.product_id}>
                <div className="item-avatar">
                  <ShoppingBag />
                </div>
                <div className="grow">
                  <h3>{item.name}</h3>
                  <small>{money(item.price)} للقطعة</small>
                </div>
                <div className="quantity">
                  <button
                    aria-label={"تقليل " + item.name}
                    disabled={action.busy || item.quantity === 1}
                    onClick={() =>
                      void action.run(() =>
                        api("/cart/items/" + item.product_id, "PUT", {
                          quantity: item.quantity - 1,
                        }),
                      )
                    }
                  >
                    <Minus size={14} />
                  </button>
                  <span>{item.quantity}</span>
                  <button
                    aria-label={"زيادة " + item.name}
                    disabled={action.busy || item.quantity >= 99}
                    onClick={() =>
                      void action.run(() =>
                        api("/cart/items/" + item.product_id, "PUT", {
                          quantity: item.quantity + 1,
                        }),
                      )
                    }
                  >
                    <Plus size={14} />
                  </button>
                </div>
                <strong>{money(Number(item.price) * item.quantity)}</strong>
                <button
                  className="icon danger"
                  disabled={action.busy}
                  aria-label={"إزالة " + item.name}
                  onClick={() =>
                    void action.run(() =>
                      api("/cart/items/" + item.product_id, "DELETE"),
                    )
                  }
                >
                  <Trash2 size={17} />
                </button>
              </div>
            ))}
            <button className="text-button" onClick={() => navigate("browse")}>
              إضافة منتجات أخرى <Plus size={16} />
            </button>
          </section>
          <aside className="panel summary">
            <h2>ملخص الطلب</h2>
            <div>
              <span>قيمة المنتجات</span>
              <strong>{money(cart.data?.subtotal ?? 0)}</strong>
            </div>
            <div>
              <span>رسوم التوصيل الحالية</span>
              <strong>{money(cart.data?.delivery_fee ?? 0)}</strong>
            </div>
            <div className="total">
              <span>الإجمالي</span>
              <strong>
                {money(
                  Number(cart.data?.subtotal ?? 0) +
                    Number(cart.data?.delivery_fee ?? 0),
                )}
              </strong>
            </div>
            <State
              loading={addresses.loading}
              error={addresses.error}
              retry={addresses.reload}
            >
              <Field label="عنوان التوصيل">
                <select
                  value={address}
                  onChange={(e) => {
                    setAddress(Number(e.target.value));
                    setKey(crypto.randomUUID());
                  }}
                >
                  <option value={0}>اختر العنوان</option>
                  {addresses.data?.map((a) => (
                    <option key={a.id} value={a.id}>
                      {a.title} — {a.street}
                    </option>
                  ))}
                </select>
              </Field>
            </State>
            <button
              className="text-button"
              onClick={() => navigate("addresses")}
            >
              <MapPin size={16} /> إضافة أو تعديل عنوان
            </button>
            <div className="payment">
              <Wallet />
              <div>
                <strong>الدفع عند الاستلام</strong>
                <small>ادفع للمندوب نقدًا بعد وصول الطلب.</small>
              </div>
            </div>
            {action.error && (
              <div className="error" role="alert">
                {action.error}
              </div>
            )}
            <button
              className="primary"
              disabled={action.busy || !address}
              onClick={() =>
                void action.run(async () => {
                  const order = await api<{ id: number }>("/checkout", "POST", {
                    address_id: address,
                    idempotency_key: key,
                  });
                  onCart();
                  navigate("orders/" + order.id);
                })
              }
            >
              {action.busy ? "جارٍ تأكيد الطلب…" : "تأكيد الطلب"}
              <ArrowLeft size={17} />
            </button>
            <small>يمكن إلغاء الطلب قبل قبول المتجر فقط.</small>
          </aside>
        </div>
      </State>
    </>
  );
}

export function Addresses() {
  const list = useData<Address[]>("/addresses"),
    cities = useData<Page<Named>>("/cities?page_size=100");
  const [editing, setEditing] = useState<Address | null | undefined>(undefined);
  const action = useAction(() => void list.reload());
  return (
    <>
      <Header
        eyebrow="يوصلك لحد بابك"
        title="عناوين التوصيل"
        description="احفظ عنوانك مكتوبًا ومعه الموقع لتسهيل التوصيل."
        action={
          <button className="primary" onClick={() => setEditing(null)}>
            <Plus size={17} />
            إضافة عنوان
          </button>
        }
      />
      {action.error && (
        <div className="error" role="alert">
          {action.error}
        </div>
      )}
      <State
        loading={list.loading}
        error={list.error}
        empty={!list.data?.length}
        retry={list.reload}
      >
        <div className="address-grid">
          {list.data?.map((a) => (
            <article className="panel" key={a.id}>
              <div className="address-top">
                <MapPin />
                <h3>{a.title}</h3>
                {a.is_default && <span className="badge">الافتراضي</span>}
              </div>
              <p>{a.street}</p>
              <small>
                {cities.data?.items.find((c) => c.id === a.city_id)?.name}
              </small>
              <div className="row-actions">
                <button onClick={() => setEditing(a)}>تعديل</button>
                <button
                  className="danger"
                  disabled={action.busy}
                  onClick={() =>
                    void action.run(() => api("/addresses/" + a.id, "DELETE"))
                  }
                >
                  حذف العنوان
                </button>
              </div>
            </article>
          ))}
        </div>
      </State>
      {editing !== undefined && (
        <Modal
          title={editing ? "تعديل العنوان" : "عنوان جديد"}
          onClose={() => setEditing(undefined)}
        >
          <AddressForm
            address={editing}
            cities={cities.data?.items ?? []}
            onSaved={() => {
              setEditing(undefined);
              void list.reload();
            }}
          />
        </Modal>
      )}
    </>
  );
}
function AddressForm({
  address,
  cities,
  onSaved,
}: {
  address: Address | null;
  cities: Named[];
  onSaved: () => void;
}) {
  const [lat, setLat] = useState(address?.latitude ?? ""),
    [lng, setLng] = useState(address?.longitude ?? ""),
    [geoError, setGeoError] = useState(""),
    [city, setCity] = useState(address?.city_id ?? cities[0]?.id ?? 0);
  const areas = useData<Page<Named>>(
    city ? "/areas?city_id=" + city + "&page_size=100" : null,
  );
  function locate() {
    setGeoError("");
    if (!navigator.geolocation) {
      setGeoError("المتصفح لا يدعم الموقع؛ أدخل الإحداثيات يدويًا.");
      return;
    }
    navigator.geolocation.getCurrentPosition(
      (p) => {
        setLat(p.coords.latitude.toFixed(7));
        setLng(p.coords.longitude.toFixed(7));
      },
      () =>
        setGeoError(
          "تعذّر تحديد الموقع. اسمح بالوصول للموقع أو أدخل الإحداثيات يدويًا.",
        ),
      { timeout: 10000, enableHighAccuracy: true },
    );
  }
  return (
    <Form
      onSubmit={async (data) => {
        await api(
          "/addresses" + (address ? "/" + address.id : ""),
          address ? "PATCH" : "POST",
          {
            title: val(data, "title"),
            street: val(data, "street"),
            city_id: city,
            area_id: Number(val(data, "area")) || null,
            latitude: lat,
            longitude: lng,
            is_default: data.get("default") === "on",
          },
        );
        onSaved();
      }}
    >
      <Field label="اسم العنوان">
        <input
          name="title"
          required
          minLength={2}
          maxLength={100}
          defaultValue={address?.title}
          placeholder="المنزل أو الشغل"
        />
      </Field>
      <Field label="العنوان بالتفصيل">
        <textarea
          name="street"
          required
          minLength={5}
          maxLength={255}
          defaultValue={address?.street}
          placeholder="الشارع، رقم البيت، الدور، وعلامة مميزة"
        />
      </Field>
      <div className="form-grid">
        <Field label="المدينة">
          <select
            required
            value={city}
            onChange={(e) => setCity(Number(e.target.value))}
          >
            <option value={0}>اختر المدينة</option>
            {cities.map((c) => (
              <option key={c.id} value={c.id}>
                {c.name}
              </option>
            ))}
          </select>
        </Field>
        <Field label="المنطقة (اختياري)">
          <select name="area" defaultValue={address?.area_id ?? 0}>
            <option value={0}>بدون تحديد</option>
            {areas.data?.items.map((a) => (
              <option key={a.id} value={a.id}>
                {a.name}
              </option>
            ))}
          </select>
        </Field>
      </div>
      <button type="button" onClick={locate}>
        <MapPin size={17} />
        استخدم موقعي الحالي
      </button>
      {geoError && (
        <p role="alert" className="error">
          {geoError}
        </p>
      )}
      <div className="form-grid">
        <Field label="خط العرض">
          <input
            required
            type="number"
            step="any"
            min={-90}
            max={90}
            value={lat}
            onChange={(e) => setLat(e.target.value)}
            dir="ltr"
          />
        </Field>
        <Field label="خط الطول">
          <input
            required
            type="number"
            step="any"
            min={-180}
            max={180}
            value={lng}
            onChange={(e) => setLng(e.target.value)}
            dir="ltr"
          />
        </Field>
      </div>
      <label className="check">
        <input
          type="checkbox"
          name="default"
          defaultChecked={address?.is_default}
        />
        العنوان الافتراضي
      </label>
    </Form>
  );
}
