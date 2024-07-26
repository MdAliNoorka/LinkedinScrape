import time
from selenium.webdriver.common.by import By
import csv
from parseurl import construct_url
from initdriver import get_driver

title = "Web Developer"
location = "Canada"

size = 5

url = construct_url(title,location)
print("preparing browser")
driver = get_driver()
driver.get(url)
time.sleep(10)
l = 0
companies = {"name":[],"link":[]}
while 1:
    ul_element = driver.find_element(By.CLASS_NAME, 'jobs-search__results-list')
    li_elements = ul_element.find_elements(By.TAG_NAME, 'li')
    li_eles = li_elements[l:]
    if l==len(li_elements):
        break
    for li in li_eles:
        try:
            if len(companies["name"]) == size:
                break
            l += 1
            driver.execute_script("arguments[0].scrollIntoView();", li)
            driver.execute_script("arguments[0].click()",li.find_element(By.CLASS_NAME,"base-search-card__info"))
            time.sleep(3.5)
            company_link = driver.find_elements(By.CLASS_NAME,"topcard__flavor-row")[0].find_element(By.TAG_NAME,"a").get_attribute("href")
            company_name = driver.find_elements(By.CLASS_NAME,"topcard__flavor-row")[0].find_element(By.TAG_NAME,"a").text
            companies["name"].append(company_name)
            companies["link"].append(company_link)
            print(company_name)
        except:
            continue
    print(companies)
    print(len(companies["name"]))
    if len(companies["name"]) == size:
        break
    button = driver.find_elements(By.XPATH, "//*[self::div or self::button or self::span][contains(text(), 'See more jobs')]")
    if len(button) != 0:
        driver.execute_script("arguments[0].click();", button[0])
        time.sleep(1)

    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(4)

unique_data = {}
for name, link in zip(companies['name'], companies['link']):
    if name not in unique_data:
        unique_data[name] = link

# Writing data to CSV
with open('companies_unique.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)

    # Writing headers
    writer.writerow(['', 'Company Name', 'Company Linkedin Link'])

    # Writing data
    for i, ( name, link) in enumerate(unique_data.items(), start=2):
        writer.writerow([f'Company{i - 1}:', name, link])


driver.quit()