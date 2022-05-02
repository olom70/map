from bs4 import BeautifulSoup


file = open('temp.htm
l', 'r')
soup = BeautifulSoup(file, 'html.parser')

#print(soup.prettify())
print(soup.find_all('td'))
file.close()