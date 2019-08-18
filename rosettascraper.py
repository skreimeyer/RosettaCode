import bs4
import requests
import sqlite3
from multiprocessing import Pool
import json
import os
import pdb


'''
Download all the pages from Rosettacode.org to make quantitative comparisons
between Python and other languages.
'''
### Initialize our db to save results ###
def initdb():
    con = sqlite3.connect("rosettacode.db")
    cur = con.cursor()
    cur.execute(
    '''CREATE TABLE IF NOT EXISTS task
    (id INTEGER PRIMARY KEY AUTOINCREMENT, task TEXT)''')
    cur.execute(
    '''CREATE TABLE IF NOT EXISTS language
    (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE)''')
    cur.execute(
    '''CREATE TABLE IF NOT EXISTS code
    (id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL,
    lang_id INTEGER NOT NULL,
    loc INTEGER,
    code BLOB,
    FOREIGN KEY(task_id) REFERENCES tasks(id),
    FOREIGN KEY(lang_id) REFERENCES language(id))''')
    con.commit()
    return cur,con


### scrape ###
def get_links():
    req = requests.get("https://rosettacode.org/wiki/Category:Programming_Tasks")
    soup = bs4.BeautifulSoup(req.text,'lxml')
    taskblock = soup.find("div",class_="mw-category")
    links =  taskblock.find_all("a")
    links = [l['href'] for l in links]
    return links

def scrape(link):
    # take an anchor tag, make an HTTP request and return a dictionary with the
    # information to be inserted into our sqlite db.
    domain = "https://rosettacode.org"
    task_name = link[6:]
    data = {"task":task_name,"blocks":[]}
    r = requests.get(domain+link,timeout=5)
    s = bs4.BeautifulSoup(r.content,'lxml')
    headers = s.find_all("h2")[1:]
    for h in headers:
        lang = h.text[:-6]
        block = h.find_next("pre")
        loc = len(block.find_all('br'))+1
        datum = {
        "lang":lang,
        "loc":loc,
        "block":str(block)
        }
        data["blocks"].append(datum);
    # Dump data to JSON file just in case script fails
    # And it will fail . . .
    with open("backup/"+task_name+"_data.json","w") as outfile:
        json.dump(data,outfile)
    return None

def insert(datablock,cur,con):
    #populate SQLite with our scraped information
    cur.execute("INSERT INTO task(task) values (?)",(datablock['task'],))
    task_id =  cur.execute("SELECT id FROM task WHERE task = (?)",
    (datablock['task'],)).fetchone()[0]
    for block in datablock['blocks']:
        loc = block['loc']
        b = block['block']
        cur.execute(
        "INSERT OR IGNORE INTO language (name) VALUES (?)",(block['lang'],)
        )
        lang_id = cur.execute("SELECT id FROM language WHERE name = (?)",(block['lang'],)).fetchone()[0]
        cur.execute("INSERT INTO code (task_id,lang_id,loc,code) VALUES (?,?,?,?)",
        (task_id,lang_id,loc,b,))
    con.commit()


if __name__ == "__main__":
    print("initializing db...")
    cur,con = initdb()
    #pdb.set_trace()
    print("fetching links...")
    links = get_links()
    ### now we have to filter out the ones we already have ###
    old_links = ["/wiki/"+f.strip("_data.json") for f in os.listdir("backup")]
    links = [l for l in links if l not in old_links]
    # Pool processes for time
    print("starting pool...")
    try:
        with Pool(8) as pool:
            data = pool.map(scrape,links)
        print("Data retrieved. Making insertions into SQLite db...")
    except:
        print("pool failed")

    ### get data from our JSON files ###

    files = os.listdir("backup")
    for f in files:
        with open("backup/"+f,"r") as infile:
            data = json.load(infile)
            try:
                insert(data,cur,con)
            except Exception as e:
                print('-'*25)
                print(e)
                pdb.set_trace()
    print("Done")
    con.close()
    exit()
