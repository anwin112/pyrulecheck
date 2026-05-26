import { test, expect } from '@playwright/test';

test('Login with Invalid Credentials', async ({ page }) => {

  // 1️⃣ Navigate to Login Page
  await page.goto('https://opensource-demo.orangehrmlive.com/');

  // 2️⃣ Enter Invalid Username
  await page.fill('input[name="username"]', 'WrongUser');

  // 3️⃣ Enter Invalid Password
  await page.fill('input[name="password"]', 'WrongPass123');

  // 4️⃣ Click Login
  await page.click('button[type="submit"]');

  // 5️⃣ Validate Invalid Credentials Message
  const errorMessage = page.locator('.oxd-alert-content-text');

  await expect(errorMessage).toBeVisible();
  await expect(errorMessage).toContainText('Invalid credentials');

});
