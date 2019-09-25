
# BELEDİYE İLETİŞİM EVRAKLARININ SINIFLANDIRILMASI
##### Güler Atçı, Ebru Topçu, Sümeyye Turan,Shahed ALALI ALGHRSI
##### Mentörler:   Duygu Can, Dicle Öztürk
##### Yapay Zeka Yaz Atölyesi
##### 18 - 31 Ağustos 2019, Kadıköy IDEA


Bu çalışmada Kadıköy Belediyesi'ne gönderilen metinlerin şikayet, talep, vs. gibi sınıflandırılması yapılacaktır. *Kapsam* ve *Döküman Metin* kolonları arasındaki ilişki incelenecektir. 
 Gelen veri Ocak 2019 - Temmuz 2019 tarihleri arasındaki web formları ve telefonla alınan isteklerden oluşuyordu. Yaklaşık 16.000 metinden anlamlı olan 13.000 metin çekilip üzerinde çalışıldı.Veri daha anlamlı hale dönüştürüldükten sonra işimize yarayacağını düşündüğümüz öznitelikler çıkardık. Özniteliklerin amacı verinin daha basit hale indirgenmesidir.Doğru yapılmış bir özellik çıkarımı ve bu özelliklere uygun bir sistem tasarımı sonucun başarılı olması ve performansını etkileyen unsurlardır.
 4 farklı makina öğrenmesi algoritması kullanıp bazı metrikler kıyaslandı ve en yüksek doğruluğu veren algoritma bulunmaya çalışıldı. Sonuçlar 7 aylık bir veri ile çalışılmasına rağmen %79 doğrulukla metinleri sınıflandırdı. Daha fazla veri ve daha iyi parametre optimizasyonu ve hatta derin öğrenme algoritmalarının denenmesi ile çok daha iyi sonuçlar alınabilir.
"""

# Run this cell to mount your Google Drive.
from google.colab import drive
drive.mount('/content/drive')

"""Veriyi okuma"""

import pandas as pd
df = pd.read_excel("/content/drive/My Drive/YapayzekaAtolyesi/EEVR_D-Evrak_iletisim_detay.xlsx")
df.tail(5)

"""Veri tabanımızda 16155 örnek, 23 kolon var."""

df.shape

"""Veri tiplerini görüntülüyelim"""

df.dtypes

"""Kategorik kolonların özgün değerlerine bakalım (Bazıları nümerik olmalıydı)."""

for col in df.columns:
  if df[col].dtype.name == "object":
    print(col, ":", df[col].unique())

"""## Veri Tekilleştirme"""

df = df.drop_duplicates()
df.shape

"""## Kayıp Veri Temizleme

*Döküman Metin* kolonunun ~%12'i boş, bunlar temizlenmeli.
"""

sum(df["Doküman Metin"].isna())/len(df)*100

import numpy as np
#df2 = df.copy()
df = df.dropna(subset=['Doküman Metin'])
#df = df[df['Doküman Metin'] != np.nan]
df.shape

sum(df["Doküman Metin"].isnull())/len(df)*100

"""Varsa *Kapsam* kolonundaki kayıp verileri de temizledik."""

sum(df["Kapsam"].isna())/len(df)*100

df = df.dropna(subset=['Kapsam'])
df.shape

"""## Ön-işleme
 ### Büyük/Küçük Harf
 
 *Döküman Metin* kolonunundaki girdilerin hepsini küçük harf yapalım çünkü *nltk* kütüphanesindeki dolgu sözcükleri küçük harfle yazılmış.
"""

df['Doküman Metin'] = df['Doküman Metin'].str.lower()
df['Doküman Metin'].head()

"""### Son Sözler...

Metin içeriğinin son kelimeleri incelendiğinde dilekçelerin "bilginize", "bilgilerinize" bittiği gözlemlendi. Dolgu sözcüğü olarak ele alınabilirler. Bazen bu kelimeler basit bir yazım hatası yüzünden önceki kelimeye bitişik yazılmıştır. "." karakterleri " " (boşluk) ile değiştirilerek, bu kelimeler dolgu kelimesi listesine eklenebilir.
"""

df['Doküman Metin'].str.rsplit(' ',1).str[1].head(10)

