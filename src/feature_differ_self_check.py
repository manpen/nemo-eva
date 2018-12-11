import numpy
import pandas

from functools import reduce

from abstract_stage import AbstractStage
from helpers import dicts_to_df, format_feature_df


class FeatureDifferSelfCheck(AbstractStage):
    _stage = "3-b-diffed_features_self_check"

    def __init__(self, features, **kwargs):
        super(FeatureDifferSelfCheck, self).__init__()
        self.features = features

    def _execute(self):
        df = dicts_to_df(self.features)
        df.sort_index(axis=1, inplace=True)
        format_feature_df(df)

        network_models = sorted(set(filter(lambda model: not model.endswith("-second"), set(df["Model"])))-set(["real-world"]))

        diff_features = df.columns[df.dtypes == float].values
        print("Calculating difference for {} features for {} models...".format(len(diff_features), len(network_models)))

        idx = pandas.IndexSlice
        for model in network_models:
            val_1 = df.loc[idx[:,:,model],diff_features].values
            val_2 = df.loc[idx[:,:,model+"-second"],diff_features].values

            df.loc[idx[:,:,model],diff_features] = val_1 - val_2
            df.loc[idx[:,:,model+"-second"],diff_features] = val_2 - val_1
            print("Done with model {}".format(model))

        for a_dict in df.to_dict("records"):
            self._save_as_csv(a_dict)
