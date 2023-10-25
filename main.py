import os
import pickle

from progress.bar import IncrementalBar
from domain.survey import Survey
from domain.asset import Asset
from google_client import GoogleClient
from loguru import logger
from loa_options import LoaOptions
from pprint import pprint
from time import sleep

# Configure loa option, this depends on which teams will it get from LoA
# Also it decides where to upload prepared data
LOA_OPTION = LoaOptions.GENERAL
PATH = os.getenv("GOOGLE_TOKEN_PATH")

with open("config.json", "r") as fp:
    import json

    CONFIG = json.load(fp)


def build_google_service(path):
    match LOA_OPTION:
        case LoaOptions.GENERAL:
            upload_table_link = CONFIG["links"]["general_loa"]
        case LoaOptions.GDPR:
            upload_table_link = CONFIG["links"]["gdpr_loa"]
        case LoaOptions.FINANCE:
            upload_table_link = CONFIG["links"]["finance_loa"]
        case _:
            raise NotImplemented

    return GoogleClient(path, upload_table_link)


@logger.catch()
def get_main_table(google_service):
    return google_service.get_values(google_service.main_table_id, "'Анкетирование'!A2:H1000")


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


def loa_handler_general(assets: list[Asset]) -> list[Asset]:
    resulting: list[Asset] = list()
    added_names = list()

    assets.sort(key=lambda x: x.name)

    for asset in assets:
        if asset.name.strip() not in added_names:
            resulting.append(asset)
            added_names.append(asset.name.strip())
        else:
            asset_index = added_names.index(asset.name)

            if asset.is_in_pci_dss_scope:
                resulting[asset_index].is_in_pci_dss_scope = True

            if asset.has_iid:
                resulting[asset_index].has_iid = True

            if asset.sensitive_data_description != resulting[
                asset_index].sensitive_data_description and asset.sensitive_data_description != "":
                resulting[asset_index].sensitive_data_description.extend(asset.sensitive_data_description)

            if asset.business_owner != resulting[asset_index].business_owner and asset.business_owner != "":
                resulting[asset_index].business_owner.extend(asset.business_owner)

            if asset.purpose != resulting[asset_index].purpose and asset.purpose != "":
                resulting[asset_index].purpose.extend(asset.purpose)

            if asset.access_owner != resulting[asset_index].access_owner and asset.access_owner != "":
                resulting[asset_index].access_owner.extend(asset.access_owner)

            if asset.comments != resulting[asset_index].comments and asset.comments != "":
                resulting[asset_index].comments.extend(asset.comments)

            resulting[asset_index].department_and_unit = (resulting[asset_index].department_and_unit.strip()
                                                          + "; " + asset.department_and_unit.strip())
    logger.debug("collapsing doubling entities...")
    for asset in resulting:
        asset.collapse()
    logger.debug("doubling entities collapsed")

    return resulting


def prepare_data(assets: list[Asset]) -> list[Asset]:
    match LOA_OPTION:
        case LOA_OPTION.GENERAL:
            return loa_handler_general(assets)
        case LOA_OPTION.GDPR:
            raise NotImplemented
        case LOA_OPTION.FINANCE:
            raise NotImplemented
        case _:
            raise NotImplemented


@logger.catch()
def survey_to_domain(raw_main_table: list[list[str, ...]]) -> list[Survey, ...]:
    return [Survey(x) for x in raw_main_table]


@logger.catch()
def upload(loa_package: list[list[str | bool]], google_service):
    google_service.upload_values(loa_package, "'LoA_raw'!A2:L1000")


def pack_up(loa: list[Asset]) -> list[list[str, bool, None]]:
    package: list[list[str | bool | None]] = list()

    for asset in loa:
        package.append([
            asset.name,
            asset.type,
            asset.is_in_pci_dss_scope,
            asset.has_iid,
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


def main(load_with_cache=None):
    logger.debug("retrieving google service...")
    google_service = build_google_service(PATH)
    logger.info("authorized to google")
    pprint(load_with_cache)

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


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Script to compute LOA, check README")
    parser.add_argument("--cache", type=bool, help="If you want to load from cache, pass \"True\"")

    args = parser.parse_args()
    main(args.cache)
