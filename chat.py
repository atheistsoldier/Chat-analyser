# -*- coding: utf-8 -*-



# Commented out IPython magic to ensure Python compatibility.
import re
import datetime
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud,STOPWORDS
import emoji
import itertools as it
from collections import Counter
from collections import OrderedDict 
import collections
from datetime import datetime



def rawToDf(file, key):
    '''Converts raw .txt file into a Data Frame'''
    
    split_formats = {
        '12hr' : '\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}\s[APap][mM]\s-\s',
        '24hr' : '\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}\s-\s',
        'custom' : ''
    }
    datetime_formats = {
        '12hr' : '%d/%m/%Y, %I:%M %p - ',
        '24hr' : '%m/%d/%y, %H:%M - ',
        'custom': ''
    }
    
    with open(file, 'r', encoding='utf-8') as raw_data:
        #print(raw_data.read())
        raw_string = ' '.join(raw_data.read().split('\n')) # converting the list split by newline char. as one whole string as there can be multi-line messages
        #print(raw_string)
        user_msg = re.split(split_formats[key], raw_string)[1:] # splits at all the date-time pattern, resulting in list of all the messages with user names
        
        date_time = re.findall(split_formats[key], raw_string) # finds all the date-time patterns
        
        df = pd.DataFrame({'date_time': date_time, 'user_msg': user_msg}) # exporting it to a df
        
    # converting date-time pattern which is of type String to type datetime,
    # format is to be specified for the whole string where the placeholders are extracted by the method 
    df['date_time'] = pd.to_datetime(df['date_time'], format=datetime_formats[key])
    
    # split user and msg 
    usernames = []
    msgs = []
    for i in df['user_msg']:
        a = re.split('([\w\W]+?):\s', i) # lazy pattern match to first {user_name}: pattern and spliting it aka each msg from a user
        if(a[1:]): # user typed messages
            usernames.append(a[1])
            msgs.append(a[2])
        else: # other notifications in the group(eg: someone was added, some left ...)
            usernames.append("group_notification")
            msgs.append(a[0])
        #print(msgs[i])

    # creating new columns  
       
    df['user'] = usernames
    df['message'] = msgs

    # dropping the old user_msg col.
    df.drop('user_msg', axis=1, inplace=True)
    
    return df

chat=input('Enter path of file: ')
format=input('Enter time format 12hr or 24hr: ')
name=input('Enter group name: ')
df= rawToDf(chat,format)
df

df['day']=df['date_time'].dt.strftime('%a')
df['month']=df['date_time'].dt.strftime('%b')
df['year']=df['date_time'].dt.year
df['date']=df['date_time'].apply(lambda x:x.date())

na=[]
for i in df.date_time:
  timestamp = datetime.datetime.timestamp(i)
  na.append(timestamp)
ar=np.array(na)
df['timestamp']=ar

def dayOfYear(date):
      days = [0,31,28,31,30,31,30,31,31,30,31,30,31]
      d = list(map(int,date.split("-")))
      if d[0] % 400 == 0:
         days[2]+=1
      elif d[0]%4 == 0 and d[0]%100!=0:
         days[2]+=1
      for i in range(1,len(days)):
         days[i]+=days[i-1]
      return days[d[1]-1]+d[2]

dataset=df.values
dataset

start=dataset[0][0].strftime('%Y-%m-%d')
start

date={}
msgLen={}
for i in range(39999):
  date[dataset[i][6].strftime("%Y-%m-%d")]=dataset[i][6].strftime("%Y-%m-%d")
  msgLen[dataset[i][6].strftime("%Y-%m-%d")]= msgLen.get(dataset[i][6].strftime("%Y-%m-%d"),0)+1

X=[]
Y=[]
for i in date:
  X.append(i)
  Y.append(msgLen[i])

fig, ax = plt.subplots(1, figsize=(20, 6))
major_ticks = np.arange(0, 50, 5)
ax.set_xticks(major_ticks)
ax.plot(X,Y)
plt.title('Messages sent per day')
plt.grid(b=True, which='major', color='#666666', linestyle='-',lw='0.5')
plt.show()

