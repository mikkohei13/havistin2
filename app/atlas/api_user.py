
import atlas.common as common

def user(user_id):
    api_url = f"https://api.laji.fi/v0/person/by-id/{user_id}?access_token="

    data = common.fetch_finbif_api(api_url)
    return data

def main(id_untrusted):
    data = user(id_untrusted)
    return data


