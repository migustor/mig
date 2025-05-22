"""
Локаторы для страницы поиска инвентаря (ID: 584)
"""
from selenium.webdriver.common.by import By

# Элементы поиска и фильтры
SEARCH_FORM = {
    # Основные поля ввода
    "part_number_field": (By.ID, "item_part_number"),
    "description_field": (By.ID, "item_description"),
    "model_field": (By.ID, "model"),
    "sku_field": (By.ID, "sku"),
    "barcode_field": (By.ID, "barcode"),
    "brand_field": (By.ID, "brand"),

    # Выпадающие списки
    "company_select": (By.ID, "customer_company_id"),
    "country_select": (By.ID, "country_id"),
    "category_select": (By.ID, "category_id"),
    "brands_specifics": (By.ID, "brands_specifics"),
    "condition_select": (By.ID, "condition_id"),

    # Кнопки действий
    "search_button": (By.ID, "html_inventory_search_button"),
    "reset_button": (By.ID, "reset_btn"),
    "save_filters_button": (By.ID, "save_filters"),

    # Мультиселекты и их элементы
    "brands_specifics_button": (By.CSS_SELECTOR, "button.multiselect[data-toggle='dropdown']"),
    "brands_dropdown_container": (By.CSS_SELECTOR, ".multiselect-container.dropdown-menu"),
    "brands_select_all": (By.CSS_SELECTOR, ".multiselect-container input[value='all']"),
    "brands_options": (By.CSS_SELECTOR, ".multiselect-container input[type='checkbox']"),

    # Чекбоксы и переключатели
    "in_stock_checkbox": (By.ID, "in_stock"),
    "include_discontinued_checkbox": (By.ID, "include_discontinued"),
    "price_range_toggle": (By.ID, "price_range_toggle"),

    # Поля диапазонов
    "min_price": (By.ID, "min_price"),
    "max_price": (By.ID, "max_price"),
    "min_qty": (By.ID, "min_qty"),
    "max_qty": (By.ID, "max_qty")
}

# Элементы результатов поиска
RESULTS = {
    # Основные элементы таблицы
    "table": (By.CSS_SELECTOR, "table.table"),
    "table_container": (By.ID, "search_results_container"),
    "rows": (By.CSS_SELECTOR, "table.table tbody tr"),
    "headers": (By.CSS_SELECTOR, "table.table thead th"),

    # Пагинация
    "pager": (By.CSS_SELECTOR, ".pager .previous strong:last-child"),
    "pagination_container": (By.CSS_SELECTOR, ".pagination"),
    "next_page": (By.CSS_SELECTOR, ".pagination .next a"),
    "prev_page": (By.CSS_SELECTOR, ".pagination .prev a"),
    "first_page": (By.CSS_SELECTOR, ".pagination .first a"),
    "last_page": (By.CSS_SELECTOR, ".pagination .last a"),
    "page_numbers": (By.CSS_SELECTOR, ".pagination li:not(.prev):not(.next):not(.first):not(.last) a"),

    # Информационные сообщения
    "no_results_message": (By.CSS_SELECTOR, "div.alert-info"),
    "loading_indicator": (By.CSS_SELECTOR, ".loading-indicator"),
    "results_count_label": (By.CSS_SELECTOR, ".results-count"),

    # Ссылки в результатах
    "item_links": (By.CSS_SELECTOR, "table.table tbody tr td a[href*='page_id=714']"),
    "company_links": (By.CSS_SELECTOR, "table.table tbody tr td a[href*='page_id=531']"),
    "expand_details": (By.CSS_SELECTOR, "a.expand-details"),

    # Элементы строк результатов
    "part_number_cells": (By.CSS_SELECTOR, "td.part-number"),
    "description_cells": (By.CSS_SELECTOR, "td.description"),
    "price_cells": (By.CSS_SELECTOR, "td.price"),
    "qty_cells": (By.CSS_SELECTOR, "td.quantity"),
    "availability_cells": (By.CSS_SELECTOR, "td.availability"),
    "brand_cells": (By.CSS_SELECTOR, "td.brand"),

    # Кнопки действий в результатах
    "add_to_cart_buttons": (By.CSS_SELECTOR, "button.add-to-cart"),
    "add_to_quote_buttons": (By.CSS_SELECTOR, "button.add-to-quote"),
    "compare_checkboxes": (By.CSS_SELECTOR, "input.compare-checkbox")
}

