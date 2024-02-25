import os
import random
import string
import time
from typing import Dict

import selenium
import undetected_chromedriver as webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import ElementClickInterceptedException, TimeoutException, NoSuchElementException
from selenium_stealth import stealth
from selenium.webdriver.common.proxy import Proxy, ProxyType
import dotenv

import save_to_xlsx


def get_categories(element: webdriver.WebElement) -> Dict:
    categories = element.find_elements(
        By.XPATH,
        """.//*"""
    )
    categories = {category.text: category.get_attribute("href") for category in categories if category.text != ""}
    return categories


def get_product_info(element: webdriver.WebElement, category: str) -> Dict:
    text = element.text.split("\n")
    try:
        image = element.find_element(
            By.CLASS_NAME,
            """lazyloaded"""
        ).get_attribute("src")
    except NoSuchElementException:
        image = None

    link = element.find_element(
        By.CLASS_NAME,
        "image"
    ).find_element(
        By.XPATH,
        ".//*"
    ).get_attribute("href")

    prices = [price for price in text if price.endswith("₽")]
    name = " ".join(text[0].split(" ")[:-1])
    price_with_discount = None
    price = prices[0]
    if len(prices) == 2:
        price_with_discount = prices[1]

    return {"category": category, "link": link,
            "name": name, "image": image,
            "price": price, "price_with_discount": price_with_discount}


def get_products(driver: webdriver.Chrome, city: str, address: str) -> Dict:
    driver.get("https://www.okeydostavka.ru/")
    try:
        address_button = driver.find_element(
            By.CSS_SELECTOR,
            """#availableReceiptTimeLink"""
        )
    except NoSuchElementException:
        driver.save_screenshot("screenshot.png")
        return {"error": "Не удалось загрузить страницу"}
    while True:
        try:
            address_button.click()
        except ElementClickInterceptedException:
            break

    city_button = driver.find_element(
        By.XPATH,
        """//*[@id="storeSelectionCity"]/tbody/tr/td[1]/div[1]/span"""
    )
    city_button.click()

    WebDriverWait(driver, 120).until(
        lambda d: d.find_element(
            By.XPATH,
            """//*[@id="storeSelectionCity_menu"]/table/tbody"""
        )
    )
    city_list = driver.find_element(
        By.XPATH,
        """//*[@id="storeSelectionCity_menu"]/table/tbody"""
    ).find_elements(
        By.XPATH,
        ".//*"
    )

    cities = [city_.text for city_ in city_list if city_.text != ""]

    if city not in cities:
        return {"error": f"Город {city} не найден"}

    for city_ in city_list:
        if city_.text == city:
            city_.click()
            break

    address_input = driver.find_element(
        By.XPATH,
        """//*[@id="addressSelectionQuery"]"""
    )
    address_input.send_keys(address)

    driver.implicitly_wait(1)
    submit_button = driver.find_element(
        By.XPATH,
        """//*[@id="addressSelectionButton"]"""
    )

    cookie_button = driver.find_element(
        By.XPATH,
        """//*[@id="cookie_alert"]/div/div[2]/button"""
    )
    cookie_button.click()

    submit_button.click()

    WebDriverWait(driver, 60).until(
        lambda d: d.find_element(
            By.XPATH,
            """//*[@id="addressSelectionQuery_popup"]"""
        )
    )
    address_choose_list = driver.find_element(
        By.XPATH,
        """//*[@id="addressSelectionQuery_popup"]"""
    ).find_elements(
        By.XPATH,
        ".//*"
    )

    for address_ in address_choose_list:
        if city in address_.text:
            address_.click()

    submit_button.click()

    time.sleep(5)
    address_style = driver.find_element(
        By.XPATH,
        """//*[@id="storeSelectionWrapper"]"""
    ).get_attribute("style")

    if "display: none" not in address_style:
        return {"error": f"Адрес {address} не найден или не обслуживается"}

    try:
        WebDriverWait(driver, 60).until(
            lambda d: d.find_element(
                By.XPATH,
                """//*[@id="availableReceiptTimeLink"]/div[1]"""
            )
        )
    except TimeoutException:
        return {"error": "Не удалось загрузить страницу"}

    catalog_button = driver.find_element(
        By.XPATH,
        """//*[@id="allDepartmentsButton"]"""
    )
    catalog_button.click()

    catalog = driver.find_element(
        By.XPATH,
        """//*[@id="content"]/div[1]/div/div[2]/div"""
    )
    product_categories = get_categories(catalog)
    products_list = []
    for category_ in ["Своя пекарня", "President", "Готовая кулинария"]:
        driver.get(product_categories[category_])
        products = driver.find_element(
            By.ID,
            """dijit__WidgetBase_0"""
        ).find_elements(
            By.XPATH,
            """.//*"""
        )

        category = driver.find_element(
            By.XPATH,
            """//*[@id="PageHeading_4_-1001_3074457345618259710"]/h1"""
        ).text

        products_text_list = set([product for product in products
                                  if len(product.text.split("\n")) > 3 and product.text[0] not in string.digits])
        products_list += [get_product_info(product, category) for product in products_text_list]
    save_to_xlsx.save_to_xlsx(products_list, "products.xlsx")


if __name__ == "__main__":
    options = webdriver.ChromeOptions()
    proxy = Proxy()
    proxy.proxyType = ProxyType.MANUAL
    dotenv.load_dotenv()
    proxy_address = os.getenv("PROXY_ADDRESS")
    proxy.http_proxy = proxy_address
    options.add_argument("--headless")
    capabilities = selenium.webdriver.DesiredCapabilities.CHROME

    driver = webdriver.Chrome(options=options, desired_capabilities=capabilities)
    stealth(driver,
            languages=["en-US", "ru-RU"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True)
    get_products(driver, "Новосибирск", "Военная 9")
    driver.delete_all_cookies()
    driver.quit()
