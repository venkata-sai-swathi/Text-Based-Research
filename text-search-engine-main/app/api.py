from app.constants import GC
from app.service import AppService
from flask import Blueprint, jsonify, request, redirect, url_for, render_template
import json



blueprint = Blueprint('search', __name__, template_folder="templates")


@blueprint.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        
        print(request.data)
        requestObject = request.data.decode("utf-8")

        word = json.loads(requestObject).get('search', None)

        if not word:
            return jsonify({"files": {}, "searchResults": {}})

        print("REQUESTING FOR", word)

        result = GC.LEMMA(word)[0].lemma_

        print("SEARCHING FOR", result)

        response = AppService().searchWord(result)

        return json.dumps(response)
        
    else:

        response = {"files": {}, "searchResults": {}}

        return render_template("search.html", response=json.dumps(response))
