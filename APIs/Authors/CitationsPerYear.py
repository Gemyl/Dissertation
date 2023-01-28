from bs4 import BeautifulSoup
from scholarly import scholarly
import urllib.request
import matplotlib.pyplot as plt

url = 'https://scholar.google.com/citations?user=otjuGKYAAAAJ'
page = urllib.request.urlopen(url)
s = BeautifulSoup(page, 'lxml')
years = list(
    map(int, [i.text for i in s.find_all('span', {'class': 'gsc_g_t'})]))
citation_number = list(
    map(int, [i.text for i in s.find_all('span', {'class': 'gsc_g_al'})]))
# final_chart_data = dict(zip(years, citation_number))

author_name = scholarly.search_author_id('otjuGKYAAAAJ')['name']

plt.bar(years, citation_number, color='green')
plt.xlabel('Years')
plt.ylabel('Citations')
plt.title(author_name + '\'s Citations Per Year')
plt.show()
