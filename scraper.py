# -*- coding: utf-8 -*-
"""
Created on Sun Mar 22 13:33:05 2020

@author: CJ
"""


import requests 
import os
import hashlib
import re
import ast
from bs4 import BeautifulSoup
from nltk.stem import PorterStemmer
from time import sleep,time

class ProjectScraper():
    def __init__(self):    
        self.allowed_domains = ['https://s2.smu.edu/~fmoore']
        self.start_url = 'https://s2.smu.edu/~fmoore'
        self.url_frontier = ['https://s2.smu.edu/~fmoore']
        self.disallowed  = []
        self.ext_blacklist = ['.com','.edu','.gov']
        self.docs_to_scrape = []
        self.docs_not_to_scrape = []
        self.page_titles = []
        self.broken_links = []
        self.external_links = []
        self.page_meta = {}
        self.dictionary = set([])
        self.postings = {}
        self.hexkeys = set([])
        self.seen = []
        self.stemmer = PorterStemmer()
        
        
    def get_disallowed(self):
        html = requests.get(self.start_url + '/robots.txt')
        robots_text = html.text
        soup = BeautifulSoup(robots_text,'html.parser')
        soup_text = soup.get_text()
        list_soup = soup_text.split('\n')
        
        for i in list_soup:
            if '#' in i:
                continue
            
            else:
               temp = i.split(':')[1].strip()
               self.disallowed.append(self.start_url + temp)
               
    def get_urls_to_crawl(self):
        count = 0
        while(len(self.url_frontier) > count):
           
            html = ''
    
            while html == '':
                print(self.url_frontier[count])
                
                try:      
                    html = requests.get(self.url_frontier[count])
                    
                except:
                    print('Connection Failed Trying Again in 3 Seconds')
                    sleep(3)
            text = html.text
            soup = BeautifulSoup(text,'html.parser')
       
            if self.start_url in self.url_frontier[count]:
                
                toindex = True
                
                for meta in soup.find_all('meta'):
                    self.page_meta[self.url_frontier[count]] = []
                    self.page_meta[self.url_frontier[count]].append(meta['content'])
                    if 'noindex' in meta['content']:
                        toindex = False
                
                if (soup.title):
                    
                    if '404' in soup.title.string:
                        self.broken_links.append(self.url_frontier[count])
                        count +=1
                        continue
                    
                    else:
                        self.page_titles.append(soup.title.string)   
    
                else:
                    self.page_titles.append(self.url_frontier[count].split('/')[-1])

                
                temp_ = self.url_frontier[count].split('/')
                
                if '.txt' in temp_[-1] or '.php' in temp_[-1]:
                    if toindex and self.url_frontier[count] not in self.broken_links:
                        self.docs_to_scrape.append(self.url_frontier[count])
                        del temp_[-1]
                    
                    else:
                        self.docs_not_to_scrape.append(self.url_frontier[count])
                        del temp_[-1]
                
                elif '.htm' in temp_[-1]:
                    if toindex and self.url_frontier[count] not in self.broken_links:
                        self.docs_to_scrape.append(self.url_frontier[count])
                        del temp_[-1]
                    else:
                        self.docs_not_to_scrape.append(self.url_frontier[count]) 
                        del temp_[-1]
                        
                elif '.' in temp_[-1]:
                    self.docs_not_to_scrape.append(self.url_frontier[count])

                temp_ = '/'.join(temp_)
                  
                for a in soup.find_all('a', href = True):
                    
                    if ':' not in a['href']:
                
                        if '.' not in self.url_frontier[count]:                     
                            new_url = temp_ + '/' + a['href']
                        
                        else:
                            new_url = temp_ + '/' + a['href']
                  
                        if new_url not in self.url_frontier:
                            
                            baddir = False
                            for d in self.disallowed:
                                if d in new_url:
                                    baddir = True
                            
                            if not baddir:
                                self.url_frontier.append(temp_ + '/' + a['href']) 
                                    
                    elif 'http' in a['href'] and a['href'] not in self.external_links:
                        self.external_links.append(a['href'])
                  
            count+=1
            
        if not os.path.isfile(os.path.join(os.getcwd(),'lines_to_read.txt')):
            open('lines_to_read.txt','a').close()
        
        with open('lines_to_read.txt','r+') as file:
            text = file.readlines()
            for url in self.docs_to_scrape:
                if (url+'\n') not in text:
                    text.append(url+'\n')
                
            file.write(''.join(text))
        
                                
    def get_document_text(self):
        
        self.get_hexkeys()
        
        newlines = []
        
        if self.docs_to_scrape:
            
            
            
            for url in self.docs_to_scrape:
                filename = url.split('/')[-1]
                print(url)

                html = ''
    
                while html == '':
                    print(url)
                    
                    try:      
                        html = requests.get(url)
                        
                    except:
                        print('Connection Failed Trying Again in 3 Seconds')
                        sleep(3)
                        
                text = html.text        
                soup = BeautifulSoup(text,'html.parser')
                
                if soup.title:
                    title = soup.title.text
                    soup.title.decompose()
                    
                else:
                    title = filename
                
                
                with open('doc_repo/temp.txt','w',encoding='utf-8') as outfile:
                    new_text = re.sub(r'[^\x00-\x7F]+',' ',soup.get_text().replace('\n',''))
                    outfile.writelines(new_text)
                if self.hashfile(os.getcwd()+'/doc_repo/temp.txt'):
                    print('getting text from: ' + filename)
                    os.rename(os.getcwd()+'/doc_repo/temp.txt',os.getcwd()+'/doc_repo/' + filename)
                    newlines.append(str(url.strip(),filename,title))
            
                else:
                    self.seen.append(url)    
                
            
                        
        else:
            with open('lines_to_read.txt') as filelinks:
                links = filelinks.readlines()
                
            for url in links:
                filename = url.split('/')[-1].strip()
                html = ''
    
                while html == '':
                    print(url.strip())
                    
                    try:      
                        html = requests.get(url.strip())
                        
                    except:
                        print('Connection Failed Trying Again in 3 Seconds')
                        sleep(3)
                text = html.text
                soup = BeautifulSoup(text,'html.parser')
                
                if soup.title:
                    title = soup.title.text
                    soup.title.decompose()
                    
                else:
                    title = filename
                    
                print(title)
                
                with open('doc_repo/temp.txt','w',encoding='utf-8') as outfile:
                    new_text = re.sub(r'[^\x00-\x7F]+',' ',soup.get_text().replace('\n',''))
                    outfile.writelines(new_text)
                if self.hashfile(os.getcwd()+'/doc_repo/temp.txt'):
                    print('getting text from: ' + filename)
                    os.rename(os.getcwd()+'/doc_repo/temp.txt',os.getcwd()+'/doc_repo/' + filename)
                    newlines.append(str((url.strip(),filename,title)))
                
                else:
                    self.seen.append(url)
                    
        if newlines:      
            with open('index.txt','w') as file:
                file.write('\n'.join(newlines))    
                
        if os.path.isfile(os.path.join(os.getcwd(),'doc_repo/temp.txt')):
            os.remove(os.path.join(os.getcwd(),'doc_repo/temp.txt'))    
                    
    def get_hexkeys(self):
        for root,dirs,files in os.walk(os.getcwd()):
            for file in files: 
                if 'doc_repo' in os.path.join(root,file):                
                    self.hashfile(os.path.join(root,file))
    
                     
     
    def hashfile(self,path, blocksize = 65536):
        templist = list(self.hexkeys)
        
        afile = open(path, 'rb')
        hasher = hashlib.md5()
        buf = afile.read(blocksize)
        while len(buf) > 0:
            hasher.update(buf)
            buf = afile.read(blocksize)
        afile.close()
        self.hexkeys.add(hasher.hexdigest())
        if len(self.hexkeys) > len(templist):
            return True
        else:
            return False 

    def make_dict_postings(self):
        
        with open('index.txt','r') as index_file:
            index = index_file.readlines()
        for i in range(len(index)):           
            index[i] = ast.literal_eval(index[i])[1]
            
        
        for root,dirs,files in os.walk(os.getcwd()):
             for file in files:
                if 'doc_repo' in os.path.join(root,file):
  
                    with open(os.path.join(root,file),'r') as cur_file:
                        text = ''.join(cur_file.readlines())
                        text = re.sub(r'[\'\"?,!/{};()$*+\\\[\]<>=*;&#%]','',text)
                        text = re.sub(r'[@.]',' ', text)
                        text = re.sub(r'\n',' ',text)
                        text = re.sub(r'(\d)([a-zA-z])|([a-zA-z])(\d)',r'\1 \2',text)                       
                        text = re.sub(r':(?=..(?<!\d:\d\d))','',text)
                        text = re.sub(r'([-])',' ',text)
                        text = re.sub(r'((?<=[a-z])[A-Z])',r' \1',text)
                        text = text.split()
                        
                        count = 0
                        for word in text:
                            if word.strip() != '':
                                
                                self.dictionary.add(self.stemmer.stem(word.strip()))
                                
                                if self.stemmer.stem(word.strip()) in self.postings.keys():
                                    self.postings[self.stemmer.stem(word.strip())].append((index.index(file),count))
                                
                                else:
                                  self.postings[self.stemmer.stem(word.strip())] = [(index.index(file),count)]
                                  
                                count+=1
                                
                        
        with open('stemmed_dictionary.txt','w') as outfile:
            dictlist = list(self.dictionary)
            dictlist.sort()
            outfile.write('\n'.join(dictlist))
            
        with open('stemmed_postings_list.txt','w') as outfile:
            for key in self.postings.keys():
                self.postings[key].sort()
                outfile.write(key + ':\t' + str(self.postings[key]) +'\n')
                
                
    def dump_everything_to_file(self):
        with open('dump.txt','w') as file:
            file.write('Documents to index: ' + str(self.docs_to_scrape) + '\n')
            file.write('Documents not to index: ' + str(self.docs_not_to_scrape) + '\n')
            file.write('Page Titles: ' + str(self.page_titles) + '\n')
            file.write('broken links: ' + str(self.broken_links) + '\n')
            file.write('duplicates: ' + str(self.seen) + '\n')                        
                        
            
    
    
if __name__ == '__main__':
    start = time()
    scraper = ProjectScraper()
    scraper.get_disallowed()
    scraper.get_urls_to_crawl()
    scraper.get_document_text()
    scraper.make_dict_postings()
    scraper.dump_everything_to_file()
    print(time() - start)
    
    