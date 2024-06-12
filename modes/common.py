def get_general_loa(google_service) -> list[any]:
    general_loa_raw = google_service.get_values(CONFIG["links"]["general_loa"], "LoA!A2:Z1000")["values"]
    return general_loa_raw