df['Doküman Metin'].str.rsplit(' ',1).str[1].str.rsplit('.').str[1].head(100)

"""## Öznitelik Çıkarımı ve Görselleştirme

### Kelime Bulutu Oluşturma
"""

import matplotlib.pyplot as plt
from matplotlib import pyplot
from wordcloud import WordCloud
text = []
for i in df["Doküman Metin"]:
   text.append(i)#here we are adding word to text array but it's looking like this ['Larency','Homicide','Robbery']
text = ' '.join(map(str, text)) #Now we make all of them like this [LarencyHomicideRobbery]
wordcloud = WordCloud(width=1600, height=800, max_font_size=300,background_color='black').generate(text)
plt.figure(figsize=(20,15))
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis("off")
plt.show()

"""### Kelime Sayısı"""

df['kelime_sayisi'] = df['Doküman Metin'].apply(lambda x: len(str(x).split(" ")))
df[['Doküman Metin','kelime_sayisi']].head()

print("Kapsam:\n",df["Kapsam"].describe())

fig, ax = plt.subplots(1, 1,figsize=(10, 8))
df[ df.Kapsam == "Talep"]["kelime_sayisi"].hist(bins=50, color="blue", alpha=0.5, ax=ax)
df[df.Kapsam=="Şikayet"]["kelime_sayisi"].hist(bins=50, color="red", alpha=0.5, ax=ax)
df[df.Kapsam=="İhbar"]["kelime_sayisi"].hist(bins=50, color="green", alpha=0.5, ax=ax)
df[df.Kapsam=="Öneri"]["kelime_sayisi"].hist(bins=50, color="yellow", alpha=0.5, ax=ax)
df[df.Kapsam=="Teşekkür"]["kelime_sayisi"].hist(bins=50, color="brown", alpha=0.7, ax=ax)
plt.title('Kapsama Göre Gruplanan Kelime Sayısı Histogramı')
plt.ylabel('Kapsam')
plt.xlabel('Kelime Sayısı')

"""### Karakter Sayısı

Metin uzunluklarından karakter sayısı çıkarılmıştır. Boşluk karakterleri de sayılmıştır.
"""

df['karakter_sayisi'] = df['Doküman Metin'].str.len() ## this also includes spaces
df[['Doküman Metin','karakter_sayisi']].head()

fg, ax = plt.subplots(1, 1,figsize=(10, 8))
df[df.Kapsam=="Talep"]["karakter_sayisi"].hist(bins=50, color="black",alpha=0.5,ax=ax)
df[df.Kapsam=="Şikayet"]["karakter_sayisi"].hist(bins=50, color="blue",alpha=0.5,ax=ax)
df[df.Kapsam=="Öneri"]["karakter_sayisi"].hist(bins=50, color="red",alpha=0.5,ax=ax)
df[df.Kapsam=="Teşekkür"]["karakter_sayisi"].hist(bins=50, color="green",alpha=0.5,ax=ax)
plt.title('Kapsama Göre Gruplanan Karakter Sayısı Histogramı')
plt.ylabel('Kapsam')
plt.xlabel('Karakter Sayısı')

"""### Ortalama Kelime Uzunluğu

Kullanılan kelimelerinin uzunluklarının kapsama göre farklılık gösterebileceği düşünülerek her metnin ortalam kelime uzunluğu bulunmuştur.
"""

def avg_word(sentence):
  words = sentence.split()
  return (sum(len(word) for word in words)/len(words))

df['ort_kelime'] = df['Doküman Metin'].apply(lambda x: avg_word(x))
df[['Doküman Metin','ort_kelime']].head()

fg, ax = plt.subplots(1, 1,figsize=(10, 8))
df[df.Kapsam=="Talep"]['ort_kelime'].hist(bins=50, color="blue",alpha=0.5,ax=ax)
df[df.Kapsam=="Şikayet"]['ort_kelime'].hist(bins=50, color="red",alpha=0.5,ax=ax)
df[df.Kapsam=="Öneri"]['ort_kelime'].hist(bins=50, color="yellow",alpha=0.5,ax=ax)
df[df.Kapsam=="Teşekkür"]['ort_kelime'].hist(bins=50, color="brown",alpha=0.5,ax=ax)
plt.title('Kapsama Göre Gruplanan Ortalama Kelime Sayısı Histogramı')
plt.ylabel('Kapsam')
plt.xlabel('Ortalama Kelime Sayısı')

