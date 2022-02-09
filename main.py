from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from time import sleep
from lxml import etree
import csv
import os

if not os.path.exists('./document'):
    os.mkdir('document')

if not os.path.exists('./document/output.csv'):
    row = 'Name', 'CPSO', 'Location', 'Phone', 'Fax', 'Second Location', 'Specialization', 'Note'
    with open('./document/output.csv', 'w', encoding='utf-8', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter='|', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(row)

startSelectOption = input("Please enter which option you want to start: ")

driver = webdriver.Firefox(executable_path=r'.\geckodriver.exe')

driver.get('https://doctors.cpso.on.ca/?search=general')
select = Select(
    driver.find_element(By.XPATH, '//*[@id="p_lt_ctl01_pageplaceholder_p_lt_ctl02_CPSO_AllDoctorsSearch_ddCity"]'))

# select city by select options
for y in range(int(startSelectOption), len(select.options)):
    select.select_by_index(y)
    sleep(2)
    driver.find_element(By.XPATH,
                        '//*[@id="p_lt_ctl01_pageplaceholder_p_lt_ctl02_CPSO_AllDoctorsSearch_btnSubmit1"]').click()
    sleep(2)

    if len(driver.find_elements(By.XPATH, '//*[@class="doctor-search-results"]')) != 0:

        isNextButtonActive = True

        while isNextButtonActive:
            numPages = len(driver.find_elements(By.XPATH, '//*[contains(@id,"lnbPage")]')) if len(
                driver.find_elements(By.XPATH, '//*[contains(@id,"lnbPage")]')) != 0 else 1

            if numPages > 1:
                NextButton = driver.find_element(By.XPATH, '//*[contains(@id,"lnbNextGroup")]')
                isNextButtonActive = False if 'aspNetDisabled' in NextButton.get_attribute("class") else True
            else:
                isNextButtonActive = False

            # Loop each page
            for x in range(numPages):
                if numPages != 1:
                    driver.find_elements(By.XPATH, '//*[contains(@id,"lnbPage")]')[x].click()

                tree = etree.HTML(driver.page_source)
                doctorList = tree.xpath('//*[@class="doctor-search-results"]/article')

                # Loop each doctors
                for doctor in doctorList:
                    doctorName = doctor.xpath('./h3/a/text()')[0] if len(doctor.xpath('./h3/a/text()')) == 1 else ''
                    CPSO = doctor.xpath('./h3/text()')[0].strip().replace(')', '').split(' ')[1] if len(
                        doctor.xpath('./h3/text()')) == 1 else ''
                    contacts = doctor.xpath('./p/strong')
                    location = doctor.xpath('./p/text()')

                    phone = ''
                    fax = ''
                    for contact in contacts:
                        location.remove(contact.tail)
                        if 'phone' in contact.text.lower():
                            phone = contact.tail.strip()
                            continue
                        if 'fax' in contact.text.lower():
                            fax = contact.tail.strip()
                            continue

                    secondaryLocation = \
                        doctor.xpath('./div[contains(@id,"pnlSecondaryAddress")]/p/em/text()')[0].split(':')[1] if len(
                            doctor.xpath('./div[contains(@id,"pnlSecondaryAddress")]/p/em/text()')) == 1 else ''
                    specialization = doctor.xpath('./div[contains(@id,"pnlSpecialization")]/p/text()')[0] if len(
                        doctor.xpath('./div[contains(@id,"pnlSpecialization")]/p/text()')) == 1 else ''
                    note = doctor.xpath('./div[contains(@class,"concerns")]/ul/li/text()') if len(
                        doctor.xpath('./div[contains(@class,"concerns")]/ul/li/text()')) > 0 else ''

                    row = doctorName.replace('\xa0', ' '), CPSO, ', '.join(location).replace('\xa0',
                                                                                             ' '), phone, fax, secondaryLocation, specialization.replace(
                        '\xa0', ' '), ','.join(note)

                    # write data into csv file
                    with open('./document/output.csv', 'a', encoding='utf-8', newline='') as csvfile:
                        writer = csv.writer(csvfile, delimiter='|', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                        writer.writerow(row)

            # click next button if next button active
            if isNextButtonActive:
                driver.find_element(By.XPATH, '//*[contains(@id,"lnbNextGroup")]').click()
                sleep(1)

    with open('./document/logCity.txt', 'a', newline='') as f:
        f.write("Finish city selection option: " + str(y))
        f.write('\n')

    # redirect to back search page
    driver.get('https://doctors.cpso.on.ca/?search=general')
    select = Select(
        driver.find_element(By.XPATH, '//*[@id="p_lt_ctl01_pageplaceholder_p_lt_ctl02_CPSO_AllDoctorsSearch_ddCity"]'))

sleep(2)
driver.quit()
