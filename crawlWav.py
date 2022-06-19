from urllib.request import urlopen
import requests
import json
import os
from io import BytesIO
from pydub import AudioSegment

waves = {}
with open('all.txt') as f:
  for line in f.readlines():
    [code, char] = line.replace('search.php?q=', '').replace("\n", '').split(' ')
    with open('dict/'+char+'.json') as o:
      for line in o.readlines():
        data = json.loads(line)
        for phonetics in data[6][0]:
          waves[''.join(phonetics[0])] = True

try:
  os.mkdir('wav')
except:
  pass

for wav in waves.keys():
  if not os.path.exists('wav/'+wav+'.mp3') and wav != '':
    try:
      audio = AudioSegment.from_file(BytesIO(urlopen('https://humanum.arts.cuhk.edu.hk/Lexis/lexi-can/sound/'+wav+'.wav').read()))
      audio.export('wav/'+wav+'.mp3', format="MP3")
    except:
      pass