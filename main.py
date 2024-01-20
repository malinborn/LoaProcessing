import os
import pickle

from progress.bar import IncrementalBar
from domain.survey import Survey
from domain.asset import Asset
from google_client import GoogleClient
from loguru import logger
from loa_options import LoaOptions
from modes import Modes
from pprint import pprint
from time import sleep
from handlers import loa_handler
from domain.domain import Domain

PATH = os.getenv("GOOGLE_TOKEN_PATH")

with open("config.json", "r") as fp:
    import json

    CONFIG = json.load(fp)


def build_google_service(path):
    match LOA_OPTION:
        case LoaOptions.GENERAL:            upload_table_link = CONFIG["links"]["general_loa"]
        case LoaOptions.GDPR:               upload_table_link = CONFIG["links"]["gdpr_loa"]
        case LoaOptions.FINANCE:            upload_table_link = CONFIG["links"]["finance_loa"]
        case LoaOptions.ENGINEERING:        upload_table_link = CONFIG["links"]["engineering_loa"]
        case LoaOptions.CORPORATE:          upload_table_link = CONFIG["links"]["corporate_loa"]
        case LoaOptions.MARKETING:          upload_table_link = CONFIG["links"]["marketing_loa"]
        case LoaOptions.DODO_PIZZA_EURASIA: upload_table_link = CONFIG["links"]["dodo_pizza_eurasia_loa"]
        case LoaOptions.DRINKIT:            upload_table_link = CONFIG["links"]["drinkit_loa"]
        case LoaOptions.KEBSTER:            upload_table_link = CONFIG["links"]["kebster_loa"]
        case LoaOptions.MENUSA:             upload_table_link = CONFIG["links"]["menusa_loa"]
        case LoaOptions.DRINKIT_UAE:        upload_table_link = CONFIG["links"]["drinkit_uae_loa"]
        case LoaOptions.DODO_PIZZA_UAE:     upload_table_link = CONFIG["links"]["dodo_pizza_uae_loa"]
        case _: raise NotImplemented

    return GoogleClient(path, upload_table_link)


# TODO: Нужно типизировать/классифицировать в таблице с анкеритированием так, чтобы не нужно было свойство unit,
#       чтобы этот метод тоже, в целом, был не нужен. Прийти должны к чему-то типа того — str(LOA_OPTION)
def prepare_data(assets: list[Asset]) -> list[Asset]:
    match LOA_OPTION:
        case LOA_OPTION.GENERAL:
            domain = Domain([], [])
        case LOA_OPTION.ENGINEERING:
            domain = Domain(
                units=["IT Eurasia People&Communications", "IT Eurasia B2B", "NSFW (Not safe for work)",
                       "SE (Seven-eleven)",
                       "Rocket Science", "k9", "HR Automation", "Slippers of Mimir", "IT Team", "IT"],
                departments=["CVM", "CVM Dev Core", "Vulnerable", "Guilds", "Platform", "DevRel"])
        case LOA_OPTION.GDPR:
            raise NotImplemented
        case LOA_OPTION.FINANCE:
            domain = Domain(units=[],
                            departments=["Finance"])
        case LOA_OPTION.CORPORATE:
            domain = Domain(units=[],
                            departments=["Finance", "HR Global", "Legal"])
        case LoaOptions.MARKETING:
            domain = Domain(units=[],
                            departments=["Marketing", "Global Marketing"])
        case LoaOptions.DODO_PIZZA_EURASIA:
            domain = Domain(units=[],
                            departments=["Business Development", "Quality Management", "Supply Chain", "DCM",
                                         "HR Eurasia"])
        case LoaOptions.DRINKIT:
            domain = Domain(units=[],
                            departments=["Drinkit"])
        case LoaOptions.KEBSTER:
            domain = Domain(units=[],
                            departments=["Kebster"])
        case LoaOptions.MENUSA:
            domain = Domain(units=[],
                            departments=["Menusa"])
        case LoaOptions.DRINKIT_UAE:
            domain = Domain(units=[],
                            departments=["Drinkit UAE"])
        case LoaOptions.DODO_PIZZA_UAE:
            domain = Domain(units=[],
                            departments=["Dodo Pizza UAE"])
        case _:
            raise NotImplemented
    return loa_handler(assets, domain)


@logger.catch()
def get_main_table(google_service):
    return google_service.get_values(CONFIG["links"]["general_loa"], "'Анкетирование'!A2:H1000")


def collect_assets_from_sub_tables(main_table: list[Survey], google_service):
    subtables_assets = list()

    bar = IncrementalBar('Countdown', max=len(main_table))

    for survey in main_table:
        try:
            logger.debug(f"getting data for {survey.department} {survey.unit}...")
            subtable_raw_assets: list[list] = google_service.get_values(survey.link, "Лист1")["values"]

            logger.debug(f"trying to merge into domain data of {survey.department} {survey.unit}...")
            subtable_assets: list[Asset] = [Asset(clarified_row, survey) for clarified_row in
                                            [row for row in subtable_raw_assets if row[0] != ""][1:]]

            subtables_assets.extend(subtable_assets)
        except Exception as ex:
            logger.error(f"couldn't get survey of {survey.department} {survey.unit}"
                         f"\n{ex}")
        bar.next()
        print("")
        sleep(1)  # it is needed to comply with Google API quotas
    return subtables_assets


