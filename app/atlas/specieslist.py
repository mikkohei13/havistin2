
import atlas.common as common

def get_species_list():
    species_list = common.read_json_to_dict("atlas-species.json")
#    common.print_log(species_list)

    html = "<ul>\n"

    for key, value in species_list.items():
        common.print_log(key)
        html += "  <li><a href='/atlas/laji/" + key + "'>" + key.capitalize() + "</a></li>\n"

    html += "</ul>\n"
    return html

def main():
    html = dict()
    html["species_list"] = get_species_list()

    return html
