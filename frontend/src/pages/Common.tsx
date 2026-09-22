import { useState } from "react";
import {
  ArrowLeft,
  Bell,
  CheckCheck,
  MapPin,
  Package,
  ShoppingBag,
} from "lucide-react";
import { api, date, money, statusName } from "../api";
import {
  Badge,
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
import type { Driver, Notice, Order, Page, User } from "../types";

export function Orders({
  user,
  navigate,
  identity,
}: {
  user: User;
  navigate: (path: string) => void;
  identity?: number;
}) {
  const [page, setPage] = useState(1),
    [filter, setFilter] = useState("");
  const list = useData<Page<Order>>(
    `/orders?page=${page}&page_size=12${filter ? "&status=" + filter : ""}`,
    10000,
  );
  const detail = useData<Order>(identity ? "/orders/" + identity : null, 10000);
  const action = useAction(() => {
    void list.reload();
    void detail.reload();
  });
  const [reason, setReason] = useState<{ id: number; status: string } | null>(
      null,
    ),
    [review, setReview] = useState<number | null>(null),
    [assign, setAssign] = useState<number | null>(null);
  const title = user.role === "Customer" ? "طلباتك" : "إدارة الطلبات";
  function transition(order: Order, status: string) {
    if (status === "Rejected" || status === "Cancelled") {
      setReason({ id: order.id, status });
      return;
    }
    void action.run(() =>
      api(`/orders/${order.id}/transition`, "POST", { status }),
    );
  }
  return (
    <>
      <Header
        eyebrow="كل خطوة في مكانها"
        title={identity ? "تفاصيل الطلب #" + identity : title}
        description="الحالة تتحدث تلقائيًا. راجع آخر تحديث قبل اتخاذ أي إجراء."
        action={
          identity ? (
            <button onClick={() => navigate("orders")}>
              كل الطلبات <ArrowLeft size={16} />
            </button>
          ) : (
            <select
              aria-label="حالة الطلب"
              value={filter}
              onChange={(e) => {
                setFilter(e.target.value);
                setPage(1);
              }}
            >
              <option value="">كل الحالات</option>
              {Object.entries(statusName)
                .filter(([s]) => s !== "Completed")
                .map(([s, n]) => (
                  <option key={s} value={s}>
                    {n}
                  </option>
                ))}
            </select>
          )
        }
      />
      {action.error && (
        <div role="alert" className="error">
          {action.error}
        </div>
      )}
      <State
        loading={identity ? detail.loading : list.loading}
        error={identity ? detail.error : list.error}
        retry={identity ? detail.reload : list.reload}
        empty={identity ? !detail.data : !list.data?.items.length}
      >
        <div className={identity ? "order-detail" : "orders-grid"}>
          {(identity
            ? detail.data
              ? [detail.data]
              : []
            : (list.data?.items ?? [])
          ).map((order) => (
            <article className="panel order-card" key={order.id}>
              <div className="order-top">
                <div className="item-avatar">
                  <Package />
                </div>
                <div className="grow">
                  <strong>طلب #{order.id}</strong>
                  <small>
                    {order.merchant_name} · {date(order.created_at)}
                  </small>
                </div>
                <Badge status={order.status} />
              </div>
              <div className="order-items">
                {order.items.map((item, i) => (
                  <p key={i}>
                    <ShoppingBag size={15} />
                    <span>
                      {item.product_name} <small>× {item.quantity}</small>
                    </span>
                    <strong>
                      {money(Number(item.unit_price) * item.quantity)}
                    </strong>
                  </p>
                ))}
              </div>
              <div className="order-total">
                <span>الإجمالي · الدفع عند الاستلام</span>
                <strong>{money(order.total_price)}</strong>
              </div>
              {identity && (
                <>
                  <div className="delivery-address">
                    <MapPin size={19} />
                    <div>
                      <strong>{order.address_snapshot.title}</strong>
                      <p>{order.address_snapshot.street}</p>
                      {user.role !== "Customer" && (
                        <>
                          <p>
                            {order.customer_name} ·{" "}
                            <a href={"tel:" + order.customer_phone}>
                              {order.customer_phone}
                            </a>
                          </p>
                          {user.role === "Driver" && (
                            <a
                              href={`https://www.openstreetmap.org/?mlat=${order.address_snapshot.latitude}&mlon=${order.address_snapshot.longitude}#map=17/${order.address_snapshot.latitude}/${order.address_snapshot.longitude}`}
                              target="_blank"
                              rel="noreferrer"
                            >
                              فتح عنوان العميل على الخريطة
                            </a>
                          )}
                        </>
                      )}
                    </div>
                  </div>
                  <div className="timeline">
                    {order.history.map((h, i) => (
                      <div key={i}>
                        <span className="timeline-dot" />
                        <div>
                          <strong>{statusName[h.status]}</strong>
                          <small>{date(h.created_at)}</small>
                          {h.note && <p>{h.note}</p>}
                        </div>
                      </div>
                    ))}
                  </div>
                </>
              )}
              {order.rejection_reason && (
                <div className="error">سبب الرفض: {order.rejection_reason}</div>
              )}
              <div className="row-actions">
                {!identity && (
                  <button onClick={() => navigate("orders/" + order.id)}>
                    تفاصيل الطلب <ArrowLeft size={15} />
                  </button>
                )}
                {user.role === "Customer" && order.status === "Pending" && (
                  <button
                    disabled={action.busy}
                    className="danger"
                    onClick={() => transition(order, "Cancelled")}
                  >
                    إلغاء الطلب
                  </button>
                )}
                {user.role === "Customer" && order.status === "Delivered" && (
                  <button onClick={() => setReview(order.id)}>
                    تقييم المتجر
                  </button>
                )}
                {(user.role === "Merchant" || user.role === "Admin") &&
                  order.status === "Pending" && (
                    <>
                      <button
                        className="primary"
                        disabled={action.busy}
                        onClick={() => transition(order, "Accepted")}
                      >
                        قبول الطلب
                      </button>
                      <button
                        className="danger"
                        disabled={action.busy}
                        onClick={() => transition(order, "Rejected")}
                      >
                        رفض الطلب
                      </button>
                    </>
                  )}
                {(user.role === "Merchant" || user.role === "Admin") &&
                  order.status === "Accepted" && (
                    <button
                      className="primary"
                      disabled={action.busy}
                      onClick={() => transition(order, "Preparing")}
                    >
                      بدء التجهيز
                    </button>
                  )}
                {(user.role === "Merchant" || user.role === "Admin") &&
                  order.status === "Preparing" && (
                    <button
                      className="primary"
                      disabled={action.busy}
                      onClick={() => transition(order, "Ready")}
                    >
                      جاهز للاستلام
                    </button>
                  )}
                {user.role === "Admin" &&
                  order.status === "Ready" &&
                  (!order.assignment ||
                    order.assignment.status === "Rejected") && (
                    <button
                      className="primary"
                      onClick={() => setAssign(order.id)}
                    >
                      تعيين سائق
                    </button>
                  )}
                {user.role === "Driver" &&
                  order.assignment?.status === "Pending" && (
                    <>
                      <button
                        className="primary"
                        disabled={action.busy}
                        onClick={() =>
                          void action.run(() =>
                            api(
                              `/assignments/${order.assignment!.id}/respond`,
                              "POST",
                              { accept: true },
                            ),
                          )
                        }
                      >
                        قبول التوصيلة
                      </button>
                      <button
                        className="danger"
                        disabled={action.busy}
                        onClick={() =>
                          void action.run(() =>
                            api(
                              `/assignments/${order.assignment!.id}/respond`,
                              "POST",
                              {
                                accept: false,
                                reason: "السائق غير متاح لهذه التوصيلة",
                              },
                            ),
                          )
                        }
                      >
                        رفض التوصيلة
                      </button>
                    </>
                  )}
                {(user.role === "Driver" || user.role === "Admin") &&
                  order.assignment?.status === "Accepted" &&
                  order.status === "Ready" && (
                    <button
                      className="primary"
                      disabled={action.busy}
                      onClick={() => transition(order, "OnDelivery")}
                    >
                      تم استلام الطلب
                    </button>
                  )}
                {(user.role === "Driver" || user.role === "Admin") &&
                  order.status === "OnDelivery" && (
                    <button
                      className="primary"
                      disabled={action.busy}
                      onClick={() => transition(order, "Delivered")}
                    >
                      تأكيد التسليم وتحصيل الكاش
                    </button>
                  )}
              </div>
              {order.assignment && user.role === "Admin" && (
                <small>
                  السائق #{order.assignment.driver_id} ·{" "}
                  {statusName[order.assignment.status]}{" "}
                  {order.assignment.reason && "· " + order.assignment.reason}
                </small>
              )}
            </article>
          ))}
        </div>
        {!identity && (
          <Pages page={page} total={list.data?.total ?? 0} onChange={setPage} />
        )}
      </State>
      {reason && (
        <Modal
          title={reason.status === "Rejected" ? "سبب رفض الطلب" : "إلغاء الطلب"}
          onClose={() => setReason(null)}
        >
          <p>
            {reason.status === "Cancelled"
              ? "هل تريد إلغاء الطلب؟ الإلغاء متاح قبل قبول المتجر فقط."
              : "السبب سيظهر للعميل في تفاصيل الطلب والإشعار."}
          </p>
          <Form
            submit={
              reason.status === "Cancelled" ? "تأكيد الإلغاء" : "تأكيد الرفض"
            }
            onSubmit={async (data) => {
              await api(`/orders/${reason.id}/transition`, "POST", {
                status: reason.status,
                reason:
                  val(data, "reason") ||
                  "Customer cancelled before merchant acceptance.",
              });
              setReason(null);
              void list.reload();
              void detail.reload();
            }}
          >
            {reason.status === "Rejected" && (
              <Field label="سبب الرفض">
                <textarea
                  name="reason"
                  required
                  minLength={2}
                  maxLength={255}
                />
              </Field>
            )}
          </Form>
        </Modal>
      )}
      {review && (
        <Modal title="تقييم المتجر" onClose={() => setReview(null)}>
          <Form
            onSubmit={async (data) => {
              await api(`/orders/${review}/review`, "POST", {
                rating: Number(val(data, "rating")),
                comment: val(data, "comment"),
              });
              setReview(null);
            }}
          >
            <Field label="تقييمك">
              <select name="rating" defaultValue={5}>
                {[5, 4, 3, 2, 1].map((n) => (
                  <option key={n} value={n}>
                    {n} من 5
                  </option>
                ))}
              </select>
            </Field>
            <Field label="رأيك في المتجر">
              <textarea name="comment" maxLength={2000} />
            </Field>
          </Form>
        </Modal>
      )}
      {assign && (
        <Modal
          title={"تعيين سائق للطلب #" + assign}
          onClose={() => setAssign(null)}
        >
          <AssignForm
            order={assign}
            saved={() => {
              setAssign(null);
              void list.reload();
              void detail.reload();
            }}
          />
        </Modal>
      )}
    </>
  );
}
function AssignForm({ order, saved }: { order: number; saved: () => void }) {
  const drivers = useData<Page<Driver>>("/admin/drivers?page_size=100");
  return (
    <State
      loading={drivers.loading}
      error={drivers.error}
      retry={drivers.reload}
    >
      <Form
        submit="تعيين السائق"
        onSubmit={async (data) => {
          await api(`/orders/${order}/assignments`, "POST", {
            driver_id: Number(val(data, "driver")),
          });
          saved();
        }}
      >
        <Field label="السائق المتاح">
          <select name="driver" required defaultValue="">
            <option value="" disabled>
              اختر سائقًا
            </option>
            {drivers.data?.items
              .filter((d) => d.is_active && d.is_available && !d.busy)
              .map((d) => (
                <option key={d.id} value={d.id}>
                  {d.name}
                </option>
              ))}
          </select>
        </Field>
        <p>يظهر السائق بعد تفعيل التوفر وتحديث حالته خلال آخر 30 دقيقة.</p>
      </Form>
    </State>
  );
}
export function Notifications() {
  const [page, setPage] = useState(1);
  const list = useData<Page<Notice>>(
    `/notifications?page=${page}&page_size=12`,
    10000,
  );
  const action = useAction(() => void list.reload());
  return (
    <>
      <Header
        eyebrow="كل جديد يهمك"
        title="الإشعارات"
        description="تحديثات طلباتك وتوصيلاتك أولًا بأول."
      />
      {action.error && <div className="error">{action.error}</div>}
      <State
        loading={list.loading}
        error={list.error}
        retry={list.reload}
        empty={!list.data?.items.length}
      >
        <div className="panel notice-list">
          {list.data?.items.map((n) => (
            <article className={n.is_read ? "read" : "unread"} key={n.id}>
              <div className="item-avatar">
                <Bell size={19} />
              </div>
              <div className="grow">
                <h3>{n.title}</h3>
                <p>{n.message}</p>
                <small>{date(n.created_at)}</small>
              </div>
              {!n.is_read && (
                <button
                  aria-label="تحديد كمقروء"
                  disabled={action.busy}
                  onClick={() =>
                    void action.run(() =>
                      api("/notifications/" + n.id + "/read", "PATCH"),
                    )
                  }
                >
                  <CheckCheck size={18} />
                </button>
              )}
            </article>
          ))}
        </div>
        <Pages page={page} total={list.data?.total ?? 0} onChange={setPage} />
      </State>
    </>
  );
}
export function Profile({
  user,
  onUser,
}: {
  user: User;
  onUser: (u: User) => void;
}) {
  const [saved, setSaved] = useState(false);
  return (
    <>
      <Header eyebrow="حسابك" title="الملف الشخصي" />
      <section className="panel narrow">
        <Form
          onSubmit={async (data) => {
            const value = await api<User>("/auth/profile", "PATCH", {
              name: val(data, "name"),
              phone: val(data, "phone"),
            });
            onUser(value);
            setSaved(true);
          }}
        >
          <Field label="الاسم">
            <input
              name="name"
              required
              minLength={2}
              maxLength={100}
              defaultValue={user.name}
            />
          </Field>
          <Field label="رقم الموبايل">
            <input
              name="phone"
              required
              pattern="\+?[0-9]{10,15}"
              dir="ltr"
              defaultValue={user.phone}
            />
          </Field>
          <Field label="البريد الإلكتروني">
            <input type="email" value={user.email} readOnly dir="ltr" />
          </Field>
        </Form>
        {saved && (
          <p className="success" role="status">
            تم حفظ التغييرات.
          </p>
        )}
      </section>
    </>
  );
}
