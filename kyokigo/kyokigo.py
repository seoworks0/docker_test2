import urllib.request, urllib.error
from urllib.request import Request, urlopen
from urllib.error import URLError
import sys
import MeCab
from .normalize import normalize
from .serps import g_serps
from .stopwords1 import stopwords
import codecs as cd
import gensim
from janome.tokenizer import Tokenizer
from gensim import corpora, models, similarities
from bs4 import BeautifulSoup
import pandas
from retry import retry
import re

def Morphological(text,phrase):
    output_words = []
    output_phrase = []
    output_verbs = []
    #MECABで名詞を取り出す
    m = MeCab.Tagger ()
    soup = m.parse (text)
    phrase1 = m.parse (phrase)
    for row in soup.split("\n"):
        word =row.split("\t")[0]
        if word == "EOS":
            break
        else:
            pos = row.split("\t")[1]
            slice = pos[0:2]
            if slice == "名詞":
                word = normalize(word)
                output_words.append(word)
            if slice == "動詞":
                verb = normalize(word)
                if len(verb)!= 1:
                    output_verbs.append(verb)

    for row in phrase1.split("\n"):
        word =row.split("\t")[0]
        if word == "EOS":
            break
        else:
            pos = row.split("\t")[1]
            slice = pos[0:2]
            if slice == "名詞":
                output_phrase.append(word)
    #単語の正規化
    list4 = []
    for item in list(output_phrase):
        a = normalize(item)
        if a != "0":
            list4.append(a)
    list4.append("0")
    list1 = list(set(output_words) - set(list4))

    #STOPWORDSの除去
    list5 =stopwords(output_verbs)
    list1 =stopwords(list1)
    return list1,list5

def url2text(urls,phrase):
    text2 = []
    list_noun = []
    list_verb = []
    j = 0
    for url in urls:
        print(url+"の内容を取得しています。")
        html = url_req(url)
        text1 = soup(html)
        list1 = [url,text1]
        text2 +=[list1]
        list2,list3=Morphological(text1,phrase)
        list_noun.append(list2)
        list_verb.append(list3)
    return list_noun,list_verb,text2

@retry()
def url_req(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    html = urllib.request.urlopen(req)
    return html

def soup(html):
    soup = BeautifulSoup(html, "html.parser")
    soup_title = soup.find_all("title")
    soup_h1 = soup.find_all("h1")
    soup_h2 = soup.find_all("h2")
    soup_h3 = soup.find_all("h3")
    soup_h4 = soup.find_all("h4")
    soup_h5 = soup.find_all("h5")
    soup_h6 = soup.find_all("h6")
    soup_a = soup.find_all("a")
    soup_p = soup.find_all("p")
    soup_li = soup.find_all("li")
    soup_dd = soup.find_all("dd")
    soup_dt = soup.find_all("dt")
    soup_table = soup.find_all("table")


    soup=soup_title+soup_h1+soup_h2+soup_h3+soup_h4+soup_h5+soup_h6+soup_a+soup_p+soup_li+soup_dd+soup_dt+soup_table

    maped_list = map(str, soup)
    soup1 = ', '.join(maped_list)
    soup2 = BeautifulSoup(soup1, "html.parser")
    text = soup2.get_text()
    return text

def make_dictionary(list3):
    idnvolume = {}
    wordnid = {}
    wordnvolume = {}
    print("辞書の作成を開始します。")
    dictionary = corpora.Dictionary(list3)
    #dictionary.filter_extremes(no_below=1, no_above=1)
    idnvolume = dictionary.dfs
    wordnid = dictionary.token2id
    wordnid = dict([(v,k) for k,v in wordnid.items()])
    idnvolume = sorted(idnvolume.items(), key=lambda x: -x[1])
    idnvolume = dict(idnvolume)
    for id_idnvolume,vol_idnvolume in idnvolume.items():
        key = wordnid[id_idnvolume]
        if vol_idnvolume != 1:
            wordnvolume.update({key:vol_idnvolume})
    print(wordnvolume)
    print("-----------------------------------------------")
    return wordnvolume

def make_corpus(dictionary,list3,text):
    print("コーパスの作成を開始します。")
    corpus = [dictionary.doc2bow(text) for text in list3]
    corpora.MmCorpus.serialize('cop.mm', corpus)
    corpus = gensim.corpora.TextCorpus('cop.mm')
    return corpus

def kyokilist(dic,text):
    kyoki_list = []
    for word in dic.keys():
        for text1 in text:
            try:
                doc = re.findall('...................................' + word + "......", text1[1])
                kyoki_list.append( doc[0] + text1[0])
                break
            except:
                pass
    return kyoki_list


def kyoki():
    phrase = ("結婚式 招待状")
    maxrank = 1
    #urls = g_serps(phrase,maxrank)
    urls = ['https://hagelabo.jp/articles/3041', 'https://customlife-media.jp/hairgrowth-marketsales']
    list3,list6,text = url2text(urls,phrase)
    dictionary_noun = make_dictionary(list3)
    dictionary_verb = make_dictionary(list6)
    nounlist = kyokilist(dictionary_noun,text)
    verblist = kyokilist(dictionary_verb,text)

    #print(nounlist,verblist)

    return nounlist,verblist

main()
