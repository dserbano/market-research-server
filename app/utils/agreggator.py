from utils.api import Pytrends_API, Wikipedia_API, MercadoLibre_API

class Aggregator:

    @staticmethod
    def aggregateKeywords(task_id):
        keywords = Pytrends_API.getKeywords(task_id)
        return keywords

    @staticmethod
    def aggregateBusinesses(task_id):
        keywords = Aggregator.aggregateKeywords(task_id)
        return Wikipedia_API.getBusinesses(task_id, keywords)

    @staticmethod
    def aggregateProducts(task_id):
        businesses = Aggregator.aggregateBusinesses(task_id)
        keywords = []
        for business in businesses:
            keywords = keywords + business["keywords"]
        return MercadoLibre_API.getProducts(task_id, list(set(keywords)))

    @staticmethod
    def aggregateSearchVolume(task_id):
        keywords = Aggregator.aggregateKeywords(task_id)
        return Pytrends_API.getSearchVolume(task_id, keywords)