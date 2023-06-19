from flask import Flask, jsonify
import math
import re
from flask import session
from flask import Flask, render_template, request, jsonify
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from math import ceil

def load_vocab():
    vocab = {}
    with open("vocab.txt", "r") as f:
        vocab_terms = f.readlines()
    with open("idf-values.txt", "r") as f:
        idf_values = f.readlines()

    for (term, idf_value) in zip(vocab_terms, idf_values):
        vocab[term.rstrip()] = int(idf_value.rstrip())

    return vocab


def load_document():
    with open("document.txt", "r") as f:
        documents = f.readlines()

    # print('Number of documents: ', len(documents))
    # print('Sample document: ', documents[0])
    return documents


def load_inverted_index():
    inverted_index = {}
    with open('inverted_index.txt', 'r') as f:
        inverted_index_terms = f.readlines()

    for row_num in range(0, len(inverted_index_terms), 2):
        term = inverted_index_terms[row_num].strip()
        documents = inverted_index_terms[row_num+1].strip().split()
        inverted_index[term] = documents

    # print('Size of inverted index: ', len(inverted_index))
    return inverted_index


def load_link_of_qs():
    with open("Leetcode-Questions-Scrapper/Qdata/Qindex.txt", "r") as f:
        links = f.readlines()

    return links


vocab = load_vocab()            # vocab : idf_values
document = load_document()
inverted_index = load_inverted_index()
Qlink = load_link_of_qs()


def get_tf_dict(term):
    tf_dict = {}
    if term in inverted_index:
        for doc in inverted_index[term]:
            if doc not in tf_dict:
                tf_dict[doc] = 1
            else:
                tf_dict[doc] += 1

    for doc in tf_dict:
        # dividing the freq of the word in doc with the total no of words in doc indexed document
        try:
            tf_dict[doc] /= len(document[int(doc)])
        except (ZeroDivisionError, ValueError, IndexError) as e:
            print(e)
            print(doc)

    return tf_dict


def get_idf_value(term):
    return math.log((1 + len(document)) / (1 + vocab[term]))


def calc_docs_sorted_order(q_terms):
    potential_docs = {}
    ans = [] # will store the set of documents containing each term

    for term in q_terms:
        if term not in vocab:
            continue

        tf_vals_by_docs = get_tf_dict(term)
        idf_value = get_idf_value(term)
        docs_for_term = set(tf_vals_by_docs.keys()) # get the documents containing this term
        ans.append(docs_for_term)

        for doc in tf_vals_by_docs:
            if doc not in potential_docs:
                potential_docs[doc] = tf_vals_by_docs[doc]*idf_value
            else:
                potential_docs[doc] += tf_vals_by_docs[doc]*idf_value

    if ans:
        docs_with_all_terms = set.intersection(*ans)
    else:
        docs_with_all_terms = set()

    # Filter potential_docs to only contain the documents with all terms
    potential_docs = {doc: score for doc, score in potential_docs.items() if doc in docs_with_all_terms}


        # print(potential_docs)
        # divide the scores of each doc with no of query terms
    for doc in potential_docs:
        potential_docs[doc] /= len(q_terms)

        # sort in dec order acc to values calculated
    potential_docs = dict(
        sorted(potential_docs.items(), key=lambda item: item[1], reverse=True))

        # if no doc found
    if (len(potential_docs) == 0):
        print("No matching question found. Please search with more relevant terms.")

        # Printing ans
        # print("The Question links in Decreasing Order of Relevance are: \n")
    for doc_index in potential_docs:
        tempQlink=Qlink[int(
            doc_index) - 1][:-2]
        question_title=tempQlink.split('/')[4]
        pro_q_title=question_title.split('-')
        string=pro_q_title[0]
        modified_string = string[0].upper() + string[1:]
        pro_q_title[0]=modified_string
        fin_str=""
        for strings in pro_q_title:
            fin_str+=strings+" "
        print(fin_str)
        ans.append({"Question Link": Qlink[int(
            doc_index) - 1][:-2], "Question title":fin_str, "img source": "leetcode.jpg", "Score": potential_docs[doc_index]})
    return ans


app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
# query = input('Enter your query: ')
# q_terms = [term.lower() for term in query.strip().split()]

# print(q_terms)
# print(calc_docs_sorted_order(q_terms)[0])
# print(len(calc_docs_sorted_order(q_terms)))


class SearchForm(FlaskForm):
    search = StringField('Enter your search term')
    submit = SubmitField('Search')


@app.route("/<query>")
def return_links(query):
    q_terms = [term.lower() for term in query.strip().split()]
    return jsonify(calc_docs_sorted_order(q_terms)[:20:])


@app.route("/", methods=['GET', 'POST'])
def home():
    form = SearchForm()
    results = []
    page = request.args.get('page', 1, type=int)
    per_page = 15  # Change to 50 results per page
    total_pages = 0  # Set total pages to 0 initially

    if form.validate_on_submit():
        session['query'] = form.search.data  # Store the search term in session
    elif request.args.get('query'):  # Check if there is a query parameter in the URL
        session['query'] = request.args.get('query')  # Update the session with the URL's query parameter
    else:
        session['query'] = None  # Explicitly set to None if no valid query is present

    if session['query']:  # If session['query'] is not None then only proceed with search
        q_terms = [term.lower() for term in session['query'].strip().split()]
        all_results = calc_docs_sorted_order(q_terms)
        total_pages = math.ceil(len(all_results) / per_page)
        paginated_results = all_results[(page-1)*per_page: page*per_page]
        results = paginated_results

    return render_template('index.html', form=form, results=results, page=page, total_pages=total_pages, per_page=per_page)



if __name__ == "__main__":
    app.run(debug=True)   
# this is the backend code - modify it to display 50 responses per page and next 50 in other and so on