userMsg={}
for i in df.user:
  userMsg[i]=userMsg.get(i,0)+1

user=userMsg.keys()
msgCount=userMsg.values()
fig = plt.figure(figsize = (15, 5)) 
plt.bar(user,msgCount,align='center',width=0.4)
plt.xlabel("User name") 
plt.ylabel("Total messages since nov 21") 
plt.title(name) 
plt.show()

sorted_values = sorted(userMsg.values()) # Sort the values
sorted_dict = {}

for i in sorted_values:
    for k in userMsg.keys():
        if userMsg[k] == i:
            sorted_dict[k] = userMsg[k]
            break

print(sorted_dict)

out = dict(it.islice(sorted_dict.items(), 5))
tot=len(sorted_dict) 
new_dict= dict(it.islice(sorted_dict.items(), tot-5,tot))
new_dict['others']=sum(out.values())

def func(pct, allvalues): 
    absolute = int((pct / 100.0)*(39999.0)) 
    return "{:.1f}%\n({:d})".format(pct, absolute) 
  
# Creating plot 

wp = { 'linewidth' : 1, 'edgecolor' : "green" } 

fig, ax = plt.subplots(figsize =(10, 7)) 
wedges, texts, autotexts = ax.pie(new_dict.values(),  
                                  autopct = lambda pct: func(pct, new_dict.values()), 
                                  labels = new_dict.keys(), 
                                  shadow = True,
                                  startangle = 90, 
                                  wedgeprops = wp, 
                                  textprops = dict(color ="black")) 
ax.legend(wedges, new_dict.keys(), 
          title ="Username", 
          loc ="center left", 
          bbox_to_anchor =(1, 0.6, 0.5, 1)) 
  
plt.setp(autotexts, size = 8, weight ="bold") 
ax.set_title("User messages chart") 
  
# show plot 
plt.show()

wordList={}
for i in df.message:
  words=i.split()
  for word in words:
    if(word.isalpha()==False):
      continue
    if(len(word)<=1):
      continue
    word=word.lower()
    word = word.replace(".","")
    word = word.replace(",","")
    word = word.replace(":","")
    word = word.replace("\"","")
    word = word.replace("!","")
    word = word.replace("â€œ","")
    word = word.replace("â€˜","")
    word = word.replace("*","")
    wordList[word]=wordList.get(word,0)+1
wordList=OrderedDict(sorted(wordList.items()))

n_print=10
print("The {} most common words for "+name+ " are as follows\n".format(n_print))
word_counter = collections.Counter(wordList)
top10words={}
for word, count in word_counter.most_common(n_print):
    
    top10words[word]=count
top10words

fig = plt.figure(figsize = (15, 5)) 
plt.bar(top10words.keys(),top10words.values(),align='center',width=0.4)
plt.xlabel("Word") 
plt.ylabel("Count") 
plt.title(name) 
plt.show()

msgTime={}
for i in range(39999):
  h=dataset[i][0].strftime('%H')
  msgTime[h]=msgTime.get(h,0)+1

msgTime=OrderedDict(sorted(msgTime.items()))
fig = plt.figure(figsize = (15, 5)) 
plt.bar(msgTime.keys(),msgTime.values(),align='center',width=0.5)
plt.xlabel("Hour") 
plt.ylabel("Message count") 
plt.title("Most active hours of "+name) 
plt.show()

daywise={}
for i in df.date:
  daywise[i]=daywise.get(i,0)+1
daywise=OrderedDict(sorted(daywise.items()))

n_print=10
print("The {} days with most messages for "+name+ " are as follows\n".format(n_print))
day_counter = collections.Counter(daywise)

top10days={}
n_print=10
day_counter.most_common(n_print)
for day,count in day_counter.most_common(n_print):
    
    top10days[day.strftime("%d")+'/'+day.strftime("%m")+'/'+day.strftime("%Y")]=count
    print(top10days)

x=list(top10days.keys())
y=list(top10days.values())

fig = plt.figure(figsize = (16, 5)) 
plt.bar(x,y,align='center',width=0.5)
plt.xlabel("Day") 
plt.ylabel("Message Count") 
plt.title(name+" Most active days") 
plt.show()