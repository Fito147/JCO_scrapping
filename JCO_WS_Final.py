from bs4 import BeautifulSoup
import requests
import pandas as pd
import re
import time

url = 'https://ascopubs.org/loi/jco'
time.sleep(3)
page = requests.get(url, headers={'User-Agent':'Your BrowserUser-Agent'})
soup = BeautifulSoup(page.content, "html.parser")

#%% Buscar que obtener de cada item (url,Issue,Fecha)

def extraer_info (links):
        web = 'https://ascopubs.org' + links.a['href']
        data = links.find('span', class_="issue_inner_container").get_text().split()
        return (web, data[0:2], data[2:5])
#%% Obtener todas las URL de la pagina

raw_data = [extraer_info(links) for links in soup.find_all('div', class_="js_issue row")]
df1 = pd.DataFrame (raw_data, columns=('Pagina Web', 'Issue', 'Fecha'))
df1.to_csv('JCO_ALL_ISSUE.csv', index=False)

issue_full_list = list (df1['Pagina Web'].astype(str).tolist())
#%%
#%%
#%% Segunda Capa
# Buscar que obtener de cada item (url, titulo y seccion de cada paper)

def extraer_info_paper (link_paper):
    doi = link_paper.find('a', class_="ref nowrap full")['href']
    title = link_paper.find('span', class_="hlFld-Title").get_text()
    return (title, doi, "https://ascopubs.org" + doi)
#%% Obtener todos los papes de la pagina

def procesar_paginas(n): 
    issue_url = issue_full_list[n]
    time.sleep(3)
    page = requests.get(issue_url, headers={'User-Agent':'Your BrowserUser-Agent'})
    soup = BeautifulSoup(page.content, "html.parser")
    papers_data = [extraer_info_paper(link_paper) for link_paper in soup.find_all('table', class_="articleEntry")]
    return pd.DataFrame(papers_data, columns=('Titulos', 'DOI', 'URL'))
#%% Scrapping en la cantidad de paginas que queremos

df2 = pd.concat([procesar_paginas(n) for n in range(0,10)], ignore_index=True)
df2.to_csv('JCO_20XX_URLS.csv', index=False)

pages = list (df2['URL'].astype(str).tolist())

#%%
#%%
#%% Tercera Capa
# Sacar info paper a paper (DOI, titulo, Volume&Issue, first Athor, Last Author, Section)

titles=list()
authors=list()
dois=list()
volume=list()
section=list()

for n in pages:
    time.sleep(3)
    page = requests.get(n, headers={'User-Agent':'Your BrowserUser-Agent'})
    soup = BeautifulSoup(page.content, "html.parser")

    #Title
    tls=re.sub(r'\|.*', "", soup.title.text)
    titles.append(tls)
    # #Author 
    all_ath = list(map(lambda i : i.text, filter(lambda i : i.text!='Search for articles by this author', soup.find_all("a", class_="entryAuthor"))))
    authors.append(all_ath)
    # DOI
    all_doi = list(map(lambda i : i.get('href'), soup.find_all('link')))
    dois.append(all_doi[2])
    # # section
    sct = soup.find_all('h2', limit=1)
    section.append(sct)
    # # Volume-Issue
    vol = list(map(lambda i : i.text, filter(lambda i : i.text!= 'Newest Articles' and i.text!='Current Issue', soup.find_all(href=re.compile('/toc/jco')))))
    volume.append(vol)

    df = pd.DataFrame({"Title": titles, "Authors": authors, "DOI": dois, "Section": section, "Vol-Issue": volume})
    
    df.to_csv('JCO_20XX.csv', index=False)


#%%



#%%
