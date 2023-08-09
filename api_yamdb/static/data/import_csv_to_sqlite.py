import pandas as pd
import sqlite3

con = sqlite3.connect('api_yamdb/db.sqlite3')
cur = con.cursor()

category = pd.read_csv('api_yamdb/static/data/category.csv',
                       header=0,
                       index_col=0,
                       names=("id", "name", "slug"))
category.to_sql('reviews_categories', con, if_exists='replace', index=False)

genre = pd.read_csv('api_yamdb/static/data/genre.csv',
                    header=0,
                    index_col=0,
                    names=("id", "name", "slug"))
genre.to_sql('reviews_genres', con, if_exists='replace', index=False)

title = pd.read_csv('api_yamdb/static/data/titles.csv',
                    header=0,
                    index_col=0,
                    names=("id", "name", "year", "category_id"))
title.to_sql('reviews_titles', con, if_exists='replace', index=False)

genre_title = pd.read_csv('api_yamdb/static/data/genre_title.csv',
                          header=0,
                          index_col=0,
                          names=("id", "titles_id", "genres_id"))
genre_title.to_sql('reviews_titles_genre',
                   con, if_exists='replace', index=False)


# для модели review
# review = pd.read_csv('api_yamdb/static/data/review.csv',
#                           header=0,
#                           index_col=0,
#                           names=("id", "titles_id", "text", "author", "score", "pub_date"))
# review.to_sql('reviews_review',
#                    con, if_exists='replace', index=False)

# для модели comments
# comments = pd.read_csv('api_yamdb/static/data/comments.csv',
#                           header=0,
#                           index_col=0,
#                           names=("id", "review_id", "text", "author", "pub_date"))
# comments.to_sql('reviews_comments',
#                    con, if_exists='replace', index=False)


# для модели users - определить название модели
# users = pd.read_csv('api_yamdb/static/data/users.csv',
#                           header=0,
#                           index_col=0,
#                           names=("id", "username", "email", "role", "bio", "first_name", "last_name"))
# users.to_sql('ХХХХ',
#                    con, if_exists='replace', index=False)

con.commit()