"""### Dolgu Sözcüğü Sayısı

Dil işleme problemini çalışmaya başlamadan önce şikayet/talep metnindeki dolgu sözcüklerini atacağız. Bu kelimeler genelde içerik hakkında bilgilendirici olmayan bağlaçlar, hitaplar, vs.'dir. Yine de bilgi kaybetmemek için dolgu sözcükleri sayısını ayrı bir kolonda tutmayı uygun gördük. Önce *nltk* kütüphanesinin dolgu sözcüklerini indirelim:
"""

import nltk
nltk.download('stopwords')

from nltk.corpus import stopwords
stop = []
stop = stopwords.words('turkish')
stop.extend(["bilginize", "bilgilerinize", ".bilginize", 
             ".bilgilerinize", "bilginize.", "bilgilerinize.", 
             ".bilginize.", ".bilgilerinize.", "saygılarımla", "saygılarımla."
             ".saygılarımla", ".saygılarımla."])

df['dolgu_sayisi'] = df['Doküman Metin'].apply(lambda x:len([x for x in x.split()if x in stop]))
df[['Doküman Metin','dolgu_sayisi']].head()

fg, ax = plt.subplots(1, 1,figsize=(10, 8))
df[df.Kapsam=="Talep"]['dolgu_sayisi'].hist(bins=50, color="blue",alpha=0.5,ax=ax)
df[df.Kapsam=="Şikayet"]['dolgu_sayisi'].hist(bins=50, color="red",alpha=0.5,ax=ax)
df[df.Kapsam=="Öneri"]['dolgu_sayisi'].hist(bins=50, color="yellow",alpha=0.5,ax=ax)
df[df.Kapsam=="Teşekkür"]['dolgu_sayisi'].hist(bins=50, color="brown",alpha=0.5,ax=ax)
plt.title('Kapsama Göre Gruplanan Dolgu Kelime Sayısı Histogramı')
plt.ylabel('Kapsam')
plt.xlabel('Dolgu Kelime  Sayısı')

print(stop)
df.dolgu_sayisi.describe()

"""### Rakam Sayısı

Metinlerde geçen rakam sayısı da bir kolonda tutulmuştur.
"""

df['rakam_sayisi'] = df['Doküman Metin'].apply(lambda x: len([x for x in x.split() if x.isdigit()]))
df[['Doküman Metin', 'rakam_sayisi']].head()
df["rakam_sayisi"].unique()

fg, ax = plt.subplots(1, 1,figsize=(10, 8))
df[df.Kapsam=="Talep"]['rakam_sayisi'].hist(bins=100, color="blue",alpha=0.5,ax=ax)
df[df.Kapsam=="Şikayet"]['rakam_sayisi'].hist(bins=100, color="red",alpha=0.5,ax=ax)
df[df.Kapsam=="Öneri"]['rakam_sayisi'].hist(bins=100, color="yellow",alpha=0.5,ax=ax)
df[df.Kapsam=="Teşekkür"]['rakam_sayisi'].hist(bins=100, color="brown",alpha=0.5,ax=ax)
plt.title('Kapsama Göre Gruplanan Rakam İçeren Kelime Sayısı Dağılımı')
plt.ylabel('Kapsam')
plt.xlabel('Rakam İçeren Kelime Sayısı')

"""## Ön-işleme'ye Devam

### Noktalama İşaretlerini Kaldırma

Noktalama işaretleri içerik açısından bilgilendirici  değildir. Önce kaldırılmaları düşünülmüştür ama bazı yazım hatalarından dolayı kelimelerin birbirlerine ulanmalarına neden olduklarından, " " (boşluk) karakteri ile değiştirilip sonradan düşürülmüşlerdir.
"""

df['Doküman Metin'] = df['Doküman Metin'].str.replace('.',' ')

df['Doküman Metin'] = df['Doküman Metin'].str.replace(',',' ')

df['Doküman Metin'] = df['Doküman Metin'].str.replace('[^\w\s]','')
df['Doküman Metin'].head()

