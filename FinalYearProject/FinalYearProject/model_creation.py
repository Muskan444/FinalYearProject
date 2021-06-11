import pandas as pd
from Foodie.models import Blogs
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import sqlalchemy

def create():
	blogs = Blogs.objects.all()
	foodlist = []

	for blog in blogs:
		foodlist.append(blog.ingredients)

	ingredients = pd.Series(foodlist)

	vectorizer = TfidfVectorizer()
	tfidf_matrix = vectorizer.fit_transform(ingredients)
	cosine_sim = cosine_similarity(tfidf_matrix)
	cosine_pd = pd.DataFrame(cosine_sim)

	with open("train.pickle","wb") as f:
		pickle.dump(cosine_sim,f)



