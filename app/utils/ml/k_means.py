from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import silhouette_score
from tasks.models import Task

class KMeans_Executor:

    @staticmethod
    def clusterProducts(task_id, products):

        result = []
        task = Task.objects.get(id=task_id)

        if len(task.clusters_products) > 0:
            result = task.clusters_products
        else:
            products_lst = [x["name"] + " " + x["price"] + " " + " ".join(x["keywords"]) for x in products]

            vectorizer = TfidfVectorizer(stop_words={'english'})
            X = vectorizer.fit_transform(products_lst)

            sil = []
            kmax = 20

            for k in range(2, kmax + 1):
                kmeans = KMeans(n_clusters=k).fit(X)
                labels = kmeans.labels_
                sil.append(silhouette_score(X, labels, metric='euclidean'))

            optimal_k = sil.index(max(sil)) + 2
            model = KMeans(n_clusters=optimal_k, init='k-means++', max_iter=200, n_init=10)
            model.fit(X)
            labels = model.labels_

            for i in range(0, len(labels)):
                item = [x for x in result if x["cluster"] == str(labels[i])]
                if len(item) > 0:
                    item[0]["keywords"] = list(set(item[0]["keywords"] + products[i]["keywords"]))
                    item[0]["products"].append(products[i])
                else:
                    result.append({
                        "cluster": str(labels[i]),
                        "keywords": products[i]["keywords"],
                        "products": [products[i]]
                    })

            result = list(sorted(result, key=lambda x: int(x["cluster"]), reverse=False))
            task.clusters_products = result
            task.save()
            return result

        return result

