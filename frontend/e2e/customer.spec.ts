import { test, expect } from "@playwright/test";
test("customer can sign in, browse, checkout and cancel pending order", async ({
  page,
}) => {
  await page.goto("/");
  await expect(
    page.getByRole("heading", { name: "متاجر قريبة منك" }),
  ).toBeVisible();
  await page.getByRole("button", { name: "تسجيل الدخول", exact: true }).click();
  await page.getByLabel("البريد الإلكتروني").fill("customer@example.com");
  await page.getByLabel("كلمة المرور").fill(process.env.E2E_PASSWORD!);
  await page.getByRole("button", { name: "تسجيل الدخول", exact: true }).click();
  await expect(
    page.getByRole("heading", { name: "متاجر قريبة منك" }),
  ).toBeVisible();
  await page.getByRole("button", { name: "أضف أرز مصري — كيلو للسلة" }).click();
  await page.getByRole("button", { name: /سلة المشتريات/ }).click();
  await expect(
    page.getByRole("heading", { name: "سلة المشتريات" }),
  ).toBeVisible();
  await page.getByRole("button", { name: "تأكيد الطلب", exact: true }).click();
  await expect(
    page.getByRole("heading", { name: /تفاصيل الطلب #/ }),
  ).toBeVisible();
  await expect(
    page.getByText("في انتظار القبول", { exact: true }).first(),
  ).toBeVisible();
  await page.getByRole("button", { name: "إلغاء الطلب", exact: true }).click();
  await page
    .getByRole("button", { name: "تأكيد الإلغاء", exact: true })
    .click();
  await expect(
    page.locator(".badge").filter({ hasText: "ملغي" }),
  ).toBeVisible();
  await page.setViewportSize({ width: 390, height: 844 });
  await page.getByRole("button", { name: "فتح القائمة" }).click();
  await page.getByRole("button", { name: "اكتشف المتاجر" }).click();
  await expect(
    page.getByRole("heading", { name: "متاجر قريبة منك" }),
  ).toBeVisible();
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= window.innerWidth,
    ),
  ).toBeTruthy();
  await page.context().clearCookies();
  await page.getByRole("button", { name: "فتح القائمة" }).click();
  await page.getByRole("button", { name: /سلة المشتريات/ }).click();
  await expect(page.getByLabel("كلمة المرور")).toBeVisible();
});
