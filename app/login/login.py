

from helpers import common_helpers


def main(person_token_untrusted):
    html = dict()
    
    html["test"] = "Token: " + person_token_untrusted

    return html
