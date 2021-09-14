from tasks.models import Task
import requests, bs4

class MercadoLibre_API:

    # get trends from Google
    @staticmethod
    def getProducts(task_id, keywords):
        result = []
        task = Task.objects.get(id=task_id)

        if len(task.products) > 0:
            result = task.products
        else:
            for keyword in keywords:
                location = 'co'
                if task.location.lower() in ["ar", "bo", "br", "cl", "co", "cr", "do", "mx", "co", "ec", "gt", "hn", "pe", "pa", "uy", "ve"]:
                    location = task.location

                link = "https://listado.mercadolibre.com." + location + "/" + keyword.replace(' ', '-')
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36'}
                page = requests.get(link, headers=headers)
                soup = bs4.BeautifulSoup(page.content, 'html.parser')

                items = soup.findAll('li', {'class': 'ui-search-layout__item'})
                titlesDom = [item.find('h2', {'class': 'ui-search-item__title'}) for item in items]
                pricesDom = [item.find('span', {'class': 'price-tag-fraction'}) for item in items]
                urlsDom = [item.find('a', {'class': 'ui-search-item__group__element ui-search-link'}) for item in items]
                imgsDom = [item.find('img', {'class': 'ui-search-result-image__element'}) for item in items]

                titles = []
                prices = []
                urls = []
                imgs = []

                for j in range(0, len(titlesDom)):
                    titles.append(titlesDom[j].text if titlesDom[j] is not None else None)
                    prices.append(pricesDom[j].text.replace(',', '') if pricesDom[j] is not None else None)
                    urls.append(urlsDom[j]['href'] if urlsDom[j] is not None else None)
                    imgs.append(imgsDom[j]['data-src'] if imgsDom[j] is not None else None)

                for j in range(len(titles[:20])):
                    item = [x for x in result if x["name"] == titles[j]]
                    if len(item) > 0:
                        item[0]["keywords"].append(keyword)
                        item[0]["keywords"] = list(set(item[0]["keywords"]))
                    else:
                        result.append({
                            "name": titles[j],
                            "price": prices[j],
                            "url": urls[j],
                            "img": imgs[j],
                            "keywords": [keyword]
                        })

            task.products = result
            task.save()
        return result

