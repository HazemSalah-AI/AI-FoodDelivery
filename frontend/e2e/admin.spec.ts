import { test, expect } from "@playwright/test";
test("admin creates and suspends a driver and adds a delivery area", async ({
  page,
}) => {
  await page.goto("/#/login");
  await page.getByLabel("البريد الإلكتروني").fill("admin@example.com");
  await page.getByLabel("كلمة المرور").fill(process.env.E2E_PASSWORD!);
  await page.getByRole("button", { name: "تسجيل الدخول", exact: true }).click();
  await page
    .getByRole("button", { name: "إدارة الحسابات", exact: true })
    .click();
  await page.getByRole("button", { name: "إنشاء حساب", exact: true }).click();
  const dialog = page.getByRole("dialog");
  await dialog.getByLabel("الاسم", { exact: true }).fill("سائق اختبار الإدارة");
  await dialog
    .getByLabel("البريد الإلكتروني")
    .fill("admin-created-driver@example.com");
  await dialog.getByLabel("رقم الموبايل").fill("01090000000");
  await dialog.getByLabel("كلمة المرور").fill(process.env.E2E_PASSWORD!);
  await dialog
    .getByRole("button", { name: "إنشاء الحساب", exact: true })
    .click();
  await expect(dialog).toHaveCount(0);
  const row = page.getByRole("row").filter({ hasText: "سائق اختبار الإدارة" });
  await expect(row).toBeVisible();
  await row.getByRole("button", { name: "إيقاف الحساب" }).click();
  await expect(row.getByText("موقوف", { exact: true })).toBeVisible();
  await page
    .getByRole("button", { name: "المدن والمناطق", exact: true })
    .click();
  await page.getByRole("button", { name: "إضافة منطقة", exact: true }).click();
  await dialog.getByLabel("المدينة").selectOption({ label: "أبو حماد" });
  await dialog
    .getByLabel("الاسم", { exact: true })
    .fill("منطقة اختبار الإدارة");
  await dialog.getByRole("button", { name: "حفظ", exact: true }).click();
  await expect(
    page.getByText("منطقة اختبار الإدارة", { exact: true }),
  ).toBeVisible();
});