"""### Rakamları Silme

Adres bilgileri ile gelen sayıların içerik hakkında bilgilendirici olmadığını düşündüğümüz için kaldırıyoruz.
"""

#df = df.copy()
df['Doküman Metin'] = df['Doküman Metin'].str.replace('\d+', '')
df['Doküman Metin'].head()

"""### Dolgu Sözcüklerinden Kurtulma"""

df['Doküman Metin'] = df['Doküman Metin'].apply(lambda x: " ".join(x for x in x.split() if x not in stop))
df['Doküman Metin'].head()

"""### Sık Tekrarlar

Sık tekrar eden kelimeler bilgilendirici olmayacaktır. Tüm girdilerde, en sık tekrar eden 15 kelimeyi listeleyelim. "talep" dışındaki kelimeler, içeriğin kapsamı hakkında bilgilendirici değildir.
"""

freq = pd.Series(' '.join(df['Doküman Metin']).split()).value_counts()[:30]
freq = freq[freq>1000]
print(freq)

freq.pop("talep")
freq

freq = list(freq.index)
df['Doküman Metin'] = df['Doküman Metin'].apply(lambda x: " ".join(x for x in x.split() if x not in freq))
df['Doküman Metin'].head()

"""### Nadir Kelimeler

Nadir görülen kelimelerin diğerleri ile olan ilişkisi zaten verideki gürültü tarafından baskılanacağı için az tekrarlanan kelimeler de bizim için bilgilendirici olmayacaktır, onları da atalım. Eşik değer olarak frekansı 5 seçtik. 5'ten az görünen kelimeleri listelediğimizde yanlış yazılan kelimelerin, birbirine ulanan kelimeler olduğunu gördük.
"""

freq2 = pd.Series(' '.join(df['Doküman Metin']).split()).value_counts()#[-100:]
freq2 = freq2[freq2<5.1]

freq2

freq2 = list(freq2.index)
#df2 = df.copy()
df['Doküman Metin'] = df['Doküman Metin'].apply(lambda x: " ".join(x for x in x.split() if x not in freq2))
df['Doküman Metin'].head()

df['Doküman Metin'].describe()

"""## Kelime Köklerini Bulma

NLTK kütüphanesinin Snowball stemmer modülü Türkçe dilini desteklememektedir. Ancak ayrı olarak indirilebilir (Aşağıdaki hücrenin başındaki # işareri kaldırılarak çalıştırılmalı).
"""

!pip install snowballstemmer

from snowballstemmer import TurkishStemmer
turkStem=TurkishStemmer()
#turkStem.stemWord(df["Doküman Metin"])

df['Doküman Metin'].apply(lambda x: " ".join(turkStem.stemWord(x) for x in x.split()))

"""## TF-IDF Ağırlıklı Vektörize Etme Ve Modelleri Deneme

5-fold cv. En iyi performans skorları RF ile elde edildi.
"""

from sklearn.feature_extraction.text import TfidfVectorizer
vectorizer = TfidfVectorizer(ngram_range=(1,1))
vectorizer.fit(df['Doküman Metin'])

y = df['Kapsam']
X = vectorizer.transform(df['Doküman Metin'])

"""### Lojistik Regresyon

5-fold acc  . [0.75437318 0.70663265 0.70897155 0.79058738 0.75264502]
Accuracy: 0.74 (+/- 0.06)
f1 Score: 0.24 (+/- 0.05)
"""

from sklearn.model_selection import cross_validate
from sklearn.metrics import f1_score
from sklearn.metrics import accuracy_score
from sklearn.linear_model import LogisticRegression


scoring = ['f1_macro', 'accuracy']
classifier = LogisticRegression(random_state=42)

scores = cross_validate(classifier, X, y, scoring=scoring, cv=5)
                        
print(sorted(scores.keys()))

print("5-fold acc  .", scores['test_accuracy'])

print("Accuracy: %0.2f (+/- %0.2f)" % (scores['test_accuracy'].mean(), scores['test_accuracy'].std() * 2))
print("f1 Score: %0.2f (+/- %0.2f)" % (scores['test_f1_macro'].mean(), scores['test_f1_macro'].std() * 2))

