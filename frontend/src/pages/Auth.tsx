import { ArrowUpRight, MapPin, ShoppingBag, Truck } from "lucide-react";
import { api } from "../api";
import { Field, Form, val } from "../components/ui";
import type { User } from "../types";
export function Auth({
  register,
  onUser,
  navigate,
}: {
  register: boolean;
  onUser: (user: User) => void;
  navigate: (path: string) => void;
}) {
  return (
    <div className="auth-layout">
      <div className="auth-story">
        <div className="brand-mark">
          <Truck size={28} />
        </div>
        <div className="eyebrow">من أهل البلد… لأهل البلد</div>
        <h1>
          طلباتك أقرب
          <br />
          مما تتخيّل.
        </h1>
        <p>
          متاجر أبو حماد في مكان واحد.
          <br />
          اطلب بسهولة وادفع عند الاستلام.
        </p>
        <div className="auth-art">
          <ShoppingBag size={100} />
          <MapPin size={40} />
          <span>أبو حماد</span>
        </div>
        <button className="light" onClick={() => navigate("browse")}>
          تصفّح المتاجر <ArrowUpRight size={18} />
        </button>
      </div>
      <div className="auth-form">
        <div className="eyebrow">أهلًا بيك في وصلة</div>
        <h2>{register ? "اعمل حسابك" : "سجّل دخولك"}</h2>
        <p>
          {register
            ? "خطوة بسيطة وطلباتك هتوصلك لحد الباب."
            : "تابع طلباتك وكل جديد في مكان واحد."}
        </p>
        <Form
          submit={register ? "إنشاء الحساب" : "تسجيل الدخول"}
          onSubmit={async (data) => {
            const email = val(data, "email"),
              password = val(data, "password");
            if (register)
              await api("/auth/register", "POST", {
                email,
                password,
                name: val(data, "name"),
                phone: val(data, "phone"),
              });
            const result = await api<{ user: User }>("/auth/login", "POST", {
              email,
              password,
            });
            onUser(result.user);
            navigate(result.user.role === "Customer" ? "browse" : "dashboard");
          }}
        >
          {register && (
            <>
              <Field label="اسمك">
                <input
                  name="name"
                  required
                  minLength={2}
                  maxLength={100}
                  autoComplete="name"
                />
              </Field>
              <Field label="رقم الموبايل">
                <input
                  name="phone"
                  type="tel"
                  required
                  pattern="\+?[0-9]{10,15}"
                  autoComplete="tel"
                  dir="ltr"
                />
              </Field>
            </>
          )}
          <Field label="البريد الإلكتروني">
            <input
              name="email"
              type="email"
              required
              autoComplete="email"
              dir="ltr"
              placeholder="you@example.com"
            />
          </Field>
          <Field label="كلمة المرور">
            <input
              name="password"
              type="password"
              required
              minLength={register ? 12 : 1}
              maxLength={128}
              autoComplete={register ? "new-password" : "current-password"}
              dir="ltr"
            />
          </Field>
          {register && (
            <small>
              12 حرفًا على الأقل. حسابات المتاجر والسائقين ينشئها المدير.
            </small>
          )}
        </Form>
        <div className="auth-switch">
          {register ? "عندك حساب بالفعل؟" : "لسه معندكش حساب؟"}{" "}
          <button
            className="text-button"
            onClick={() => navigate(register ? "login" : "register")}
          >
            {register ? "سجّل دخولك" : "إنشاء حساب"}
          </button>
        </div>
      </div>
    </div>
  );
}
