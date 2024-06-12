import os
import pickle

from progress.bar import IncrementalBar
from domain.survey import Survey
from domain.asset import Asset
from domain.update_pack import UpdatePack
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
    logger.debug("retrieving google service...")
    match LOA_OPTION:
        case LoaOptions.GENERAL:
            upload_table_link = CONFIG["links"]["general_loa"]
        case LoaOptions.GDPR:
            upload_table_link = CONFIG["links"]["gdpr_loa"]
        case LoaOptions.FINANCE:
            upload_table_link = CONFIG["links"]["finance_loa"]
        case LoaOptions.ENGINEERING:
            upload_table_link = CONFIG["links"]["engineering_loa"]
        case LoaOptions.CORPORATE:
            upload_table_link = CONFIG["links"]["corporate_loa"]
        case LoaOptions.MARKETING:
            upload_table_link = CONFIG["links"]["marketing_loa"]
        case LoaOptions.DODO_PIZZA_EURASIA:
            upload_table_link = CONFIG["links"]["dodo_pizza_eurasia_loa"]
        case LoaOptions.DRINKIT:
            upload_table_link = CONFIG["links"]["drinkit_loa"]
        case LoaOptions.KEBSTER:
            upload_table_link = CONFIG["links"]["kebster_loa"]
        case LoaOptions.MENUSA:
            upload_table_link = CONFIG["links"]["menusa_loa"]
        case LoaOptions.DRINKIT_UAE:
            upload_table_link = CONFIG["links"]["drinkit_uae_loa"]
        case LoaOptions.DODO_PIZZA_UAE:
            upload_table_link = CONFIG["links"]["dodo_pizza_uae_loa"]
        case LoaOptions.IMF:
            upload_table_link = CONFIG["links"]["imf_loa"]
        case _:
            raise NotImplemented

    logger.info("authorized to google")
    return GoogleClient(path, upload_table_link)


def loa_collect(google_service):
    logger.info("performing collect...")
    if (not os.path.isfile("stored.pickle") and CACHE_OPTION) or not CACHE_OPTION:
        if not os.path.isfile("stored.pickle"):
            logger.info("seems like there is no cache")
        assets = get_assets_from_google(google_service)
    else:
        assets = get_assets_from_cache()

    loa: list[Asset] = prepare_data(assets)

    upload(pack_up(loa), google_service)


def get_assets_from_cache():
    logger.debug("loading from file...")
    with open("stored.pickle", "rb") as fp:
        assets = pickle.load(fp)
    return assets


def store_cache(assets):
    logger.info("dumping data into file...")
    with open("stored.pickle", "wb") as fp:
        pickle.dump(assets, fp)


def get_assets_from_google(google_service):
    logger.info("loading from google...")

    main_table = get_surveys(google_service)

    assets = collect_assets_from_sub_tables(main_table, google_service)

    store_cache(assets)

    return assets


def get_surveys(google_service: GoogleClient) -> list[Survey]:
    raw_main_table: list[list[str, ...]] = get_main_table(google_service)["values"]
    main_table: list[Survey] = survey_to_domain(raw_main_table)
    Survey.fill_departments(main_table)
    return main_table


@logger.catch()
def get_main_table(google_service):
    logger.debug("retrieving main table, inventory sheet...")
    return google_service.get_values(CONFIG["links"]["general_loa"], "'Анкетирование'!A2:H1000")


@logger.catch()
def survey_to_domain(raw_main_table: list[list[str, ...]]) -> list[Survey]:
    return [Survey(x) for x in raw_main_table]


