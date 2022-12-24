from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

vectorize = TfidfVectorizer()

strings = ['University of Athens', 'university of columbia']

stringsVec = vectorize.fit_transform(strings)
similarity = cosine_similarity(stringsVec)

print(similarity)