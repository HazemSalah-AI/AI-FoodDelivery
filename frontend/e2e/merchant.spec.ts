import { test, expect } from "@playwright/test";
test("merchant manages products and business availability", async ({
  page,
}) => {
  await page.goto("/#/login");
  await page.getByLabel("البريد الإلكتروني").fill("merchant@example.com");
  await page.getByLabel("كلمة المرور").fill(process.env.E2E_PASSWORD!);
  await page.getByRole("button", { name: "تسجيل الدخول", exact: true }).click();
  await expect(
    page.getByRole("heading", { name: "متجرك في نظرة" }),
  ).toBeVisible();
  await expect(page.getByText("إجمالي الطلبات", { exact: true })).toBeVisible();
  await page.screenshot({
    path: "test-results/merchant-desktop.png",
    fullPage: true,
  });
  await page
    .getByRole("button", { name: "إدارة المنتجات", exact: true })
    .click();
  await page.getByRole("button", { name: "إضافة منتج" }).click();
  await page
    .getByLabel("اسم المنتج", { exact: true })
    .fill("منتج اختبار المتجر");
  await page.getByLabel("السعر بالجنيه").fill("19.50");
  await page.getByLabel("الكمية المتاحة").fill("12");
  await page
    .getByRole("dialog")
    .getByRole("button", { name: "حفظ", exact: true })
    .click();
  const row = page.getByRole("row").filter({ hasText: "منتج اختبار المتجر" });
  await expect(row).toBeVisible();
  await row.getByRole("button", { name: "إخفاء", exact: true }).click();
  await expect(row.getByText("مخفي", { exact: true })).toBeVisible();
  await row.getByRole("button", { name: "إظهار", exact: true }).click();
  await page
    .getByRole("button", { name: "إعدادات المتجر", exact: true })
    .click();
  await page.getByLabel("المتجر مفتوح لاستقبال طلبات جديدة").uncheck();
  await page.getByRole("button", { name: "حفظ", exact: true }).click();
  await expect(
    page.getByText("المتجر مغلق حاليًا", { exact: true }),
  ).toBeVisible();
  await page.getByLabel("المتجر مفتوح لاستقبال طلبات جديدة").check();
  await page.getByRole("button", { name: "حفظ", exact: true }).click();
  await expect(
    page.getByText("المتجر يستقبل الطلبات", { exact: true }),
  ).toBeVisible();
});