"""### SVM (linear kernel)
5-fold acc  . [0.75182216 0.64723032 0.71480671 0.78803356 0.76541408]
Accuracy: 0.73 (+/- 0.10)
f1 Score: 0.33 (+/- 0.06)
"""

from sklearn.model_selection import cross_validate
from sklearn.metrics import f1_score
from sklearn.metrics import accuracy_score
from sklearn import svm


scoring = ['f1_macro', 'accuracy']
classifier = svm.SVC(kernel = 'linear',random_state=42)


scores = cross_validate(classifier, X, y, scoring=scoring, cv=5)
                        
print(sorted(scores.keys()))

print("5-fold acc  .", scores['test_accuracy'])

print("Accuracy: %0.2f (+/- %0.2f)" % (scores['test_accuracy'].mean(), scores['test_accuracy'].std() * 2))
print("f1 Score: %0.2f (+/- %0.2f)" % (scores['test_f1_macro'].mean(), scores['test_f1_macro'].std() * 2))

"""### Random Forest 

5-fold acc  . [0.77040816 0.70262391 0.71735959 0.80809923 0.78657424]
Accuracy: 0.76 (+/- 0.08)
f1 Score: 0.48 (+/- 0.10)
"""

from sklearn.model_selection import cross_validate
from sklearn.metrics import f1_score
from sklearn.metrics import accuracy_score
from sklearn.ensemble import RandomForestClassifier


classifier = RandomForestClassifier(n_estimators=100,random_state=42)

scoring = ['f1_macro', 'accuracy']


scores = cross_validate(classifier, X, y, scoring=scoring, cv=5)
                        
print(sorted(scores.keys()))

print("5-fold acc  .", scores['test_accuracy'])

print("Accuracy: %0.2f (+/- %0.2f)" % (scores['test_accuracy'].mean(), scores['test_accuracy'].std() * 2))
print("f1 Score: %0.2f (+/- %0.2f)" % (scores['test_f1_macro'].mean(), scores['test_f1_macro'].std() * 2))

"""## N-gram Seçimi

### Bi-gram

Unigramlar yerine bigrama göre vektörize edildiğinde, vektör uzunluğu arttığından modele sokulan öznitelik sayısı artmıştır. Bu da modelin eğitim süresinin çok uzamasına neden olmuştur. Ayrıca model daha düşük performans gösterdiği için unigram modeli ile devam etmeye karar verdik.

5-fold acc  . [0.68440233 0.70918367 0.66119621 0.73549799 0.7019336 ]
Accuracy: 0.70 (+/- 0.05)
f1 Score: 0.40 (+/- 0.07)
"""

from sklearn.feature_extraction.text import TfidfVectorizer
vectorizer = TfidfVectorizer(ngram_range=(2,2))
vectorizer.fit(df['Doküman Metin'])

y = df['Kapsam']
X = vectorizer.transform(df['Doküman Metin'])

classifier = RandomForestClassifier(n_estimators=100,random_state=42)

scoring = ['f1_macro', 'accuracy']


scores = cross_validate(classifier, X, y, scoring=scoring, cv=5)
                        
print(sorted(scores.keys()))

print("5-fold acc  .", scores['test_accuracy'])

print("Accuracy: %0.2f (+/- %0.2f)" % (scores['test_accuracy'].mean(), scores['test_accuracy'].std() * 2))
print("f1 Score: %0.2f (+/- %0.2f)" % (scores['test_f1_macro'].mean(), scores['test_f1_macro'].std() * 2))

"""## Eğitim - Test Kumesi Ayrımı

kapsamdaki sınıflara gore katmanlı 80/20 oraNINda ayrım yapıldı
"""

from sklearn.model_selection import train_test_split
y = df["Kapsam"]
sentences = df["Doküman Metin"]
sentences_train, sentences_test, y_train, y_test = train_test_split(sentences, y, test_size=0.20, stratify = y, random_state=42)
print(sentences_train.shape)
print(sentences_test.shape)

from sklearn.feature_extraction.text import TfidfVectorizer

vectorizer = TfidfVectorizer(ngram_range=(1,1))
vectorizer.fit(sentences_train)


X_train = vectorizer.transform(sentences_train)
X_test = vectorizer.transform(sentences_test)

X_train.shape