def collect_assets_from_sub_tables(main_table: list[Survey], google_service):
    logger.info("collecting assets from sub tables...")
    subtables_assets = list()

    bar = IncrementalBar('Countdown', max=len(main_table))

    for survey in main_table:
        try:
            logger.debug(f"getting data for {survey.department} {survey.unit}...")
            subtable_raw_assets: list[list[str, ...]] = google_service.get_values(survey.link, "Лист1")["values"]

            logger.debug(f"trying to merge into domain data of {survey.department} {survey.unit}...")
            subtable_assets: list[Asset] = [Asset.make_from_survey(clarified_row, survey) for clarified_row in
                                            [row for row in subtable_raw_assets if row[0] != ""][1:]]

            subtables_assets.extend(subtable_assets)
        except Exception as ex:
            logger.error(f"couldn't get survey of {survey.department} {survey.unit}"
                         f"\n{ex}")
        bar.next()
        print("")
        sleep(1)  # it is needed to comply with Google API quotas
    logger.info(f"collected assets from sub tables...")
    return subtables_assets


# TODO: Нужно типизировать/классифицировать в таблице с анкеритированием так, чтобы не нужно было свойство unit,
#       чтобы этот метод тоже, в целом, был не нужен. Прийти должны к чему-то типа того — str(LOA_OPTION)
def prepare_data(assets: list[Asset]) -> list[Asset]:
    logger.info(f"preparing data for {str(LOA_OPTION.name)}...")
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
        case LoaOptions.IMF:
            domain = Domain(units=[],
                            departments=["Internation Master Franchising"])
        case _:
            raise NotImplemented
    logger.info(f"prepared data for {str(LOA_OPTION.name)}")
    return loa_handler(assets, domain)


@logger.catch()
def upload(loa_package: list[list[str | bool]], google_service):
    logger.info(f"uploading data for {str(LOA_OPTION.name)} LOA...")
    google_service.wipe_range(spreadsheet_id=google_service.main_table_id, range="'LoA_raw'!A2:Z1000")
    google_service.upload_values(loa_package, "'LoA_raw'!A2:Z1000")
    logger.info(f"uploaded data for {str(LOA_OPTION.name)} LOA")


def pack_up(loa: list[Asset]) -> list[list[str, bool]]:
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


def backsync_pack_up(loa: list[Asset]) -> list[list[str, bool]]:
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
            "; ".join(asset.access_owner),
            asset.comments,
            asset.department,
            asset.unit,
            "; ".join(asset.department_and_unit)
        ])

    return package


def accept_pool_request(update_packs: list[UpdatePack], google_service: GoogleClient):
    if not IGNORE_PR_OPTION:
        make_pr_lists(google_service, update_packs)

    upload_update_packs(update_packs, google_service, "'PR'!A2:Z1000")

    user_answer = input("should we accept PR? (yes/no): ")

    if user_answer.upper() == "NO":
        logger.info("deleting PR sheets...")
        delete_pr_sheets(google_service, update_packs)
        raise KeyboardInterrupt("something is wrong with PR")
    logger.info("deleting PR sheets...")
    delete_pr_sheets(google_service, update_packs)


def make_pr_lists(google_service: GoogleClient, update_packs: list[UpdatePack]):
    request = {
        "requests": [
            {
                "addSheet": {
                    "properties": {
                        "sheetId": "666",
                        "title": "PR"
                    }
                }
            }
        ]
    }
    bar = IncrementalBar('Countdown', max=len(update_packs))
    for update_pack in update_packs:
        try:
            google_service.batch_update(update_pack.sheet_id, request)
        except Exception as ex:
            logger.error(ex)
        bar.next()
        sleep(1)


def delete_pr_sheets(google_service: GoogleClient, update_packs: list[UpdatePack]):
    request = {
        "requests": [
            {
                "deleteSheet": {
                    "sheetId": "666"
                }
            }
        ]
    }
    bar = IncrementalBar('Countdown', max=len(update_packs))
    for update_pack in update_packs:
        try:
            google_service.batch_update(update_pack.sheet_id, request)
        except Exception as ex:
            logger.error(ex)
        bar.next()
        sleep(1)