# Сообщения об ошибках и валидации
ERRORS = {
    # Общие ошибки
    "general_error": (By.CSS_SELECTOR, "div.alert-danger"),
    "validation_summary": (By.CSS_SELECTOR, ".validation-summary-errors"),

    # Ошибки конкретных полей
    "part_number_error": (By.CSS_SELECTOR, "#part_number_error"),
    "description_error": (By.CSS_SELECTOR, "#description_error"),
    "price_range_error": (By.CSS_SELECTOR, "#price_range_error"),

    # Специфичные ошибки
    "brands_specifics_error": (By.CSS_SELECTOR, ".brands_specifics_summary-errors"),
    "validation_errors": (By.CSS_SELECTOR, ".has-error .help-block"),
    "server_error": (By.CSS_SELECTOR, ".server-error"),

    # Предупреждения
    "search_warning": (By.CSS_SELECTOR, ".search-warning"),
    "filter_warning": (By.CSS_SELECTOR, ".filter-warning")
}

# Элементы экспорта и специальных операций
EXPORT = {
    # Кнопки экспорта
    "export_dropdown": (By.ID, "export_dropdown"),
    "export_excel": (By.ID, "export_excel"),
    "export_csv": (By.ID, "export_csv"),
    "export_pdf": (By.ID, "export_pdf"),

    # Настройки экспорта
    "export_columns_dropdown": (By.ID, "export_columns"),
    "export_format_select": (By.ID, "export_format"),
    "include_images_checkbox": (By.ID, "include_images"),

    # Модальное окно экспорта
    "export_modal": (By.ID, "exportModal"),
    "export_confirm_button": (By.CSS_SELECTOR, "#exportModal .btn-primary"),
    "export_cancel_button": (By.CSS_SELECTOR, "#exportModal .btn-secondary")
}

# Элементы сохранения и загрузки шаблонов поиска
SEARCH_TEMPLATES = {
    # Кнопки шаблонов
    "save_template_button": (By.ID, "save_search_template"),
    "load_template_button": (By.ID, "load_search_template"),

    # Элементы модального окна сохранения
    "template_name_input": (By.ID, "template_name"),
    "save_as_default_checkbox": (By.ID, "save_as_default"),
    "save_template_confirm": (By.CSS_SELECTOR, "#saveTemplateModal .btn-primary"),

    # Элементы модального окна загрузки
    "template_select": (By.ID, "template_select"),
    "delete_template_button": (By.ID, "delete_template"),
    "load_template_confirm": (By.CSS_SELECTOR, "#loadTemplateModal .btn-primary")
}

# Элементы сравнения товаров
COMPARE = {
    # Кнопки сравнения
    "compare_button": (By.ID, "compare_selected"),
    "clear_compare_button": (By.ID, "clear_compare"),

    # Счетчик выбранных элементов
    "selected_count": (By.ID, "selected_count"),

    # Страница сравнения
    "comparison_table": (By.ID, "comparison_table"),
    "comparison_headers": (By.CSS_SELECTOR, "#comparison_table th"),
    "feature_rows": (By.CSS_SELECTOR, "#comparison_table tr.feature-row")
}

# Специальные элементы для мобильного вида
MOBILE_VIEW = {
    "filter_toggle": (By.ID, "filter_toggle"),
    "mobile_search_button": (By.ID, "mobile_search"),
    "mobile_pagination": (By.CSS_SELECTOR, ".mobile-pagination"),
    "view_switcher": (By.CSS_SELECTOR, ".view-switcher")
}
