from loguru import logger


def loa_clean(google_service):
    logger.info("performing cleaning on PR sheets...")

    general_loa: list = get_general_loa(google_service)

    assets: list[Asset] = parse_to_domain_assets(general_loa)

    surveys_list: list[Survey] = get_surveys(google_service)

    update_packs: list[UpdatePack] = make_update_packs(assets, surveys_list)

    delete_pr_sheets(google_service, update_packs)