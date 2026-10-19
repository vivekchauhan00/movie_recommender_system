import os
import pickle
import requests
import streamlit as st
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

TOKEN = os.getenv("TMDB_TOKEN")   

session = requests.Session()
retry = Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
session.mount("https://", HTTPAdapter(max_retries=retry))

HEADERS = {"Authorization": f"Bearer {TOKEN}", "accept": "application/json"}


@st.cache_data
def _get_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}"
    response = session.get(url, headers=HEADERS, timeout=10)
    response.raise_for_status()
    poster_path = response.json().get("poster_path")
    if not poster_path:
        return None
    return "https://image.tmdb.org/t/p/w500" + poster_path


def fetch_poster(movie_id):
    try:
        return _get_poster(movie_id)
    except requests.exceptions.RequestException:
        return None   # failed requests aren't cached, so it retries next click


def recommend(movie_name):
    movie_index = movies_list[movies_list['title'] == movie_name].index[0]
    distance = similarity[movie_index]
    mov_list = sorted(list(enumerate(distance)), reverse=True, key=lambda x: x[1])[1:6]

    names, posters = [], []
    for i in mov_list:
        row = movies_list.iloc[i[0]]
        names.append(row.title)
        posters.append(fetch_poster(row.movie_id))
    return names, posters


movies_list = pickle.load(open('movies.pkl', 'rb'))
similarity = pickle.load(open('similarity.pkl', 'rb'))

st.title("Movie Recommender System")
selected_option = st.selectbox('Select movie', movies_list['title'])

if st.button('Recommend'):
    names, posters = recommend(selected_option)

    for col, name, poster in zip(st.columns(5), names, posters):
        with col:
            st.text(name)
            if poster:
                st.image(poster)
            else:
                st.write("Poster unavailable")