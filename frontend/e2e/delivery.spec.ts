import { test, expect, type Page } from "@playwright/test";

async function login(page: Page, email: string) {
  await page.goto("/#/login");
  await page.getByLabel("البريد الإلكتروني").fill(email);
  await page.getByLabel("كلمة المرور").fill(process.env.E2E_PASSWORD!);
  await page.getByRole("button", { name: "تسجيل الدخول", exact: true }).click();
  await expect(
    page.getByRole("button", { name: "تسجيل الخروج" }),
  ).toBeVisible();
}
async function openOrder(page: Page, path: string) {
  await page.goto(path);
  await page.reload();
  await expect(
    page.getByRole("heading", { name: /تفاصيل الطلب #/ }),
  ).toBeVisible();
}

test("four roles complete delivery after driver rejection and reassignment", async ({
  browser,
}) => {
  const contexts = await Promise.all(
    Array.from({ length: 5 }, () =>
      browser.newContext({
        geolocation: { latitude: 30.5391, longitude: 31.6802 },
        permissions: ["geolocation"],
      }),
    ),
  );
  try {
    const [customer, merchant, admin, first, second] = await Promise.all(
      contexts.map((c) => c.newPage()),
    );
    for (const [page, email] of [
      [customer, "customer@example.com"],
      [merchant, "merchant@example.com"],
      [admin, "admin@example.com"],
      [first, "driver@example.com"],
      [second, "driver2@example.com"],
    ] as [Page, string][])
      await login(page, email);
    await customer
      .getByRole("button", { name: "أضف أرز مصري — كيلو للسلة" })
      .click();
    await customer.getByRole("button", { name: /سلة المشتريات/ }).click();
    await customer
      .getByRole("button", { name: "تأكيد الطلب", exact: true })
      .click();
    await expect(
      customer.getByRole("heading", { name: /تفاصيل الطلب #/ }),
    ).toBeVisible();
    const orderPath = new URL(customer.url()).hash;
    await openOrder(merchant, "/" + orderPath);
    await merchant
      .getByRole("button", { name: "قبول الطلب", exact: true })
      .click();
    await expect(
      merchant.getByRole("button", { name: "بدء التجهيز" }),
    ).toBeVisible();
    await customer.reload();
    await expect(
      customer.locator(".badge").filter({ hasText: "تم القبول" }),
    ).toBeVisible();
    await expect(
      customer.getByRole("button", { name: "إلغاء الطلب", exact: true }),
    ).toHaveCount(0);
    await merchant.getByRole("button", { name: "بدء التجهيز" }).click();
    await merchant
      .getByRole("button", { name: "جاهز للاستلام", exact: true })
      .click();
    for (const driver of [first, second]) {
      await driver.getByRole("button", { name: "تفعيل التوفر" }).click();
      await expect(
        driver.getByRole("button", { name: "إيقاف التوفر" }),
      ).toBeVisible();
    }
    await first
      .getByRole("button", { name: "مشاركة الموقع مع المدير" })
      .click();
    await expect(first.getByRole("status")).toHaveText(
      "موقعك بيتحدث للمدير فقط.",
    );
    await openOrder(admin, "/" + orderPath);
    await admin
      .getByRole("button", { name: "تعيين سائق", exact: true })
      .click();
    await admin
      .getByLabel("السائق المتاح")
      .selectOption({ label: "علي — التوصيل" });
    await admin
      .getByRole("button", { name: "تعيين السائق", exact: true })
      .click();
    await expect(admin.getByRole("dialog")).toHaveCount(0);
    await openOrder(first, "/" + orderPath);
    await first
      .getByRole("button", { name: "رفض التوصيلة", exact: true })
      .click();
    await expect(
      first.getByRole("button", { name: "رفض التوصيلة", exact: true }),
    ).toHaveCount(0);
    await admin.reload();
    await admin
      .getByRole("button", { name: "تعيين سائق", exact: true })
      .click();
    await admin
      .getByLabel("السائق المتاح")
      .selectOption({ label: "محمد — التوصيل" });
    await admin
      .getByRole("button", { name: "تعيين السائق", exact: true })
      .click();
    await expect(admin.getByRole("dialog")).toHaveCount(0);
    await openOrder(second, "/" + orderPath);
    await second
      .getByRole("button", { name: "قبول التوصيلة", exact: true })
      .click();
    await second
      .getByRole("button", { name: "تم استلام الطلب", exact: true })
      .click();
    await second
      .getByRole("button", { name: "تأكيد التسليم وتحصيل الكاش", exact: true })
      .click();
    await expect(
      second.locator(".badge").filter({ hasText: "تم التسليم" }),
    ).toBeVisible();
    await customer.reload();
    await expect(
      customer.locator(".badge").filter({ hasText: "تم التسليم" }),
    ).toBeVisible();
    await expect(customer.locator("iframe")).toHaveCount(0);
    await expect(customer.getByText("30.5391", { exact: false })).toHaveCount(
      0,
    );
    await customer.getByRole("button", { name: "تقييم المتجر" }).click();
    await customer.getByLabel("رأيك في المتجر").fill("توصيل ممتاز");
    await customer
      .getByRole("dialog")
      .getByRole("button", { name: "حفظ", exact: true })
      .click();
    await expect(customer.getByRole("dialog")).toHaveCount(0);
    await admin
      .getByRole("button", { name: "السائقون والمواقع", exact: true })
      .click();
    await admin
      .locator(".list-row")
      .filter({ hasText: "علي — التوصيل" })
      .getByRole("button", { name: "عرض الموقع" })
      .click();
    await expect(
      admin.getByTitle("آخر موقع للسائق علي — التوصيل"),
    ).toHaveAttribute("src", /marker=30.5391,31.6802/);
    await admin.screenshot({
      path: "test-results/admin-drivers.png",
      fullPage: true,
    });
    await second.setViewportSize({ width: 390, height: 844 });
    expect(
      await second.evaluate(
        () => document.documentElement.scrollWidth <= innerWidth,
      ),
    ).toBeTruthy();
  } finally {
    await Promise.all(contexts.map((c) => c.close()));
  }
});
