import uuid
import warnings
import plotly.graph_objs as go
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    import plotly.offline as plotly


plotly.offline.init_notebook_mode()


_my_uuid_counter = 0


def _my_uuid():
    global _my_uuid_counter
    _my_uuid_counter += 1
    return "_my_uuid_counter" + str(_my_uuid_counter-1)


uuid.uuid4 = _my_uuid


def scatter(df, xName, yName, label_column=None, bool_column=None):
    if label_column is None:
        sub_dfs = [("", df)]
    else:
        sub_dfs = [
            (label, df.loc[df[label_column] == label]) for label in df[label_column].unique()
        ]

    data = [
        go.Scatter(
            x=sub_df[xName],
            y=sub_df[yName],
            text=sub_df.index,
            mode="markers",
            marker=dict(
                symbol="circle"
                       if bool_column is None else
                       ["circle" if i else "x" for i in sub_df[bool_column]]
            ),
            name=label
        )
        for label, sub_df in sub_dfs
    ]

    layout = dict(
        title=label_column if label_column is not None else "Scatterplot",
        xaxis=dict(title=xName),
        yaxis=dict(title=yName),
        showlegend=label_column is not None,
        hovermode="closest"
    )
    return plotly.iplot(dict(data=data, layout=layout))
