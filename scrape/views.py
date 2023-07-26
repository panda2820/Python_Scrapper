import csv
import io
import json
import time
from urllib.parse import urlencode
from bs4 import BeautifulSoup
from django.shortcuts import render
from django.http import HttpResponse,JsonResponse
from flask import request, jsonify
import selectorlib
import requests
import pandas as pd
import requests
from django.views.decorators.csrf import csrf_exempt
# Amazon


@csrf_exempt
def scrape_amazon_reviews(request):    
    if request.method=='POST':
        item_id = request.POST.get('item_id')
        cntry = request.POST.get('cntry')
        page = 1
        url = "https://amazon-product-reviews-keywords.p.rapidapi.com/product/reviews"

        querystring = {"asin":item_id,"country":cntry,"variants":page,"top":"0"}

        headers = {
            "X-RapidAPI-Key": "24b5c5ae2fmsh1cb36b5405fd7dep1cc41ajsn65803d27984a",
            "X-RapidAPI-Host": "amazon-product-reviews-keywords.p.rapidapi.com"
        }

    #     response = requests.get(url, headers=headers, params=querystring)
    #     data = json.loads(response.text)
    #     # print(data)
    #     reviews = data["reviews"]

    # # Create the CSV file
    # response = HttpResponse(content_type="text/csv")
    # response["Content-Disposition"] = f'attachment; filename="reviews of {cntry}.csv"'

    # writer = csv.writer(response)
    # writer.writerow(["name", "title", "rating", "review"])

    # for review in reviews:
    #     writer.writerow([review["name"], review["title"], review["rating"], review["review"]])
    # return response
    consective_check = 0
    while consective_check<3:
            response = requests.get(url, headers=headers, params=querystring)
            data = json.loads(response.text)
            reviews = data.get("reviews", [])

            if len(reviews) == 0:
                consective_check+=1
                continue  
            
            # Create the CSV file
            response = HttpResponse(content_type="text/csv")
            response["Content-Disposition"] = f'attachment; filename="reviews of {cntry}.csv"'

            writer = csv.writer(response)
            writer.writerow(["name", "title", "rating", "review"])

            for review in reviews:
                writer.writerow([review.get("name"), review.get("title"), review.get("rating"), review.get("review")])

            return response



# B&N
@csrf_exempt
def scrape_bn_reviews(request):
    if request.method=='POST':
        item_id = request.POST.get('item_id')
        url = f'https://api.bazaarvoice.com/data/batch.json?passkey=caC2Xb0kazery1Vgcza74qqETLsDbclQWr3kbWiGXSvjI&apiversion=5.5&displaycode=19386_1_0-en_us&resource.q1=reviews&filter.q1=isratingsonly%3Aeq%3Afalse&filter.q1=productid%3Aeq%3A{item_id}&filter.q1=contentlocale%3Aeq%3Aen*%2Cen_US&sort.q1=relevancy%3Aa1&stats.q1=reviews&filteredstats.q1=reviews&include.q1=authors%2Cproducts%2Ccomments&filter_reviews.q1=contentlocale%3Aeq%3Aen*%2Cen_US&filter_reviewcomments.q1=contentlocale%3Aeq%3Aen*%2Cen_US&filter_comments.q1=contentlocale%3Aeq%3Aen*%2Cen_US&limit.q1=100&offset.q1=0&limit_comments.q1=3'
        response = requests.get(url)
        # this is assuming the response has no errors and is status code 200
        json_response = response.json()
        json_string = json.dumps(json_response)
        data = json.loads(json_string)
        Results = data['BatchedResults']['q1']["Results"]
        # print(Results)

        # Create the CSV file
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="reviews.csv"'

        writer = csv.writer(response)
        writer.writerow(["UserNickname", "Title", "Rating", "ReviewText"])

        for Result in Results:
            writer.writerow([Result.get("UserNickname", ""), Result.get("Title", ""), Result.get("Rating", ""), Result.get("ReviewText", "")])
        return response


@csrf_exempt
def index(request):
    if request.method == 'POST':
        source = request.POST.get('source')
        print("Source:::" + source)
        if source == 'amazon':
            return scrape_amazon_reviews(request)
        elif source == 'bn':
            return scrape_bn_reviews(request)
        else:
            return HttpResponse('Invalid source selected.')
    else:
        return render(request, 'index.html')
