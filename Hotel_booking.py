import re
import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')


def get_grand_total(text):
    amounts = re.findall(r'₹[\s]*([\d,]+)', text)
    amounts = [int(amount.replace(',', '')) for amount in amounts]
    if len(amounts) >= 3:
        return amounts[2]
    return None


def setup_driver():
    options = Options()
    prefs = {
        "profile.default_content_setting_values.notifications": 2,
        "profile.default_content_setting_values.geolocation": 1
    }
    options.add_experimental_option("prefs", prefs)
    driver = webdriver.Chrome(options=options)
    driver.maximize_window()
    return driver


def wait_and_click(driver, by, value):
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((by, value))).click()


def apply_coupon(driver, code):
    wait_and_click(driver, By.XPATH, "(//span[@class='cpncd_lnk fontt-13 rmv_text ng-star-inserted'])[1]")
    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.XPATH, "//input[@placeholder='Enter promo code']"))).send_keys(code)
    wait_and_click(driver, By.XPATH, "(//span[@class='cpncd_lnk text_bl fontt-13 ng-star-inserted'])[1]")


def main():
    driver = setup_driver()
    wait = WebDriverWait(driver, 10)

    try:
        logging.info("Navigating to EaseMyTrip...")
        driver.get("https://www.easemytrip.com/")
        wait_and_click(driver, By.XPATH, "//a[@href='/hotels/']")

        # Select City
        wait_and_click(driver, By.XPATH, "//div[@class='hp_inputBox selectHtlCity']")
        city_input = wait.until(EC.presence_of_element_located((By.ID, "txtCity")))
        city_input.send_keys("New York, United States Of America")

        # Select Dates
        wait_and_click(driver, By.XPATH, "(//div[@class='hp_inputBox ht-dates'])[1]")
        wait_and_click(driver, By.XPATH, "//a[text()='18']")  # Use dynamic date logic if needed
        wait_and_click(driver, By.XPATH, "(//div[@class='hp_inputBox ht-dates'])[2]")
        wait_and_click(driver, By.XPATH, "//a[text()='25']")

        wait_and_click(driver, By.ID, "btnSearch")

        # View rooms and switch tab
        wait_and_click(driver, By.XPATH, "(//div[@class='viewBtn'][normalize-space()='View Rooms'])[1]")
        tabs = driver.window_handles
        driver.switch_to.window(tabs[1])

        wait_and_click(driver, By.XPATH, "(//a[@class='fill-btn ng-tns-c3739152123-2'])[1]")
        # Price before applying coupon
        price_before_elem = wait.until(EC.presence_of_element_located(
            (By.XPATH, "(//div[@class='hotelRvw_box3 ng-tns-c2179837240-4 ng-star-inserted'])[1]")))
        before_price = get_grand_total(price_before_elem.text)
        logging.info(f"Price before applying coupon: ₹{before_price}")

        # Apply coupon
        apply_coupon(driver, "SUMMER25")
        time.sleep(3)  # allow coupon to apply

        price_after_elem = driver.find_element(By.XPATH,
                                               "(//div[@class='hotelRvw_box3 ng-tns-c2179837240-4 ng-star-inserted'])[1]")
        after_price = get_grand_total(price_after_elem.text)
        logging.info(f"Price after applying coupon: ₹{after_price}")

        # Validate discount
        expected_price = round(before_price * 0.75)
        if abs(after_price - expected_price) <= 2:
            logging.info("✅ 25% discount applied successfully.")
        else:
            logging.warning(f"❌ Discount not applied as expected. Expected: ₹{expected_price}, Got: ₹{after_price}")

        logging.info("Script completed. Closing browser in 10 seconds...")
        time.sleep(10)

    except Exception as e:
        logging.error(f"❌ An error occurred: {e}")

    finally:
        driver.quit()


if __name__ == "__main__":
    main()
