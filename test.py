from bs4 import BeautifulSoup
from urllib.request import urlopen

url = "http://www.dynastyfftools.com/tools/players"

response = urlopen(url)
page_source = response.read()

# OPTIONAL: parse in python
soup = BeautifulSoup(page_source, 'html.parser')
# Print out whole page source
print(soup.prettify())