"""## Hiper-parametre Kestirimi

1. Best parameters {'bootstrap': True, 'max_depth': 50, 'max_features': 'sqrt', 'min_samples_leaf': 3, 'min_samples_split': 8, 'n_estimators': 100, 'n_jobs': -1, 'random_state': 42, 'verbose': 2}
 

---

F1 Score:  0.2544484246352658
Test Accuracy: 0.7743346700692673
************************

## **Hiper-parametre optimal**
2. Best parameters {'bootstrap': False, 'max_depth': [20, 30, 40, 50],
   'max_features': ['auto' ],
   'min_samples_leaf': [ 4, 6, 8],
   'min_samples_split': [10, 16, 24],
   'n_estimators': [100],
   'random_state': [50],
   'verbose': [2],
   'n_jobs': [-1]


---

F1 Score:  0.2692892811136687 Test Accuracy: 0.7830842143638352
"""

from sklearn.model_selection import GridSearchCV
# Create the parameter grid based on the results of random search
param_grid = {
   'bootstrap': [False],
   'max_depth': [20, 30, 40, 50],
   'max_features': ['auto' ],
   'min_samples_leaf': [ 4, 6, 8],
   'min_samples_split': [10, 16, 24],
   'n_estimators': [100],
   'random_state': [50],
   'verbose': [2],
   'n_jobs': [-1]
}
# Create a based model
rf = RandomForestClassifier()
# Instantiate the grid search model
grid_search = GridSearchCV(estimator = rf, param_grid = param_grid,
                         cv = 3, n_jobs = -1, verbose = 2)

grid_search.fit(X_train, y_train)
print("Best parameters", grid_search.best_params_)
best_model = grid_search.best_estimator_
print(best_model)

from sklearn import metrics

y_pred = best_model.predict(X_test)

  
  
print("************************")
print("F1 Score: ",f1_score(y_test,y_pred, average='macro' ))
print("Test Accuracy:",metrics.accuracy_score(y_test, y_pred))

print("************************")

from sklearn import metrics

y_pred = best_model.predict(X_train)

  
  
print("************************")
print("F1 Score: ",f1_score(y_train,y_pred, average='macro' ))
print("Train Accuracy:",metrics.accuracy_score(y_train, y_pred))

print("************************")

"""## **Hiper-parametre optimal training set üzerinde**
2. Best parameters {'bootstrap': False, 'max_depth': [20, 30, 40, 50],
   'max_features': ['auto' ],
   'min_samples_leaf': [ 4, 6, 8],
   'min_samples_split': [10, 16, 24],
   'n_estimators': [100],
   'random_state': [50],
   'verbose': [2],
   'n_jobs': [-1]


---

F1 Score:  0.2815500959472641
Test Accuracy: 0.7935089798523111


Y-train ile Y-test arasındaki accuracy farkı 0.01042476548
Y-train ile Y-test arasındaki F1 Score farkı 0.01226081483

## Kaynaklar

1.   [Ultimate guide to deal with Text Data (using Python) – for Data Scientists and Engineers](https://www.analyticsvidhya.com/blog/2018/02/the-different-methods-deal-text-data-predictive-python/)
2.   [Python’da SnowBall Stemmer Kullanılması](https://medium.com/@aanilkayy/pythonda-snowball-stemmer-kullanılması-e91ed9be8e9e)
3.[Document Classification Part 2: Text Processing (N-Gram Model & TF-IDF Model)](https://medium.com/machine-learning-intuition/document-classification-part-2-text-processing-eaa26d16c719)
4. [Document Classification Part 3: Detection Algorithm (Support Vector Machines & Gradient Descent)](https://medium.com/machine-learning-intuition/document-classification-part-3-detection-algorithm-support-vector-machines-gradient-descent-282316b0838e)
5.[Practical Text Classification With Python and Keras](https://realpython.com/python-keras-text-classification/)
6. [Natural Language Processing: Text Data Vectorization](https://medium.com/@paritosh_30025/natural-language-processing-text-data-vectorization-af2520529cf7)
7. [TÜRKÇE METİN İŞLEMEDE İLK ADIMLAR](http://www.veridefteri.com/2017/11/20/turkce-metin-islemede-ilk-adimlar/)
"""
