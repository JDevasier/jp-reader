from flask import Flask
from flask import render_template
from flask import request
from flask.json import jsonify
import jp_helper

kanji_helper = jp_helper.KanjiHelper()

app = Flask(__name__)

@app.route("/parse_jp", methods=["POST"])
def parse_jp():
    text = request.get_json().get("text")
    
    if len(text.strip("")) == 0:
        return jsonify(None)
    
    vocab = kanji_helper.parse(text)
    
    return jsonify(vocab)

@app.route("/")
def home():
    return render_template('reader.html', name="test")