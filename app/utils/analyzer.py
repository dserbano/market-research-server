from utils import Aggregator
from utils.ml import KMeans_Executor, KRLSTracker_Executor

class Analyzer:

    @staticmethod
    def analyzeForecastsSearchVolume(task_id):
        return KRLSTracker_Executor.forecastVolume(task_id, Aggregator.aggregateSearchVolume(task_id))

    @staticmethod
    def analyzeClustersProducts(task_id):
        return KMeans_Executor.clusterProducts(task_id, Aggregator.aggregateProducts(task_id))

