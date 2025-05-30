# Flask - Used to build the web app.
# difflib - For fuzzy string matching
# pickle - Loads pre-trained models


from flask import Flask, render_template, request, jsonify
import pickle
import numpy as np
import pandas as pd
import difflib
from chatbot_logic import get_chatbot_response


popular_df = pd.read_pickle(open('model/popular.pkl','rb'))
pt = pd.read_pickle(open('model/pt.pkl','rb'))
books = pd.read_pickle(open('model/books.pkl','rb'))
similarity_scores = pd.read_pickle(open('model/similarity_scores.pkl','rb'))

app = Flask(__name__)


# Home
@app.route('/')
def index():
    return render_template('index.html',
                           book_name=list(popular_df['Book-Title'].values),
                           author=list(popular_df['Book-Author'].values),
                           image=list(popular_df['Image-URL-M'].values),
                           votes=list(popular_df['num_ratings'].values),
                           rating=list(popular_df['avg_rating'].values))


# Autocomplete - Helps the front end suggest book titles as the user types.
@app.route('/autocomplete', methods=['GET'])
def autocomplete():
    query = request.args.get('query')
    if query:
        # Use fuzzy string matching to find close matches
        matches = difflib.get_close_matches(query, pt.index.tolist(), n=5, cutoff=0.6)
        return jsonify(matches)
    return jsonify([])


# Recommend Books
@app.route('/recommend')
def recommend_ui():
    return render_template('recommend.html')

@app.route('/recommend_books', methods=['POST'])
def recommend():
    user_input = request.form.get('user_input', '').strip()
    user_input = ' '.join(user_input.split())  # Clean extra whitespace

    # Use fuzzy matching to find best match
    best_matches = difflib.get_close_matches(user_input, pt.index.tolist(), n=1, cutoff=0.6)

    if not best_matches:
        return render_template('recommend.html', error="Book not found. Please check the title and try again.")

    matched_title = best_matches[0]
    index = pt.index.tolist().index(matched_title)

    similar_items = sorted(list(enumerate(similarity_scores[index])), key=lambda x: x[1], reverse=True)[1:5]

    data = []
    for i in similar_items:
        temp_df = books[books['Book-Title'] == pt.index[i[0]]].drop_duplicates('Book-Title')
        if not temp_df.empty:
            item = [
                temp_df['Book-Title'].values[0],
                temp_df['Book-Author'].values[0],
                temp_df['Image-URL-M'].values[0]
            ]
            data.append(item)

    return render_template('recommend.html', data=data)


# Chatbot
# GET - retrieve data from the server
# POST - send data to the server

@app.route('/chatbot', methods=['GET', 'POST'])
def chatbot():
    response = None
    if request.method == 'POST':
        user_input = request.form.get('user_input')
        response = get_chatbot_response(user_input)
    return render_template('chatbot.html', response=response)

if __name__ == '__main__':
    app.run(debug=True)
