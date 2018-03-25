import uuid
import IPython.display
import json

_render_dict_counter = 0


def data_path():
    return "../../data/"


def list_to_dict(a_list, delimiter):
    the_dict = {}
    for entry in a_list:
        path = entry.split(delimiter)
        value_holder = the_dict
        for key in path[:-1]:
            value_holder = value_holder.setdefault(key, {})
        value_holder[path[-1]] = 0
    return the_dict


def render_dict(a_dict):
    global _render_dict_counter
    my_uuid = "render_dict_" + str(_render_dict_counter)  # str(uuid.uuid4())
    _render_dict_counter += 1
    IPython.display.display_html('<div id="{}" style="height: 600px; width:100%;"></div>'.format(my_uuid), raw=True)
    IPython.display.display_javascript("""
    require(["./helpers/renderjson.js"], function() {
      document.getElementById('%s').appendChild(renderjson(%s))
    });
    """ % (my_uuid, json.dumps(a_dict, sort_keys=True)), raw=True)


def list_as_table(a_list, col_width=20, cols=5):
    cell_format = "|{:" + str(col_width) + "." + str(col_width) + "}|"
    return ((cell_format*cols + "\n")*(len(a_list)//cols) + cell_format * (len(a_list) % cols)).format(*a_list)
