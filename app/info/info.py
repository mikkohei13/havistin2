


import app_secrets

def main():
    html = dict()
    html["bird_secret"] = app_secrets.bird_secret
    print(html)
    return html