@logger.catch()
def survey_to_domain(raw_main_table: list[list[str, ...]]) -> list[Survey, ...]:
    return [Survey(x) for x in raw_main_table]


@logger.catch()
def upload(loa_package: list[list[str | bool]], google_service):
    google_service.upload_values(loa_package, "'LoA_raw'!A2:Z1000")


def pack_up(loa: list[Asset]) -> list[list[str, bool, None]]:
    package: list[list[str | bool | None]] = list()

    for asset in loa:
        package.append([
            asset.name,
            asset.type,
            asset.is_in_pci_dss_scope,
            asset.has_iid_clients,
            asset.has_iid_employees,
            asset.sensitive_data_description,
            asset.business_owner,
            asset.purpose,
            asset.access_owner,
            asset.comments,
            asset.department,
            asset.unit,
            asset.department_and_unit
        ])

    return package


def get_assets_from_cache():
    logger.debug("loading from file...")
    with open("stored.pickle", "rb") as fp:
        assets = pickle.load(fp)
    return assets


def get_assets_from_google(google_service):
    logger.info("loading from google...")
    logger.debug("retrieving main table, inventory sheet...")
    raw_main_table: list[list[str, ...]] = get_main_table(google_service)["values"]
    main_table: list[Survey, ...] = survey_to_domain(raw_main_table)
    Survey.fill_departments(main_table)
    # pprint(main_table)
    logger.info("obtained main table, inventory sheet")
    logger.info("collecting assets from sub tables...")
    assets = collect_assets_from_sub_tables(main_table, google_service)
    # pprint(assets)
    logger.info(f"collected assets from sub tables...")
    logger.info("dumping data into file...")
    with open("stored.pickle", "wb") as fp:
        pickle.dump(assets, fp)
    return assets


def loa_collect(google_service, load_with_cache):
    if (not os.path.isfile("stored.pickle") and load_with_cache) or not load_with_cache:
        if not os.path.isfile("stored.pickle"):
            logger.info("seems like there is no cache")
        assets = get_assets_from_google(google_service)
    else:
        assets = get_assets_from_cache()
    logger.info(f"preparing data for {str(LOA_OPTION.name)}...")
    loa = prepare_data(assets)
    # pprint(loa)
    # print(len(loa))
    logger.info(f"prepared data for {str(LOA_OPTION.name)}")
    logger.info(f"uploading data for {str(LOA_OPTION.name)} LOA...")
    upload(pack_up(loa), google_service)
    logger.info(f"uploaded data for {str(LOA_OPTION.name)} LOA")
    logger.info("all done, shutting down...")


def loa_backsync(google_service):
    pass


def main(load_with_cache: bool = None):
    logger.debug("retrieving google service...")
    google_service = build_google_service(PATH)
    logger.info("authorized to google")

    match MODE:
        case Modes.COLLECT:   loa_collect(google_service, load_with_cache)
        case Modes.BACKSYNC:  loa_backsync(google_service)
        case _: raise NotImplemented("There is no such mode yet")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Script to compute LOA, check README")
    parser.add_argument("mode", metavar="mode", type=str, help="performs update on surveys by info from "
                                                               "the general LOA")
    parser.add_argument("-c", "--cache", type=str, help="If you want to load from cache, pass \"True\"",
                        choices=["True"])
    parser.add_argument("-d", "--domain", type=str, help="Enter name of domain for which you want to collect LOA, "
                                                   "for example, \"DE\", \"Finance\" etc. GENERAL is default value. "
                                                   "Make sure that you configured link to spreadsheet in config.jsom")
    args = parser.parse_args()

    match args.mode.upper():
        case "backsync" | "bs" | "back_sync" | "back_synchronization": MODE = Modes.BACKSYNC
        case _:                                                        MODE = Modes.COLLECT

    cache_option = True if args.cache == "True" else False

    match args.domain.upper():
        case "DE" | "ENGINEERING":                                 LOA_OPTION = LoaOptions.ENGINEERING
        case "FN" | "FINANCE":                                     LOA_OPTION = LoaOptions.FINANCE
        case "DPEU" | "DODO PIZZA EURASIA" | "DODO_PIZZA_EURASIA": LOA_OPTION = LoaOptions.DODO_PIZZA_EURASIA
        case "CRP" | "CORPORATE":                                  LOA_OPTION = LoaOptions.CORPORATE
        case "MRKT" | "MARKETING":                                 LOA_OPTION = LoaOptions.MARKETING
        case "DI" | "DRINKIT":                                     LOA_OPTION = LoaOptions.DRINKIT
        case "KB" | "KEBSTER":                                     LOA_OPTION = LoaOptions.KEBSTER
        case "MNS" | "MENUSA":                                     LOA_OPTION = LoaOptions.MENUSA
        case "DIUAE" | "DRINKIT UAE" | "DRINKIT_UAE":              LOA_OPTION = LoaOptions.DRINKIT_UAE
        case "DPUAE" | "DODO PIZZA UAE" | "DODO_PIZZA_UAE":        LOA_OPTION = LoaOptions.DODO_PIZZA_UAE
        case _:                                                    LOA_OPTION = LoaOptions.GENERAL

    logger.info(f"{LOA_OPTION=}")

    main(cache_option)
