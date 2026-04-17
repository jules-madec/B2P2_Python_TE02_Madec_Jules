import requests
import csv
import json
import pandas


def get_json(url, limit, page):
    try:
        response = requests.get(
            url + "/products.json" + "?" + "page=" + page + "&" + "limit=" + limit
        )
        a = response.json()["products"]
        return a
    except requests.ConnectionError as e:
        print(f"Connexion impossible : {str(e)}")
    except requests.Timeout as e:
        print(f"Délai dépassé{str(e)}")
    except requests.HTTPError as e:
        print(f"Erreur http :{str(e)}")


def json_to_df(json):

    dataframe = pandas.DataFrame(json)
    return dataframe


def get_products(url):
    boollean = True
    a = 1
    dataframe = pandas.DataFrame()

    while boollean == True:
        data = json_to_df(get_json(url, "0", str(a)))

        if len(data) == 0:
            print("tout est finie")
            boollean = False

        else:
            dataframe = pandas.concat([dataframe, data], ignore_index=True)
            a += 1

    return dataframe


def get_variants(df_products):
    rows = []

    for index, product in df_products.iterrows():

        variants = product["variants"]
        images = product["images"]
        options = product["options"]

        for variant in variants:

            row = {}

            row["ID"] = variant["id"]
            row["Type"] = "variation"
            row["SKU"] = variant["sku"]
            row["Name"] = variant["title"]
            row["Published"] = 1 if variant["available"] else 0
            row["Is featured?"] = 1 if variant["featured_image"] else 0
            row["Visibility in catalog"] = "visible"
            row["description"] = product["body_html"]
            row["Tax class"] = "standard"
            row["Weight (lbs)"] = variant["grams"]
            row["Sale price"] = variant["price"]
            row["Regular price"] = variant["compare_at_price"]
            row["Tags"] = product["tags"]
            row["Position"] = variant["position"]

            if variant["requires_shipping"] == True:
                row["Tax status"] = "shipping"
            elif variant["taxable"] == True:
                row["Tax status"] = "taxable"
            else:
                row["Tax status"] = "none"

            variant_images = []
            for image in images:
                if variant["id"] in image["variant_ids"]:
                    variant_images.append(image["src"])
            row["Images"] = ", ".join(variant_images)

            for option in options:
                pos = option["position"]
                row[f"Attribute {pos} name"] = option["name"]
                row[f"Attribute {pos} value(s)"] = variant[f"option{pos}"]

            rows.append(row)

    df_variants = pandas.DataFrame(rows).reset_index(drop=True)
    return df_variants


def get_csv(df_variants):
    df_variants.to_csv("products.csv", index=False)


products_df = get_products("https://takoon.com")
variants_df = get_variants(products_df)
get_csv(variants_df)

print(f"{len(products_df)} produits")
print(f"{len(variants_df)} variantes")
