from pyelasticsearch import ElasticSearch
from flask import Flask, request, render_template

app = Flask(__name__)

def get_es_query(search_term, num_results):
    query = {"query":{"query_string":{"query": search_term, "fields":["text"],"use_dis_max": True}},"size":num_results, "sort":[{"created":{"order":"desc"}}],"facets":{"updated_on":{"date_histogram":{"field":"created","interval":"hour"}},"user_mentions":{"terms":{"field":"user_mentions","size":10}}, "hashtags":{"terms":{"field":"hashtags","size":10}}, "sentiment": {"terms":{"field": "sentiment", "size":2}} }}
    return query

@app.route("/")
def hello():
    if not request.args.get('q'):
        return render_template("home.html")

    search_term = request.args.get('q')
    q = get_es_query(search_term, 40)
    es = ElasticSearch("http://localhost:9200")
    results = es.search(q, index='tweets')
    if results['hits']['total'] == 0:
        return render_template("home.html", noresults=True)

    senti = results['facets']['sentiment']['terms']
    pos = 0
    neg = 0
    for i in senti:
        if i['term'] == 4:
            pos = i['count']
        elif i['term'] == 0:
            neg = i['count']

    total = pos + neg
    return render_template("home.html", results=results, sentiment={"pos": pos, "neg": neg, "total": total})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")


