from datetime import datetime

def main():
    html = dict()
    html["current_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return html 