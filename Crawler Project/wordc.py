import jieba
from wordcloud import WordCloud as wc
from matplotlib import pyplot as plt
import sqlite3 as sql


conn = sql.connect("movie.db")
cur = conn.cursor()
query = 'SELECT introduction FROM movie250'
data = cur.execute(query)
text = ""
for items in data:
    text = text + items[0]
cur.close()
conn.close()

# split words
cut = jieba.cut(text)
string = ' '.join(cut)
print(len(string))


# show wordcloud
w = wc(
    background_color='white',
    font_path="/System/Library/Fonts/Hiragino Sans GB.ttc",
    max_font_size=100,
    max_words=100,
    scale=2
)
w.generate(text=string)

fig = plt.figure(figsize=(20, 10))
plt.imshow(w)
plt.axis('off')
plt.show()
