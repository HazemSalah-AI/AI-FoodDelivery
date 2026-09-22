import {
  ArrowLeft,
  CheckCircle2,
  Clock3,
  Package,
  Truck,
  Wallet,
} from "lucide-react";
import { date, money } from "../api";
import { Badge, Header, State, useData } from "../components/ui";
import type { Order, Page, Stats, User } from "../types";
export function Dashboard({
  user,
  navigate,
}: {
  user: User;
  navigate: (path: string) => void;
}) {
  const stats = useData<Stats>(
    "/" + user.role.toLowerCase() + "/dashboard",
    10000,
  );
  const orders = useData<Page<Order>>("/orders?page_size=5", 10000);
  const labels =
    user.role === "Merchant"
      ? ["متجرك في نظرة", "تابع الطلبات وجهّزها في الوقت المناسب."]
      : user.role === "Driver"
        ? ["توصيلاتك النهارده", "استقبل التوصيلات، وأكّد كل خطوة بعد تنفيذها."]
        : ["البلد بتطلب، وإنت بتتابع", "كل الطلبات والعمليات في مكان واحد."];
  return (
    <>
      <Header
        eyebrow={"أهلًا، " + user.name}
        title={labels[0]}
        description={labels[1]}
        action={
          <button onClick={() => navigate("orders")}>
            كل الطلبات <ArrowLeft size={16} />
          </button>
        }
      />
      <State loading={stats.loading} error={stats.error} retry={stats.reload}>
        {stats.data && (
          <>
            <div className="stats-grid">
              {[
                {
                  title: "إجمالي الطلبات",
                  value: String(stats.data.orders_total),
                  icon: Package,
                  note: "الطلبات المسموح لحسابك بمتابعتها",
                },
                {
                  title: "جاهز للاستلام",
                  value: String(stats.data.ready),
                  icon: Clock3,
                  note: "بانتظار الاستلام من المتجر",
                },
                {
                  title: "في الطريق",
                  value: String(stats.data.on_delivery),
                  icon: Truck,
                  note: "تم استلامها من المتجر",
                },
                {
                  title: "قيمة الطلبات المسلّمة",
                  value: money(stats.data.cod_total),
                  icon: Wallet,
                  note: "إجمالي الكاش • وليس أرباح السائق",
                },
              ].map((s) => (
                <article className="panel stat" key={s.title}>
                  <span>
                    {s.title}
                    <s.icon size={18} />
                  </span>
                  <strong>{s.value}</strong>
                  <small>{s.note}</small>
                </article>
              ))}
            </div>
            <div className="dashboard-grid">
              <section className="panel">
                <div className="section-heading" style={{ marginTop: 0 }}>
                  <h2>آخر الطلبات</h2>
                  <Package size={20} />
                </div>
                <State
                  loading={orders.loading}
                  error={orders.error}
                  retry={orders.reload}
                  empty={!orders.data?.items.length}
                >
                  <div>
                    {orders.data?.items.map((o) => (
                      <div className="list-row" key={o.id}>
                        <div className="item-avatar">
                          <Package size={20} />
                        </div>
                        <div className="grow">
                          <strong>
                            طلب #{o.id} · {o.merchant_name}
                          </strong>
                          <small>
                            {date(o.created_at)} · {money(o.total_price)}
                          </small>
                        </div>
                        <Badge status={o.status} />
                        <button onClick={() => navigate("orders/" + o.id)}>
                          عرض
                        </button>
                      </div>
                    ))}
                  </div>
                </State>
              </section>
              <section className="panel">
                <h2>حركة الطلبات</h2>
                <p>توزيع الحالات الحالية</p>
                <div
                  className="chart-bars"
                  role="img"
                  aria-label={`بانتظار القبول ${stats.data.pending}، جاهز ${stats.data.ready}، في الطريق ${stats.data.on_delivery}، تم التسليم ${stats.data.delivered}`}
                >
                  {[
                    { name: "انتظار", count: stats.data.pending },
                    { name: "جاهز", count: stats.data.ready },
                    { name: "في الطريق", count: stats.data.on_delivery },
                    { name: "تم", count: stats.data.delivered },
                  ].map((s) => (
                    <div key={s.name}>
                      <strong>{s.count}</strong>
                      <i
                        style={{
                          height: Math.max(
                            4,
                            (s.count / Math.max(stats.data!.orders_total, 1)) *
                              120,
                          ),
                        }}
                      />
                      <span>{s.name}</span>
                    </div>
                  ))}
                </div>
                <div className="payment">
                  <CheckCircle2 size={23} />
                  <div>
                    <strong>{stats.data.delivered} طلب تم تسليمه</strong>
                    <small>الدفع نقدًا عند الاستلام فقط</small>
                  </div>
                </div>
              </section>
            </div>
          </>
        )}
      </State>
    </>
  );
}
