from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random
from selenium.webdriver.chrome.options import Options
chrome_options = Options()
chrome_options.add_experimental_option("detach", True)



def parsing_avito(prices,area, pages):
#prices - диапазон цен в формате [a, b], где b > a
#are - диапазон площади квартиры [c, d], где d > c
#pages - количество страниц для парсинга

    driver = webdriver.Chrome(options=chrome_options)
    driver.get("https://www.avito.ru/moskva/nedvizhimost")

    #ждём пока прогрузится сайт и кнопка станет кликабельной
    button = WebDriverWait(driver, 120).until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, "div.buyer-location-b488yl > button[type='button']")
                )
            )
    button.click()#нажимаем на кнопку "все фильтры"
    time.sleep(3)

    #записываем наш диапазон цен в соответствующие ячейки
    price_from = driver.find_element(By.CSS_SELECTOR, "input[marker='price-from'][autocomplete='off']")


    for char in str(prices[0]):
                price_from.send_keys(char)
                time.sleep(random.uniform(0.05, 0.2)) #ну это мне гпт подсказал, честно
    #до такого я бы не додумался...
    time.sleep(1.5)
    price_to = driver.find_element(By.CSS_SELECTOR, "input[marker='price-to'][autocomplete='off']")

    for char in str(prices[1]):
                price_to.send_keys(char)
                time.sleep(random.uniform(0.05, 0.2))

    #повторяем аналогично с диапазоном для площади

    area_from = driver.find_element(By.CSS_SELECTOR, "input[marker='params[578]-from']")
    area_to = driver.find_element(By.CSS_SELECTOR, "input[marker='params[578]-to']")

    for char in str(area[0]):
                area_from.send_keys(char)
                time.sleep(random.uniform(0.05, 0.2))

    time.sleep(1.5)

    for char in str(area[1]):
                area_to.send_keys(char)
                time.sleep(random.uniform(0.05, 0.2))

    #теперь надо отметить галочкой чекбокс с балконом
    checkbox_label = driver.find_element(By.XPATH, "//label[contains(@data-marker, 'params[118593]/checkbox')]")#тут тоже гпт немного помог
    # а то я что-то запутался, где рабочая область этого checkbox в html
    checkbox_label.click()

    #теперь осталось кликнуть на кнопку "показать объявления"

    button_finale = driver.find_element(By.CSS_SELECTOR, "div.styles-module-margin-top_none-P0ihW > "
                "button.styles-module-root_preset_accent-CsGuH") #здесь мы сделали специальный селектор по структуре html-кода

    time.sleep(1)
    button_finale.click()
    #наконец нам вывелись все квартиры, подходящие по всем параметрам
    #теперь хотим получить список всех адресов этих квартир, чтобы потом из них вытащить координаты


    current_page = 1
    addresses = []

    while current_page <= pages:
        #Ждём, пока всё прогрузится и потом находим все контейнеры с объявлениями
        items = WebDriverWait(driver, 15).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div[data-marker="item"]')))

        #извлекаем адрес для каждого объявления
        for item in items:
            try:
                # взглянув на html-код, напишем следующие селекторы
                street = item.find_element(By.CSS_SELECTOR, '[data-marker="street_link"]').text.strip()
                house = item.find_element(By.CSS_SELECTOR, '[data-marker="house_link"]').text.strip()
                addresses.append(f"{street}, {house}")
            except:
                continue
        #конструкция try-except позволяет программе работать даже в случае, если данные не нашлись

        if current_page < pages:
            try:
                next_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, 'a[data-marker="pagination-button/nextPage"]'))
                )
                driver.execute_script("arguments[0].scrollIntoView();", next_button)
                next_button.click()
                #подождём пока объявления прогрузятся
                WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-marker="item"]'))
                )
                time.sleep(1)
            except:
                break

        current_page += 1

    return addresses

#рассмотрим как пример все квартиры с балконом, стоимостью от 10млн до 30 млн и площадью от 60м^2 до 150м^2
adresses_res = parsing_avito([10000000,30000000], [60,150],20)

print(len(adresses_res))
print(adresses_res)
#удаляем все дубликаты
adresses_res = list(set(adresses_res))
print(len(adresses_res))
print(adresses_res)