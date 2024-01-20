from domain.asset import Asset
from loguru import logger
from domain.domain import Domain


def domain_filter(assets: list[Asset], domain: Domain = Domain([], [])) -> list[Asset]:
    raw_assets = assets
    filtered_assets = list()

    if domain == Domain([], []):
        return raw_assets

    for asset in raw_assets:
        if asset.department not in domain.departments and asset.unit not in domain.units:
            continue
        else:
            filtered_assets.append(asset)

    return filtered_assets


def loa_handler(assets: list[Asset], domain: Domain) -> list[Asset]:
    resulting: list[Asset] = list()
    added_names = list()

    assets = domain_filter(assets, domain)

    assets.sort(key=lambda x: x.name)

    for asset in assets:
        if asset.name.strip() not in added_names:
            resulting.append(asset)
            added_names.append(asset.name.strip())
        else:
            asset_index = added_names.index(asset.name)

            if asset.is_in_pci_dss_scope:
                resulting[asset_index].is_in_pci_dss_scope = True

            if asset.has_iid_clients:
                resulting[asset_index].has_iid_clients = True

            if asset.has_iid_employees:
                resulting[asset_index].has_iid_employees = True

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


if __name__ == "__main__":
    raw_assets: list[Asset] = list()
    de_domain = Domain(
        units=["IT Eurasia People&Communications", "IT Eurasia B2B", "NSFW (Not safe for work)", "SE (Seven-eleven)",
               "Rocket Science", "k9", "HR Automation", "Slippers of Mimir", "IT Team", "IT"],
        departments=["CVM", "CVM Dev Core", "Vulnerable", "Guilds", "Platform"])

    handled_de_assets = loa_handler(raw_assets, de_domain)