def loa_backsync(google_service):
    logger.info("performing backsync...")

    general_loa: list = get_general_loa(google_service)

    assets: list[Asset] = parse_to_domain_assets(general_loa)

    surveys_list: list[Survey] = get_surveys(google_service)

    update_packs: list[UpdatePack] = make_update_packs(assets, surveys_list)

    logger.debug("Update packs:")
    pprint(update_packs[40:60])

    if not IGNORE_BACKUP_OPTION:
        make_survey_backups(google_service, surveys_list)

    accept_pool_request(update_packs, google_service)

    # update_surveys(update_packs, google_service)


def get_general_loa(google_service) -> list[any]:
    general_loa_raw = google_service.get_values(CONFIG["links"]["general_loa"], "LoA!A2:Z1000")["values"]
    return general_loa_raw


def parse_to_domain_assets(general_loa: list[any]) -> list[Asset]:
    return [Asset.make_from_loa_asset(loa_asset) for loa_asset in general_loa]


def make_update_packs(loa: list[Asset], surveys_list: list[Survey]) -> list[UpdatePack]:
    """
    :param surveys_list: верхнеуровневый лист с анкетами, базовая инфа
    :param loa: тут лежат доменные ассеты
    :return: вернуть нужно лист пакетов обновления
    """
    update_pack_dict: dict[str, UpdatePack] = dict()

    for survey in surveys_list:
        update_pack_dict[f"{survey.department.strip()} {survey.unit.strip()}"] = UpdatePack(
            sheet_id=survey.link,
            full_unit=f"{survey.department.strip()} {survey.unit.strip()}",
            assets=list()
        )

    for asset in loa:
        for unit in asset.department_and_unit:
            if bool(update_pack_dict.get(unit)):
                update_pack_dict[unit].assets.append(asset)

    resulting = list(update_pack_dict.values())

    return resulting


def make_survey_backups(google_service: GoogleClient, surveys: list[Survey]):
    """
    :return: ничего не возвращаем
    """
    bar = IncrementalBar('Countdown', max=len(surveys))
    for survey in surveys:
        try:
            response = google_service.get_values(survey.link, "'Лист1'!A1:Z1000")

            body = {
                "majorDimension": "ROWS",
                "range": "'backup'!A1:Z1000",
                "values": response['values']
            }

            response_for_copy = google_service.update_range(survey.link,
                                                            "'backup'!A1:Z1000",
                                                            body)
            logger.info(response_for_copy)
        except Exception as ex:
            logger.error(ex)
        bar.next()
        sleep(1)
    logger.info("made backups")


def update_surveys(update_packs: list[UpdatePack], google_client: GoogleClient):
    upload_update_packs(update_packs, google_client, "'Лист1'!A2:Z1000")


def upload_update_packs(update_packs: list[UpdatePack], google_client: GoogleClient, range: str):
    """
        :param google_client: клиент для общения с гуглом, тут загружаем значения в таблы
        :param update_packs: пакеты обновлений, тут есть все, что нужно
        :return: ничего не возвращаем
        """
    logger.info("uploading updating packs...")
    bar = IncrementalBar('Countdown', max=len(update_packs))
    for update_pack in update_packs:
        try:
            print('\n')
            logger.debug(f"trying to WIPE range on {update_pack.full_unit}, {update_pack.sheet_id}")

            google_client.wipe_range(spreadsheet_id=update_pack.sheet_id,
                                     range=range)

            print('\n')
            logger.debug(f"trying to UPDATE range on {update_pack.full_unit}, {update_pack.sheet_id}")

            logger.debug(f"backsync packup for {update_pack.full_unit}, {update_pack.sheet_id}")
            pprint(backsync_pack_up(update_pack.assets))

            google_client.update_range(update_pack.sheet_id,
                                       range=range,
                                       body={"majorDimension": "ROWS",
                                             "range": range,
                                             "values": backsync_pack_up(update_pack.assets)})

        except Exception as ex:
            print('\n')
            logger.error(ex)
        bar.next()
        sleep(1)


