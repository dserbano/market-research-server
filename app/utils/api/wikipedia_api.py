import wikipedia, re, wptools
from tasks.models import Task
from urlextract import URLExtract


class Wikipedia_API:

    # get trends from Google
    @staticmethod
    def getBusinesses(task_id, keywords):
        task = Task.objects.get(id=task_id)

        result = []

        if len(task.businesses) > 0:
            result = task.businesses
        else:
            extractor = URLExtract()

            for keyword in keywords:
                businesses = wikipedia.search(keyword)[:4]
                for business in businesses:
                    item = [x for x in result if x["name"] == business]
                    if len(item) > 0:
                        item[0]["keywords"].append(keyword)
                    else:
                        infobox = wptools.page(business, lang=task.language).get_parse(show = False).data['infobox']

                        if infobox is not None and "type" in infobox and ("company" in infobox["type"].lower() or "subsidiary" in infobox["type"].lower() or "business" in infobox["type"].lower()):
                            for param in infobox.keys():
                                if param in ["homepage", "website"]:
                                    infobox[param] = extractor.find_urls(infobox[param])
                                    for i in range(0, len(infobox[param])):
                                        infobox[param][i] = infobox[param][i].replace("}", "").replace("{", "")
                                else:
                                    infobox[param] =  re.sub(r'[^\w]', ' ', infobox[param])
                                    infobox[param] = ' '.join(infobox[param].split())

                            infobox_type = infobox["type"] if "type" in infobox else ""
                            infobox_industry = infobox["industry"] if "industry" in infobox else ""
                            infobox_divisions = infobox["divisions"] if "divisions" in infobox else ""
                            infobox_location = infobox["location"] if "location" in infobox else ""
                            infobox_location_city = infobox["location_city"] if "location_city" in infobox else ""
                            infobox_coountry = infobox["coountry"] if "coountry" in infobox else ""
                            infobox_homepage = infobox["homepage"] if "homepage" in infobox else []
                            infobox_website = infobox["website"] if "website" in infobox else []
                            infobox_key_people = infobox["key_people"] if "key_people" in infobox else ""
                            infobox_founder = infobox["founder"] if "founder" in infobox else ""
                            infobox_founded = infobox["founded"] if "founded" in infobox else ""
                            infobox_foundation = infobox["foundation"] if "foundation" in infobox else ""
                            infobox_products = infobox["products"] if "products" in infobox else ""


                            result.append({
                                "name": business,
                                "type": infobox_type,
                                "industry": infobox_industry + " " + infobox_divisions,
                                "location": infobox_location + " " + infobox_location_city + " " + infobox_coountry,
                                "websites": infobox_homepage + infobox_website,
                                "key_people": infobox_key_people + " " + infobox_founder,
                                "founded": infobox_founded + " " + infobox_foundation,
                                "products": infobox_products,
                                "keywords": [keyword]
                            })

            task.businesses = result
            task.save()

        return result




