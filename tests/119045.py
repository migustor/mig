#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException
)
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
import time
import sys

# ------------------------------------------------------------------------------
# Systems to Test
# Each entry has:
#   "name": A short name for logging
#   "login_url": The login page
#   "editor_url": The page with "sales_order_list_items" table
# ------------------------------------------------------------------------------
systems_config = [
    {
        "name": "Eminia",
        "login_url": "https://stage15.office.eminiasystem.com/sage/?logout",
        "editor_url": "https://stage15.office.eminiasystem.com/sage/index.cfm?page_id=888&phase=edit&sales_order_id=276267"
    },
    {
        "name": "Sova max usa",
        "login_url": "https://stage15.office.sovamaxusa.com/sage/?logout",
        "editor_url": "https://stage15.office.sovamaxusa.com/sage/index.cfm?page_id=888&phase=edit&sales_order_id=34525"
    },
    {
        "name": "Sova max",
        "login_url": "https://stage15.office.sovasystem.com/sage/?logout",
        "editor_url": "https://stage15.office.sovasystem.com/sage/index.cfm?page_id=888&phase=edit&sales_order_id=605352"
    },
    {
        "name": "Agava",
        "login_url": "https://stage15.office.agavasystem.com/sage/?logout",
        "editor_url": "https://stage15.office.agavasystem.com/sage/index.cfm?page_id=888&phase=edit&sales_order_id=50248"
    },
    {
        "name": "Lanius",
        "login_url": "https://stage15.office.laniustoys.com/sage/?logout",
        "editor_url": "https://stage15.office.laniustoys.com/sage/index.cfm?page_id=888&phase=edit&sales_order_id=88021"
    },
    {
        "name": "Ra trading",
        "login_url": "https://stage15.office.ratrading.eu/sage/?logout",
        "editor_url": "https://stage15.office.ratrading.eu/sage/index.cfm?page_id=888&phase=edit&sales_order_id=100723"
    },
    {
        "name": "Horus",
        "login_url": "https://stage15.office.horustrading.eu/sage/?logout",
        "editor_url": "https://stage15.office.horustrading.eu/sage/index.cfm?page_id=888&phase=edit&sales_order_id=892"
    },
    {
        "name": "Dbreactor",
        "login_url": "https://stage15.office.dbreactor.com/sage/?logout",
        "editor_url": "https://stage15.office.dbreactor.com/sage/index.cfm?page_id=888&phase=edit&sales_order_id=1083"
    },
    {
        "name": "Atlas",
        "login_url": "https://stage15.office.atlastradingworld.com/sage/?logout",
        "editor_url": "https://stage15.office.atlastradingworld.com/sage/index.cfm?page_id=888&phase=edit&sales_order_id=483"
    }
]

# ------------------------------------------------------------------------------
# Global Credentials
# (Assuming same for all systems)
# ------------------------------------------------------------------------------
USERNAME = "victor.moisei@mteam.md"
PASSWORD = "12"

# We will do a single driver or you can re-instantiate the driver per system.
# Let's do a single driver for demonstration, though re-initializing might 
# be safer if each system is truly separate.

driver = webdriver.Chrome()
logs = []

# ------------------------------------------------------------------------------
# Logging
# ------------------------------------------------------------------------------
def log_and_print(msg):
    print(msg)
    logs.append(msg)

# ------------------------------------------------------------------------------
# Wait Helpers
# ------------------------------------------------------------------------------
def wait_for_element(locator_type, locator, timeout=10):
    try:
        return WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((locator_type, locator))
        )
    except TimeoutException:
        log_and_print(f"FAILED: Element not found: {locator}")
        driver.quit()
        sys.exit(1)

def wait_for_clickable(locator_type, locator, timeout=10):
    try:
        return WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((locator_type, locator))
        )
    except TimeoutException:
        log_and_print(f"FAILED: Element not clickable: {locator}")
        driver.quit()
        sys.exit(1)

def wait_for_invisible(locator_type, locator, timeout=10):
    try:
        WebDriverWait(driver, timeout).until(
            EC.invisibility_of_element_located((locator_type, locator))
        )
        time.sleep(1)
    except TimeoutException:
        log_and_print(f"FAILED: Element '{locator}' did not become invisible in time.")
        driver.quit()
        sys.exit(1)

