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

radicals = [ 
  "", "一", "丨", "丶", "丿", "乙", "亅", "二", "亠", "人", "儿", "入", "八", 
  "冂", "冖", "冫", "几", "凵", "刀", "力", "勹", "匕", "匚", "匸", "十", "卜", 
  "卩", "厂", "厶", "又", "口", "囗", "土", "士", "夂", "夊", "夕", "大", "女", 
  "子", "宀", "寸", "小", "尢", "尸", "屮", "山", "巛", "工", "己", "巾", "干", 
  "幺", "广", "廴", "廾", "弋", "弓", "彑", "彡", "彳", "心", "戈", "戶", "手", 
  "支", "攴", "文", "斗", "斤", "方", "无", "日", "曰", "月", "木", "欠", "止", 
  "歹", "殳", "毋", "比", "毛", "氏", "气", "水", "火", "爪", "父", "爻", "爿", 
  "片", "牙", "牛", "犬", "玄", "玉", "瓜", "瓦", "甘", "生", "用", "田", "疋", 
  "疒", "癶", "白", "皮", "皿", "目", "矛", "矢", "石", "示", "禸", "禾", "穴", 
  "立", "竹", "米", "糸", "缶", "网", "羊", "羽", "老", "而", "耒", "耳", "聿", 
  "肉", "臣", "自", "至", "臼", "舌", "舛", "舟", "艮", "色", "艸", "虍", "虫", 
  "血", "行", "衣", "襾", "見", "角", "言", "谷", "豆", "豕", "豸", "貝", "赤", 
  "走", "足", "身", "車", "辛", "辰", "辵", "吧", "酉", "釆", "里", "金", "長", 
  "門", "阜", "隶", "隹", "雨", "青", "非", "面", "革", "韋", "韭", "音", "頁", 
  "風", "飛", "食", "首", "香", "馬", "骨", "高", "髟", "鬥", "鬯", "鬲", "鬼", 
  "魚", "鳥", "鹵", "鹿", "麥", "麻", "黃", "黍", "黑", "黹", "黽", "鼎", "鼓", 
  "鼠", "鼻", "齊", "齒", "龍", "龜", "龠"
]

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

def parseSource(elem):
  text = ''
  for e in elem.descendants:
    if isinstance(e, str):
      text += e.strip()
    elif e.name == 'br' or e.name == 'p':
      text += "\n"
  return text


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
    sources = parseSource(row.find_all('td')[2])
    explanation = row.find_all('td')[-1]
    for a in explanation.select('a'):
      a.extract()
    explanation = row.find_all('td')[-1].get_text()
    phonetics[1].append([phonetic, explanation])
  
  combinations = [elem.get_text() for elem in soup.find('form').find_all(recursive=False) if elem.name == 'a']
  mandarin = list(filter(None, soup.find_all('table')[3].find_all('tr')[0].find_all('td')[3].get_text().split(' ')))
  englist = soup.find_all('table')[3].find_all('tr')[1].find_all('td')[3].get_text()
  
  return [
    radicals[int(rad)],
    stroke,
    phoneticClass,
    cangjie,
    rank, 
    freq,
    phonetics,
    sources,
    combinations,
    mandarin,
    englist
  ]

if __name__ == '__main__':
  getAllCharaters()
  crawlCharacter()
  dict = {}
  with open('dist/all.txt') as f:
    for line in f.readlines():
      [code, char] = line.replace('search.php?q=', '').replace("\n", '').split(' ')
      print (char)
      if not path.exists("dist/dict/"+char+".json"):
        with open("dist/dict/"+char+".json", 'w') as o:
          o.write(json.dumps(crawlCharacter(char=char, code=code), ensure_ascii=False))
      with open("dist/dict/"+char+".json") as o:
        dict[char] = json.load(o)
  
  with open('dist/dict.json', 'w') as f:
    f.write(json.dumps(dict, ensure_ascii=False))