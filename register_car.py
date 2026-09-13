from playwright.sync_api import sync_playwright
from local_config import GUEST_PARKING_URL


def register_car(plate, email):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(GUEST_PARKING_URL)

        plate_input = page.locator("input[placeholder*='license plate']")
        plate_input.fill(plate)

        email_input = page.locator("input[placeholder*='E-mail']")
        email_input.fill(email)

        checkbox = page.locator("input[type='checkbox']")
        checkbox.check()

        page.get_by_role("button", name="FORTSÆT").click()

        confirm_button = page.get_by_role("button", name="CONFIRM AND CREATE")
        confirm_button.wait_for(state="visible", timeout=10000)
        confirm_button.click()

        page.get_by_text("parking permit has been created").wait_for(state="visible", timeout=10000)

        browser.close()
        return True


if __name__ == "__main__":
    success = register_car("EC68539", "runen8800@gmail.com")
    print("Success:", success)
