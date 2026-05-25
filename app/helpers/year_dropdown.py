import datetime


def generate_year_dropdown(start_year):
    current_year = datetime.datetime.now().year
    html_options = []

    for year in range(current_year, (start_year - 1), -1):
        html_options.append('<option value="{0}">{0}</option>'.format(year))

    return "\n".join(html_options)
