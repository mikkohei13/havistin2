import datetime


def main():
    current_year = datetime.datetime.now().year
    years = [current_year, current_year - 1, current_year - 2]
    return {"current_year": current_year, "years": years}
