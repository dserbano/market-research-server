from pytrends.request import TrendReq
from tasks.models import Task

class Pytrends_API:

    @staticmethod
    def getKeywords(task_id):
        task = Task.objects.get(id=task_id)
        result = task.from_keywords.split(" ")

        if len(task.keywords) > 0:
            result = task.keywords
        else:
            pytrends_api = TrendReq(hl=str(task.language) + "_" + str(task.location))

            for keyword in result.copy():
                suggestions = pytrends_api.suggestions(keyword=keyword)[:3]
                for suggestion in suggestions:
                    result.append(suggestion["title"])

            for keyword in result.copy():
                pytrends_api.build_payload(kw_list=[keyword], geo=task.location)
                related_queries = pytrends_api.related_queries()
                for i in related_queries.keys():
                    for j in related_queries[i].keys():
                        if related_queries[i][j] is not None:
                            unpack = related_queries[i][j].to_dict()
                            if "query" in unpack:
                                result = result + list(unpack["query"].values())[:15]

                related_topic = pytrends_api.related_topics()
                for i in related_topic.keys():
                    for j in related_topic[i].keys():
                        if related_topic[i][j] is not None:
                            unpack = related_topic[i][j].to_dict()
                            if "topic_title" in unpack:
                                result = result + list(unpack["topic_title"].values())[:15]
            result = list(set(result))[:400]
            task.keywords = list(set(task.keywords + result))
            task.save()

        return result


    @staticmethod
    def getSearchVolume(task_id, keywords):
        task = Task.objects.get(id=task_id)
        keywords_chunks = [keywords[i:i + 5] for i in range(0, len(keywords), 5)]

        result = []

        if len(task.search_volume) > 0:
            result = task.search_volume
        else:
            pytrends_api = TrendReq(hl=str(task.language) + "_" + str(task.location))
            for i in range(0, len(keywords_chunks)):
                pytrends_api.build_payload(kw_list=keywords_chunks[i])
                trends_partial = pytrends_api.interest_over_time().to_dict()
                for keyword in trends_partial.keys():
                    if keyword != "isPartial":
                        dates = list(trends_partial[keyword].keys())
                        volumes = []
                        for date in dates:
                            volumes.append(trends_partial[keyword][date])

                        result.append({
                            "keyword": keyword,
                            "average": sum(volumes)/len(volumes),
                            "monthly_searches": {
                                "dates": list(map(lambda x: x.strftime("%d/%m/%Y"), dates)),
                                "volumes": volumes,
                            }
                        })

            task.search_volume = sorted(result, reverse=True, key=lambda x : x["average"])
            task.save()

        return result

