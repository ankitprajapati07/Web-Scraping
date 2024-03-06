from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import csv
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import credential
from time import sleep


def login_linkedin(credential): #credential is module(credential.py) that stored username & password

    chrome_options = Options()
    chrome_options.add_argument("--incognito")
    driver = webdriver.Chrome(options=chrome_options)
    driver.get('https://www.linkedin.com/home')

    # Entering username via send keys
    username = driver.find_element('id', 'session_key')
    username.send_keys(credential.linkedin_username)
    sleep(0.5)

    # Entering password via send keys
    password = driver.find_element('id', "session_password")
    password.send_keys(credential.linkedin_password)
    sleep(0.5)

    # Locate the sign-in button using Xpath
    sign_in_button = WebDriverWait(driver, 10).until(
      EC.element_to_be_clickable((By.XPATH, '//button[@type="submit"]'))
    )

    sign_in_button.click()
    driver.implicitly_wait(10)
    return driver


def scrape_linkedin_data(driver, first_name, last_name):

    driver.get(f"https://www.linkedin.com/pub/dir?firstName={first_name}&lastName={last_name}&trk=people-guest_people-search-bar_search-submit")

    # Wait for page to load
    driver.implicitly_wait(10)

    # Extracting profiles
    profiles = driver.find_elements(By.CLASS_NAME, "reusable-search__result-container")
    #print("profiles: ", profiles)
    data = []

    for profile in profiles[:10]:
        profile.click()  # Clicking on the profile to view full details
        driver.implicitly_wait(5)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        full_name = soup.find('h1', class="ember741text-heading-xlarge inline t-24 v-align-middle break-words").get_text().strip()
        occupation = soup.find('div', class_='display-flex align-items-center mr1 t-bold').get_text().strip()
        current_company = soup.find('div', class_='HEgpIEFMxDRUizkbRBHapVYbGpJhbCOyI inline-show-more-text--is-collapsed inline-show-more-text--is-collapsed-with-line-clamp inline').get_text().strip()
        location = soup.find('span', class_='text-body-small inline t-black--light break-words').get_text().strip()

        data.append({
            'Full Name': full_name,
            'Occupation': occupation,
            'current company': current_company,
            'Location': location
        })
        driver.back()  # Going back to search results page

    driver.quit()

    return data


def save_to_csv(data, filename):
    if data:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['Full Name', 'Occupation', 'current company', 'Location']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for person in data:
                writer.writerow(person)
        print("Data saved to CSV successfully.")
    else:
        print("No data to save.")


if __name__ == "__main__":
    first_name = input("Enter user's first name: ")
    last_name = input("Enter user's last name: ")

    login = login_linkedin(credential)
    linkedin_data = scrape_linkedin_data(login, first_name, last_name)
    if linkedin_data:
        save_to_csv(linkedin_data, 'linkedin_data_browser.csv')
