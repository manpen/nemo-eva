helpers_funcs = ["dicts_to_df", "format_feature_df", "list_as_table", "list_to_dict", "render_dict", "use_paper_data"]
for func in helpers_funcs:
    exec("from helpers.helpers import %s" % func)