def loa_clean(google_service):
    logger.info("performing cleaning on PR sheets...")

    general_loa: list = get_general_loa(google_service)

    assets: list[Asset] = parse_to_domain_assets(general_loa)

    surveys_list: list[Survey] = get_surveys(google_service)

    update_packs: list[UpdatePack] = make_update_packs(assets, surveys_list)

    delete_pr_sheets(google_service, update_packs)


def main() -> bool:
    google_service = build_google_service(PATH)

    match MODE:
        case Modes.COLLECT:
            loa_collect(google_service)
        case Modes.BACKSYNC:
            loa_backsync(google_service)
        case Modes.CLEAR:
            loa_clean(google_service)
        case _:
            raise NotImplemented("There is no such mode yet")

    return True


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Script to compute LOA, check README")
    parser.add_argument("-c", "--cache", action="store_true",
                        help="Pass this flag if you want to perform collect mode from cache")
    parser.add_argument("-b", "--ignore-backup", dest="ignore_backup", action="store_true",
                        help="Pass this flag if you want to perform backsync without backup")
    parser.add_argument("-p", "--ignore-pr", dest="ignore_pr", action="store_true",
                        help="Pass this flag if you want to perform backsync without creating pr — "
                             "ONLY FOR DEBUG PURPOSES")
    parser.add_argument("-d", "--domain", type=str, default="GENERAL",
                        help="Enter name of domain for which you want to collect LOA, "
                             "for example, \"DE\", \"Finance\" etc. GENERAL is default value. "
                             "Make sure that you configured link to spreadsheet in config.jsom")
    parser.add_argument("--mode", metavar="MODE", type=str, choices=["collect", "backsync", "clear"],
                        default="COLLECT",
                        help="\"Collect\" - creates list of assets from surveys, that is default mode. "
                             "\"Backsync\" - performs update on surveys by info from the general LOA. "
                             "\"Clear\" - performs deletion of PR lists")
    args = parser.parse_args()

    CACHE_OPTION = args.cache
    IGNORE_BACKUP_OPTION = args.ignore_backup
    IGNORE_PR_OPTION = args.ignore_pr

    match args.mode.upper():
        case "BACKSYNC" | "BS" | "BACK_SYNC" | "BACK_SYNCHRONIZATION":
            MODE = Modes.BACKSYNC
        case "CLEAR" | "CLEAN":
            MODE = Modes.CLEAR
        case _:
            MODE = Modes.COLLECT

    match args.domain.upper():
        case "DE" | "ENGINEERING" | "DODO ENGINEERING":
            LOA_OPTION = LoaOptions.ENGINEERING
        case "FN" | "FINANCE":
            LOA_OPTION = LoaOptions.FINANCE
        case "DPEU" | "DODO PIZZA EURASIA" | "DODO_PIZZA_EURASIA":
            LOA_OPTION = LoaOptions.DODO_PIZZA_EURASIA
        case "CRP" | "CORPORATE":
            LOA_OPTION = LoaOptions.CORPORATE
        case "IMF":
            LOA_OPTION = LoaOptions.IMF
        case "MRKT" | "MARKETING":
            LOA_OPTION = LoaOptions.MARKETING
        case "DI" | "DRINKIT":
            LOA_OPTION = LoaOptions.DRINKIT
        case "KB" | "KEBSTER":
            LOA_OPTION = LoaOptions.KEBSTER
        case "MNS" | "MENUSA":
            LOA_OPTION = LoaOptions.MENUSA
        case "DIUAE" | "DRINKIT UAE" | "DRINKIT_UAE":
            LOA_OPTION = LoaOptions.DRINKIT_UAE
        case "DPUAE" | "DODO PIZZA UAE" | "DODO_PIZZA_UAE":
            LOA_OPTION = LoaOptions.DODO_PIZZA_UAE
        case _:
            LOA_OPTION = LoaOptions.GENERAL

    logger.info(f"{MODE=}")
    logger.info(f"{LOA_OPTION=}")

    is_ok = main()

    if is_ok:
        logger.info("everything's done, shutting down...")
    else:
        raise Exception("mode function didn't do what's it paid for")
