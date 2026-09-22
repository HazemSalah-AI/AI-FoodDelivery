export class ApiError extends Error {
  constructor(
    public status: number,
    message: string,
  ) {
    super(message);
  }
}
const messages: Record<string, string> = {
  unauthenticated: "سجّل دخولك للمتابعة.",
  invalid_credentials: "البريد الإلكتروني أو كلمة المرور غير صحيحة.",
  forbidden: "هذه العملية غير متاحة لحسابك.",
  not_found: "العنصر غير موجود أو غير متاح لحسابك.",
  csrf_failed: "حدّث الصفحة ثم حاول مرة أخرى.",
  conflict: "البيانات مستخدمة من قبل أو تتعارض مع سجل موجود.",
  single_merchant: "السلة لمتجر واحد. أفرغ السلة الحالية أولًا.",
  stock_conflict: "المخزون اتغير. راجع الكميات في سلتك.",
  unavailable: "المنتج أو الكمية المطلوبة غير متاحة.",
  invalid_transition: "حالة الطلب اتغيرت؛ حدّث الصفحة وراجع الإجراء المتاح.",
  driver_unavailable: "السائق غير متاح أو لم يحدّث حالته مؤخرًا.",
  assignment_conflict: "السائق أو الطلب مرتبط بالفعل بتوصيلة نشطة.",
  rate_limited: "محاولات كثيرة. انتظر دقيقة ثم حاول مجددًا.",
  already_reviewed: "قيّمت الطلب ده بالفعل.",
  empty_cart: "أضف منتجات إلى سلتك أولًا.",
  merchant_closed: "المتجر مغلق حاليًا.",
  reason_required: "اكتب سبب رفض الطلب.",
  not_delivered: "التقييم متاح بعد تسليم الطلب.",
  active_delivery: "أكمل التوصيلة الحالية قبل إيقاف حساب السائق.",
};
export async function api<T>(
  path: string,
  method = "GET",
  body?: unknown,
): Promise<T> {
  const token = document.cookie
    .split("; ")
    .find((x) => x.startsWith("delivery_csrf="))
    ?.slice("delivery_csrf=".length);
  let response: Response;
  try {
    response = await fetch("/api/v1" + path, {
      method,
      credentials: "include",
      headers: {
        ...(body !== undefined ? { "Content-Type": "application/json" } : {}),
        ...(token ? { "X-CSRF-Token": decodeURIComponent(token) } : {}),
      },
      body: body === undefined ? undefined : JSON.stringify(body),
    });
  } catch {
    throw new Error("تعذّر الاتصال. تأكد أن الخادم يعمل وحاول مرة أخرى.");
  }
  if (response.status === 204) return undefined as T;
  const data = await response.json();
  if (!response.ok) {
    const error = data.error;
    throw new ApiError(
      response.status,
      messages[error?.code] ??
        (error?.code === "validation_error"
          ? "راجع البيانات المطلوبة: " +
            (error.fields ?? [])
              .map(
                (x: { field: string; message: string }) =>
                  x.field.replace("body.", "") + ": " + x.message,
              )
              .join("، ")
          : (error?.message ?? "تعذّر إتمام العملية.")),
    );
  }
  return data as T;
}
export const money = (value: string | number) =>
  new Intl.NumberFormat("ar-EG", { maximumFractionDigits: 2 }).format(
    Number(value),
  ) + " ج.م";
export const date = (value: string) =>
  new Date(value).toLocaleString("ar-EG", {
    day: "numeric",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
  });
export const statusName: Record<string, string> = {
  Pending: "في انتظار القبول",
  Accepted: "تم القبول",
  Preparing: "قيد التجهيز",
  Ready: "جاهز للاستلام",
  OnDelivery: "في الطريق",
  Delivered: "تم التسليم",
  Rejected: "مرفوض",
  Cancelled: "ملغي",
  Completed: "مكتمل",
};
