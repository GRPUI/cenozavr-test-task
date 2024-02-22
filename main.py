import time
from typing import Dict

import undetected_chromedriver as webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import ElementClickInterceptedException


def get_products(driver: webdriver.Chrome, city: str, address: str) -> Dict:
    driver.get("https://www.okeydostavka.ru/")
    address_button = driver.find_element(
        By.CSS_SELECTOR,
        """#availableReceiptTimeLink"""
    )
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
        driver.quit()
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

    driver.implicitly_wait(1)
    address_style = driver.find_element(
        By.XPATH,
        """//*[@id="storeSelectionWrapper"]"""
    ).get_attribute("style")

    if "display: none" not in address_style:
        driver.quit()
        return {"error": f"Адрес {address} не найден или не обслуживается"}

    print("1")
    time.sleep(100)

    driver.quit()


if __name__ == "__main__":
    get_products(webdriver.Chrome(), "Новосибирск", "Плахотного 10")
