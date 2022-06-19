import requests
import json
from bs4 import BeautifulSoup
from os import path

specialChars = {
  "%F9%D9": "墻",
  "%F9%DC": "嫺",
  "%F9%DA": "恒",
  "%F9%D6": "碁",
  "%F9%DB": "粧",
  "%F9%D8": "裏",
  "%F9%D7": "銹"
}

def getAllCharaters():
  if path.exists('dist/all.txt'):
    return
  page = requests.get('https://humanum.arts.cuhk.edu.hk/Lexis/lexi-can/rad.php')
  soup = BeautifulSoup(page.content.decode('big5', 'ignore'), "html.parser")

  with open('dist/all.txt', 'w') as f:
    rads = [a['href'] for a in soup.find_all('table')[1].find_all('a')]
    for rad in rads:
      page = requests.get('https://humanum.arts.cuhk.edu.hk/Lexis/lexi-can/'+rad)
      radSoup = BeautifulSoup(page.content.decode('big5', 'ignore'), "html.parser")
      for row in radSoup.find_all('table')[1].find_all('tr')[1:]:
        for character in row.find_all('td')[1].find_all('a'):
          if character['href'][-6:] in specialChars:
            f.write(character['href'] + " " + specialChars[character['href'][-6:]] + "\n")
          else:
            f.write(character['href'] + " " + character.decode_contents() + "\n")

def crawlCharacter(char = '愛', code="%B7R"):
  page = requests.get('https://humanum.arts.cuhk.edu.hk/Lexis/lexi-can/search.php?q='+code, cookies={"Canton": "1"})
  soup = BeautifulSoup(page.content.decode('big5', 'ignore'), "html.parser")
  cells = soup.find_all('table')[0].find_all('td')
  rad = cells[2].find_all('a')[0]['href'].replace('rad-str.php?rad=', '')
  stroke = cells[4].find_all('a')[0].decode_contents()
  phoneticClass = cells[6].find_all('a')[0].decode_contents()
  cangjie = cells[11].decode_contents()
  [rank, freq] = cells[13].decode_contents().split(' / ')

  phonetics = [[], []]
  rows = soup.find_all('table')[1].find_all('tr')[1:]
  for row in rows:
    phonetic = [font.get_text() for font in row.find_all('td')[0].find_all('font')]
    explanation = row.find_all('td')[-1]
    for a in explanation.select('a'):
      a.extract()
    explanation = row.find_all('td')[-1].get_text()
    phonetics[0].append([phonetic, explanation])

  page = requests.get('https://humanum.arts.cuhk.edu.hk/Lexis/lexi-can/search.php?q='+code, cookies={"Canton": "1"})
  soup = BeautifulSoup(page.content, "html.parser")
  rows = soup.find_all('table')[1].find_all('tr')[1:]
  for row in rows:
    phonetic = [font.get_text() for font in row.find_all('td')[0].find_all('font')]
    explanation = row.find_all('td')[-1]
    for a in explanation.select('a'):
      a.extract()
    explanation = row.find_all('td')[-1].get_text()
    phonetics[1].append([phonetic, explanation])
  
  return [
    rad,
    stroke,
    phoneticClass,
    cangjie,
    rank, 
    freq,
    phonetics
  ]

if __name__ == '__main__':
  getAllCharaters()
  dict = {}
  with open('dist/all.txt') as f:
    for line in f.readlines():
      [code, char] = line.replace('search.php?q=', '').replace("\n", '').split(' ')
      if not path.exists("dist/dict/"+char+".json"):
        with open("dist/dict/"+char+".json", 'w') as o:
          o.write(json.dumps(crawlCharacter(char=char, code=code), ensure_ascii=False))
      with open("dist/dict/"+char+".json") as o:
        dict[char] = json.load(o)
  
  with open('dist/dict.json', 'w') as f:
    f.write(json.dumps(dict, ensure_ascii=False))