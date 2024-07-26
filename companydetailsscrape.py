import time
from datetime import datetime, timedelta
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from initdriver import get_driver
import pandas as pd
from parseurl import remove_url_parameters, originalSubdomain
max_members = 2
# Load data
data = pd.read_csv("companies_unique.csv")
urls = data["Company Linkedin Link"]

# Set cookie expiration
expiry_date = datetime.now() + timedelta(days=60)
expiry_timestamp = int(time.mktime(expiry_date.timetuple()))

# li_at cookie value
value = "AQEDATz8-pUBo_9IAAABkFRFCNgAAAGQ8m_Kw1YALCWkbQvrnNPS4cn6DGV1Xe0Me7S_IUltfMBFSQuKR0Jwq2Cj6PoxpgjihHUxjTEM2TYorUbVZcDX8gZ3gB80NetVwL3_nC4p4bn2OZ0Ml8gffKoo"
# Initialize driver
driver = get_driver()
driver.get("https://www.linkedin.com/")

# Add cookie
li_at_cookie = {
    'name': 'li_at',
    'value': value,
    'domain': '.linkedin.com',
    'expiry': expiry_timestamp,
    'path': '/',
    'secure': True,
    'httpOnly': True
}

driver.add_cookie(li_at_cookie)
driver.refresh()

# Initialize lists
webs = []
talent_roles = ['hr']
talent_urls = []
# Iterate through URLs
for url in urls:
    url = remove_url_parameters(url)
    url_about = url + "/about"
    driver.execute_script(f"window.location.href='{url_about}'")
    print(f"Scraping: {url}")
    # Wait for the element to be present
    try:
        web_element = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "dd a span"))
        )
        web = web_element.text
    except Exception as e:
        web = ""
        talent_urls.append([])
        webs.append(web)
        print(f"Error1: {e}")
        continue
    time.sleep(1)
    url_people = url+"/people?keywords=talent"
    url_people = originalSubdomain(url_people)
    driver.execute_script(f"window.location.href='{url_people}'")
    links = []
    time.sleep(4)
    if "talent" not in driver.current_url:
        try:
            value = "Search employees by title, keyword or school"
            input = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located(
                    (By.XPATH, f"//input[@placeholder='{value}']")
)
            )
            driver.execute_script("arguments[0].scrollIntoView()", input)
            time.sleep(1)
            input.send_keys("talent")
            time.sleep(1)
            input.send_keys(Keys.ENTER)
            value = "Keyword search already applied"
            web_element = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located(
                    (By.XPATH, f"//input[@placeholder='{value}']")
)
            )
        except Exception as e:
            talent_urls.append([])
            webs.append(web)
            print(e)
            continue
    try:
        web_element = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "li.grid.grid__col--lg-8.block.org-people-profile-card__profile-card-spacing"))
        )
    except Exception as e:
        print("No members found")
        talent_urls.append(links)
        webs.append(web)
        continue
    li = 0
    while 1:
        if li >= max_members:
            print(f'members extracted: {li}')
            break
        time.sleep(2)
        cards = driver.find_elements(By.CSS_SELECTOR,"li.grid.grid__col--lg-8.block.org-people-profile-card__profile-card-spacing")
        new_cards = cards[li:]
        if li == len(cards):
            break
        for card in new_cards:
            if li >= max_members:
                print(f'members extracteds: {li}')
                break
            li+=1
            driver.execute_script("arguments[0].scrollIntoView()",card)
            time.sleep(0.1),
            try:
                role = card.find_element(By.CSS_SELECTOR,"div.ember-view.lt-line-clamp.lt-line-clamp--multi-line")
            except:
                continue
            try:
                link = card.find_element(By.TAG_NAME,"a").get_attribute("href")
            except:
                continue
            if "talent" in role.text.lower():
                print(link)
                links.append(link)
        button = driver.find_elements(By.XPATH,
                                      "//*[self::div or self::button or self::span][contains(text(), 'See more')]")
        if len(button) != 0:
            driver.execute_script("arguments[0].click();", button[0])
            time.sleep(1)
    talent_urls.append(links)
    webs.append(web)






# Read the CSV file
df = pd.read_csv("companies_unique.csv")

# Add the 'Website Link' column
df['Website Link'] = pd.Series(webs)


# Define the output CSV file path
output_csv_file_path = 'companies_unique.csv'

# Find the maximum length of sublists in talent_roles
max_len = max(len(sublist) if isinstance(sublist, list) else 1 for sublist in talent_urls)

# Pad the sublists in talent_roles to ensure they all have the same length
padded_talent_urls = [sublist if isinstance(sublist, list) else [sublist] for sublist in talent_urls]
padded_talent_urls = [sublist + [None] * (max_len - len(sublist)) for sublist in padded_talent_urls]

# Print debugging information
print(f'talent roles: {talent_urls}')
print(f'padded talent roles: {padded_talent_urls}')
print(f'max len: {max_len}')

# Define the column names
column_names = [f'Column {i+4}' for i in range(max_len)]
print(f'column_names: {column_names}')

# Creating the new DataFrame with additional column
new_df = pd.DataFrame(columns=df.columns.tolist() + ["person's linkedin url"])

for i in range(len(df)):
    row = df.iloc[i].to_dict()  # Convert the row to a dictionary
    for j in range(len(padded_talent_urls[i])):
        row_copy = row.copy()  # Make a copy of the row dictionary
        row_copy["person's linkedin url"] = padded_talent_urls[i][j]
        new_df = new_df._append(row_copy, ignore_index=True)
        print(f"row_copy: {row_copy}")
        print(f"new df: {new_df}")
    if len(padded_talent_urls[i]) == 0:
        row["person's linkedin url"] = None
        new_df = new_df._append(row, ignore_index=True)

new_df.to_csv(output_csv_file_path, index=False)

#
# # Create a DataFrame from the padded talent roles
# talent_urls_df = pd.DataFrame(padded_talent_urls, columns=column_names)
#
# # Concatenate the original DataFrame with the new DataFrame
# df = pd.concat([df, talent_urls_df], axis=1)
#
# # Write the updated DataFrame to the CSV file
# df.to_csv(output_csv_file_path, index=False)
#





#
# # Save results to CSV
# df = pd.read_csv("companies_unique.csv")
# df['Website Link'] = pd.Series(webs)
# output_csv_file_path = 'companies_unique.csv'
# max_len = max(len(sublist) for sublist in talent_roles)
#
# column_names = [f'Column {i+4}' for i in range(max_len)]
#
# talent_roles_df = pd.DataFrame(talent_roles, columns=column_names)
#
# df = pd.concat([df, talent_roles_df], axis=1)
#
# df.to_csv(output_csv_file_path, index=False)
driver.quit()