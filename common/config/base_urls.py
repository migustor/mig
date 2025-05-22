import os
from dotenv import load_dotenv

load_dotenv()

PROJECT_BASE_URLS = {
    "ra_eu": "https://stage15.office.ratrading.eu/sage/",
    "at_eu": "https://stage15.office.atlastradingworld.com/sage/",
    "ag_eu": "https://stage15.office.agavasystem.com/sage/",
    "sm_us": "https://stage15.office.sovamaxusa.com/sage/",
    "sm_eu": "https://stage15.office.sovasystem.com/sage/",
    "et_eu": "https://stage15.office.eminiasystem.com/sage/",
    "ho_eu": "https://stage15.office.horustrading.eu/sage/",
    "lt_eu": "https://stage15.office.laniustoys.com/sage/",
    "dr_eu": "https://stage15.office.dbreactor.com/sage/",
    "argon": "https://stage15.office.argontrading.de/sage/",
    "aro_eu": "https://stage15.office.arotrading.eu/sage/",
    "roc":    "https://stage15.office.roctrading.de/sage/",
    "gr_eu":  "https://stage15.office.grafit.md/sage/",
    "et_store": "https://stage15.store.eminiatrading.com/"
}