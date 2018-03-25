helpers_funcs = ["data_path", "list_as_table", "list_to_dict", "render_dict"]
for func in helpers_funcs:
    print(func)
    exec('from helpers.helpers import %s' % func)
