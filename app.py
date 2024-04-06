import flask
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import time

app = flask.Flask(__name__, template_folder='templates')

df2 = pd.read_csv('./model/tmdb.csv')

tfidf = TfidfVectorizer(stop_words='english',analyzer='word')

tfidf_matrix = tfidf.fit_transform(df2['soup'])
print(tfidf_matrix.shape)

cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)
print(cosine_sim.shape)

df2 = df2.reset_index()
indices = pd.Series(df2.index, index=df2['title']).drop_duplicates()

all_titles = [df2['title'][i] for i in range(len(df2['title']))]

def get_recommendations(title):
    global sim_scores
    idx = indices[title]
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:11]
    print("\n movieId      score")
    for i in sim_scores:
        print(i)

    movie_indices = [i[0] for i in sim_scores]

    return_df = pd.DataFrame(columns=['Title','Homepage'])
    return_df['Title'] = df2['title'].iloc[movie_indices]
    return_df['Homepage'] = df2['homepage'].iloc[movie_indices]
    return_df['ReleaseDate'] = df2['release_date'].iloc[movie_indices]
    return return_df

@app.route('/', methods=['GET', 'POST'])

def main():
    if flask.request.method == 'GET':
        return(flask.render_template('index.html'))
            
    if flask.request.method == 'POST':
        m_name = " ".join(flask.request.form['movie_name'].split())
        if m_name not in all_titles:
            return(flask.render_template('notFound.html',name=m_name))
        else:
            result_final = get_recommendations(m_name)
            names = []
            homepage = []
            releaseDate = []
            for i in range(len(result_final)):
                names.append(result_final.iloc[i][0])
                releaseDate.append(result_final.iloc[i][2])
                if(len(str(result_final.iloc[i][1]))>3):
                    homepage.append(result_final.iloc[i][1])
                else:
                    homepage.append("#")
                

            return flask.render_template('found.html',movie_names=names,movie_homepage=homepage,search_name=m_name, movie_releaseDate=releaseDate, movie_simScore=sim_scores)
        
    
def get_genre(name):
    movies = df2[df2['genres'].str.contains(name)]
    movies_data = movies.sample(10)
    return movies_data


@app.route('/genre/<genre_name>')
def fetch_genre(genre_name):
    movies_homepage = []
    movie_names = []
    release_date = []
    movies_data = get_genre(genre_name)
    for i in range(len(movies_data)):
        movie_names.append(movies_data.iloc[i][8])
        release_date.append(movies_data.iloc[i][13])
        url = movies_data.iloc[i][4]
        if len(str(url)) > 3:
            movies_homepage.append(str(url))
        else:
            movies_homepage.append('')
    return flask.render_template('genres.html', genre_name = genre_name, movie_homepage = movies_homepage, movie_releaseDate = release_date, movie_names = movie_names)

if __name__ == '__main__':
    app.run(host="127.0.0.1", port=8080, debug=True)