import os

from graph_crawler import GraphCrawler
from random_feature_extractor import RandomizedFeatureExtractor
from feature_cleaner import FeatureCleaner
from classifier import Classifier
from csv import DictReader


def run_stages(stages, initial_input_data=None, check_clean=True, **kwargs):
    input_data = initial_input_data
    for i, stage in enumerate(stages):
        print("### STAGE", stage.__name__, "###")
        if check_clean:
            stage_path = stage._stagepath
            if os.path.exists(stage_path) and not os.listdir(stage_path) == []:
                raise RuntimeError(
                    "Make sure the folder %s is empty." % stage_path
                )
        if isinstance(input_data, str):
            with open(input_data) as input_dicts_file:
                input_dicts = list(DictReader(input_dicts_file))
        else:
            input_dicts = input_data
        if input_dicts:
            stage(input_dicts, **kwargs).execute()
        else:
            stage(**kwargs).execute()
        input_data = stage.resultspath


run_stages(
    [
        #GraphCrawler,
        RandomizedFeatureExtractor,
        FeatureCleaner, 
        Classifier
    ],
    GraphCrawler.resultspath,
    #FeatureExtractor.resultspath,
    #FeatureCleaner.resultspath,
    check_clean=False,
    cores=12
)