def safe_click(locator_type, locator, timeout=10):
    elem = wait_for_clickable(locator_type, locator, timeout)
    driver.execute_script("arguments[0].scrollIntoView(true);", elem)
    time.sleep(0.5)
    driver.execute_script("arguments[0].click();", elem)
    time.sleep(1)

# ------------------------------------------------------------------------------
# Priority Modal Functions
# ------------------------------------------------------------------------------
def select_priority_in_modal(priority_text):
    log_and_print(f"Selecting priority: {priority_text}")
    dropdown = wait_for_element(By.ID, "modal_profile_priority")
    Select(dropdown).select_by_visible_text(priority_text)
    time.sleep(0.5)

def click_modal_save():
    log_and_print("Clicking 'Save' on modal...")
    save_btn = wait_for_element(By.ID, "modalProfileSave_btn")
    save_btn.click()
    time.sleep(1)

def wait_modal_close():
    wait_for_invisible(By.ID, "modal_profile_priority")

# ------------------------------------------------------------------------------
# Re-profile Logic
# ------------------------------------------------------------------------------
def reprofile_item(row_element, new_priority):
    """Similar logic as previously used to re-profile a single item row."""
    desc_elems = row_element.find_elements(By.CSS_SELECTOR, "strong.item_description")
    item_desc = ""
    for d in desc_elems:
        txt = d.text.strip()
        if txt:
            item_desc = txt
            break

    log_and_print(f"Reprofiling '{item_desc}' => '{new_priority}'")
    profile_btn = row_element.find_element(By.XPATH, ".//input[starts-with(@id,'profile_item_id_')]")
    driver.execute_script("arguments[0].scrollIntoView(true);", profile_btn)
    time.sleep(0.5)
    driver.execute_script("arguments[0].click();", profile_btn)
    time.sleep(1)

    select_priority_in_modal(new_priority)
    click_modal_save()
    wait_modal_close()

    log_and_print(f"Successfully re-profiled '{item_desc}' => {new_priority}")
    return item_desc

# ------------------------------------------------------------------------------
# PBO Filter
# ------------------------------------------------------------------------------
def select_single_priority_and_search(priority_text):
    log_and_print(f"Selecting only '{priority_text}' in PBO filter...")

    pbo_container = wait_for_element(By.ID, "profile_based_op")
    # 1) Open dropdown
    multi_span = pbo_container.find_element(By.XPATH, ".//span[contains(@class,'multiselect-selected-text')]")
    driver.execute_script("arguments[0].scrollIntoView(true);", multi_span)
    time.sleep(0.5)
    driver.execute_script("arguments[0].click();", multi_span)
    time.sleep(1)

    # 2) Uncheck all
    checkboxes = pbo_container.find_elements(By.XPATH, ".//ul[contains(@class,'multiselect-container')]//input[@type='checkbox']")
    for cb in checkboxes:
        if cb.is_selected():
            driver.execute_script("arguments[0].click();", cb)
    time.sleep(1)

    # 3) Check only priority_text
    prio_xpath = f".//ul[contains(@class,'multiselect-container')]//label[contains(text(),'{priority_text}')]/input"
    prio_cb = pbo_container.find_element(By.XPATH, prio_xpath)
    if not prio_cb.is_selected():
        driver.execute_script("arguments[0].click();", prio_cb)
    time.sleep(1)

    # 4) Close
    driver.execute_script("arguments[0].click();", multi_span)
    time.sleep(1)

    # 5) Search
    search_btn = driver.find_element(By.ID, "html_profile_based_opportunities_search_button")
    driver.execute_script("arguments[0].scrollIntoView(true);", search_btn)
    time.sleep(0.5)
    driver.execute_script("arguments[0].click();", search_btn)
    time.sleep(2)

