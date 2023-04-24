import random
import re
import json
from bs4 import BeautifulSoup
from requests import get, Session
from time import sleep

def get_headers() -> dict:
    # Returns header dictionary with user agent
    headers = {
    'User-Agent': ''
    }

    with open('user-agent.txt', 'r', encoding='utf8') as f:
        headers['User-Agent'] = random.choice(f.readlines()).strip('\n')
    
    return headers

def wait(min = 5, max = 10):
    # Waits seconds passed, both inclusive. Between 5 and 10 seconds by default
    random.seed()
    sleep(random.randint(min, max))

# Make user agent a global variable to avoid requests from different "browsers" with the same IP
URL_HEADERS = get_headers()

def sou_ch(set: dict):

    req = get(set['url'])

    if req.status_code == 200:
        soup = BeautifulSoup(req.content)
        chap = soup.body.find(class_='post-body')
    else:
        raise Exception(req.status_code)

    # Cleanup content
    [tag.decompose() for tag in chap.find_all('span')[1:]]
    [tag.decompose() for tag in chap.find_all('h3')[1:]]
    [tag.decompose() for tag in chap.find_all('div')]
    [tag.decompose() for tag in chap.find_all('a')]

    with open(f'Series/Death March/{set["name"]}.md', 'w', encoding='utf8') as f:
        f.write(chap.prettify())
    
    return

def sou_idx(url: str):
    # This will search chapters in the url and then save them locally
    req = get(url)
    
    if req.status_code == 200:
        soup = BeautifulSoup(req.content)
        idx = soup.body.find(class_='post-body').find_all('a', href=re.compile('sousetsuka'), string=re.compile('Chapter'))
    else:
        raise Exception(req.status_code)
    
    return [{'name': c.text, 'url': c.attrs['href']} for c in idx]

def nu_readlist(id = 81517, num = 0) -> list:

    s = Session()
    s.get(f'https://www.novelupdates.com/readlist/?uid={id}', headers=URL_HEADERS)
    formdata = {
        'action': 'nu_prevew',
        'pagenum': num,
        'intUserID': id,
        'isMobile': ''
    }
    wait()
    p = s.post('https://www.novelupdates.com/wp-admin/admin-ajax.php', headers=URL_HEADERS, data=formdata)
    response = json.loads(p.text[:-1])
    
    with open('readlist.json', 'w') as f:
        json.dump(response, f)

    table = BeautifulSoup(response['data'].encode('latin1').decode('utf-8'), 'lxml')

    return [{'Name': t.attrs['title'], 'Url': t.attrs['href']} for t in table.find_all('a') if '/series/' in t.attrs['href']]