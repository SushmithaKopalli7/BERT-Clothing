from flask import Flask, jsonify, render_template
from flask import request, render_template
from collections import OrderedDict
from gensim.summarization import keywords
from gensim.summarization import summarize
from stemming.porter2 import stem
from flask_cors import CORS, cross_origin
from bert import Ner
# from reviewModel import reviewModel
# from ClothingNerBert import Bert

import spacy
import operator
import re

from bert_serving.client import BertClient
from util import cosine_similarity

app = Flask(__name__)
cors = CORS(app, resources={r"/tags": {"origins": "http://localhost:port"}})

nlp = spacy.load('en_core_web_sm')
clothModel = Ner("C:/Users/NLP/Desktop/BERT-MSC/BERT")

@app.route("/hello")
def check():
    return "Hii......"

def keyWordExtraction(text):
    try:
        return (keywords(text, words=10)).replace("\n", " , ")
    except:
        return (keywords(text)).replace("\n", "  ")


def ClothingNer(description):
    seo = {}
    storage = []
    clothing_Entities = {}
    category = {}
    cat = {}
    marker = set()
    output = clothModel.predict(description)
    for entites in output:
        if entites['tag'] != 'O':
            storage.append(entites)
    washtype = ""
    for i in range(len(storage)):
        itemtype = ""
        try:
            if storage[i].get('tag') == "B-itemtype" and storage[i + 1].get('tag') == "I-itemtype":
                itemtype = itemtype + " " + storage[i].get('word') + storage[i + 1].get('word')
                clothing_Entities.setdefault(storage[i].get('tag'), []).append(itemtype)
        except:
            print("some error----------------------------->")
    value = ""
    for entites in storage:
        if entites['tag'] == "B-washtype" or entites['tag'] == "I-washtype":
            washtype = washtype + entites['word']
        else:
            clothing_Entities.setdefault(entites['tag'], []).append(entites['word'])

    clothing_Entities.setdefault("washtype", []).append(washtype)
    depulates = clothing_Entities
    for items in depulates:
        result = []
        for l in depulates[items]:
            ll = l.lower()
            if ll not in marker:  # test presence
                marker.add(ll)
                result.append(l)
        if len(result) != 0:
            clothing_Entities[items] = result
    try:
        del clothing_Entities['I-target']
    except:
        print("indie the except due to keyerror")
    cat.setdefault("Category-1", []).append("Clothing")
    try:
        cat.setdefault("Category-2", []).append(clothing_Entities['B-target'])
    except:
        print("indie the except due to keyerror")
    try:
        cat.setdefault("Category-3", []).append(clothing_Entities['B-itemtype'])
    except:
        print("indie the except due to keyerror")
    category.setdefault("Category", []).append(cat)
    category.setdefault("Entiites", []).append(clothing_Entities)
    seo.setdefault("KeyWords", []).append(keyWordExtraction(description))
    try:
        seo.setdefault("KeyWords", []).append(clothing_Entities['B-color'])
    except:
        print("inside seo url try catch block")
    try:
        seo.setdefault("KeyWords", []).append(clothing_Entities['B-fabric'])
    except:
        print("inside seo url try catch block")
    try:
        seo.setdefault("KeyWords", []).append(clothing_Entities['B-occasion'])
    except:
        print("inside seo url try catch block")
    try:
        seo.setdefault("KeyWords", []).append(clothing_Entities['B-target'])
    except:
        print("inside seo url try catch block")
    try:
        seo.setdefault("KeyWords", []).append(clothing_Entities['B-itemtype'])
    except:
        print("inside seo url try catch block")

    # des=seo.setdefault("Meta_Description", []).append(model(description))
    # if des=='':
    #     seo.setdefault("Meta_Description", []).append(description)
    # else:
    #     seo.setdefault("Meta_Description", []).append(des)
    try:
        seo.setdefault("Meta_Description", []).append(summarize(description))
        print(summarize(description))
    except:
        seo.setdefault("Meta_Description", []).append(description)

    value = "Clothing_"
    try:
        value = value + clothing_Entities['B-target'][0]
    except:
        print("Not found")
    value = value + "_"
    try:
        value = value + clothing_Entities['B-itemtype'][0]
    except:
        print("Not found")
    if value.endswith("_"):
        value.replace(value[len(value)],"")
    seo.setdefault("SEO_URL", []).append(value)
    category.setdefault("SEO", []).append(seo)

    return category

@app.route("/bert/clothing")
@cross_origin(origin='localhost', headers=['Content- Type', 'Authorization'])
def bertClothing():
    return render_template("bertIndex.html")


@app.route("/clothBert")
@cross_origin(origin='localhost', headers=['Content- Type', 'Authorization'])
def bertClothingRedirection():
    return render_template("redirection.html")

@app.route("/words")
@cross_origin(origin='localhost', headers=['Content- Type', 'Authorization'])
def similarityMainPage():
    return render_template("similarity.html")


@app.route("/Clothing", methods=['POST'])
@cross_origin(origin='localhost', headers=['Content- Type', 'Authorization'])
def clothingEntity():
    req_data = request.get_json()
    description = req_data['description']
    return jsonify(ClothingNer(description))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