def verify_pbo_items_found(expected_desc_list):
    log_and_print(f"Verifying PBO results: {expected_desc_list}")
    try:
        panel = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((
                By.XPATH,
                "//div[@class='panel panel-default' and .//h4[contains(text(), 'Item(s) Found')]]"
            ))
        )
        info_divs = panel.find_elements(By.CSS_SELECTOR, "div.info_compact strong.item_description")
        found_list = [x.text.strip() for x in info_divs]

        set_exp = set(expected_desc_list)
        set_found = set(found_list)
        if set_exp == set_found:
            log_and_print("PASSED: Correct item(s) displayed.")
        else:
            log_and_print("FAILED: Mismatch in PBO items.")
            log_and_print(f"Expected: {set_exp}")
            log_and_print(f"Found:    {set_found}")
            driver.quit()
            sys.exit(1)
    except TimeoutException:
        log_and_print("FAILED: 'Item(s) Found' panel not found in PBO.")
        driver.quit()
        sys.exit(1)
    except Exception as e:
        log_and_print(f"FAILED: verify_pbo_items_found => {e}")
        driver.quit()
        sys.exit(1)

# ------------------------------------------------------------------------------
# Test Flow for a Single System
# ------------------------------------------------------------------------------
def test_system(login_url, editor_url, system_name):
    """
    1) Log in at login_url
    2) Navigate to editor_url
    3) Expand 'Add More Items' => PBO
    4) Re-profile first => Low, second => Medium, verifying each
    5) Re-profile them => High, Web Store, verifying each
    """
    log_and_print(f"\n=== Starting test for {system_name} ===")

    # Step A: Go to login
    driver.get(login_url)
    time.sleep(2)
    # Attempt login
    try:
        driver.find_element(By.ID, "login_name").send_keys(USERNAME)
        driver.find_element(By.ID, "password").send_keys(PASSWORD, Keys.RETURN)
        log_and_print(f"{system_name}: Logged in successfully.")
    except NoSuchElementException:
        log_and_print(f"FAILED: {system_name} - login fields not found.")
        driver.quit()
        sys.exit(1)
    time.sleep(3)

    # Step B: Go to editor
    driver.get(editor_url)
    time.sleep(3)

    # Step C: Expand "Add More Items" => "Profile Based Opportunities"
    safe_click(By.XPATH, "//h4[contains(text(),'Add More Items')]")
    safe_click(By.XPATH, "//a[@href='#profile_based_op' and contains(text(),'Profile Based Opportunities')]")

    # Step D: Access items table (we skip heading click)
    so_table = wait_for_element(By.ID, "sales_order_list_items")
    rows = so_table.find_elements(By.XPATH, ".//tbody/tr[starts-with(@id,'sales_order_item_row_')]")
    if not rows:
        log_and_print(f"FAILED: {system_name} - No items found in 'List of Sales Order Items'.")
        driver.quit()
        sys.exit(1)

    # Step E: Reprofile first => Low, second => Medium
    item1_desc = reprofile_item(rows[0], "Low")
    item2_desc = ""
    if len(rows) > 1:
        item2_desc = reprofile_item(rows[1], "Medium")

    # Step F: Check each in PBO singly
    # only Low => item1
    select_single_priority_and_search("Low")
    verify_pbo_items_found([item1_desc])

    if item2_desc:
        select_single_priority_and_search("Medium")
        verify_pbo_items_found([item2_desc])

    # Step G: Re-profile => High, Web Store
    item1_desc = reprofile_item(rows[0], "High")
    if item2_desc:
        item2_desc = reprofile_item(rows[1], "Web Store")

    # Step H: Check each singly
    select_single_priority_and_search("High")
    verify_pbo_items_found([item1_desc])

    if item2_desc:
        select_single_priority_and_search("Web Store")
        verify_pbo_items_found([item2_desc])

    log_and_print(f"{system_name}: ALL STEPS COMPLETED SUCCESSFULLY.")

# ------------------------------------------------------------------------------
# Main Script: Loop over each system in systems_config
# ------------------------------------------------------------------------------
try:
    for system_info in systems_config:
        sys_name = system_info["name"]
        login_page = system_info["login_url"]
        editor_page = system_info["editor_url"]

        test_system(login_page, editor_page, sys_name)

    log_and_print("All systems tested successfully. Test PASSED.")
    driver.quit()
    sys.exit(0)

except Exception as e:
    log_and_print(f"FAILED: Unexpected error => {e}")
    driver.quit()
    sys.exit(1)
