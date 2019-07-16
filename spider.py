import requests
from bs4 import BeautifulSoup
import MySQLdb


def populate_table(region):
    if region == 'north east england':
        TABLE_NAME = "northeastengland"
    elif region == 'north west england':
        TABLE_NAME = "northwestengland"
    elif region == 'central england':
        TABLE_NAME = "centralengland"
    elif region == 'north wales':
        TABLE_NAME = "northwales"
    elif region == 'south wales':
        TABLE_NAME = "southwales"
    elif region == 'eastern central england':
        TABLE_NAME = "easterncentralengland"
    elif region == 'eastern england & east anglia':
        TABLE_NAME = "eastanglia"
    elif region == 'south west england':
        TABLE_NAME = "southwestengland"
    elif region == 'south and south east england':
        TABLE_NAME = "southeastengland"
    elif region == 'south west scotland':
        TABLE_NAME = "southwestscotland"
    elif region == 'south east scotland':
        TABLE_NAME = "southeastscotland"
    elif region == 'west central scotland':
        TABLE_NAME = "westcentralscotland"
    elif region == 'east central scotland':
        TABLE_NAME = "eastcentralscotland"
    elif region == 'scottish highlands':
        TABLE_NAME = "scottishhighlands"
    elif region == 'northern ireland':
        TABLE_NAME = "northernireland"
    else:
        return 'Not a valid region'


    con = MySQLdb.connect('localhost', 'root', 'password', 'cottages')
    cur = con.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS %s (
        ID INT UNIQUE NOT NULL AUTO_INCREMENT,
        Name VARCHAR(500) NULL,
        URL VARCHAR(500) NULL,
        offer VARCHAR(500) NULL,
        details VARCHAR(500) NULL,
        nights VARCHAR(500) NULL,
        price VARCHAR(500) NULL,
        per_night INT NULL,
        location VARCHAR(500) NULL,
        ref VARCHAR(500) NULL,
        LatLng VARCHAR(500) NULL,
        PRIMARY KEY (ID)) """  % (TABLE_NAME,))

    cleartable = "DELETE from %s" % (TABLE_NAME,)
    resetcount = "ALTER TABLE %s AUTO_INCREMENT = 1" % (TABLE_NAME,)

    cur.execute(cleartable)
    cur.execute(resetcount)
    con.commit()


    headers = {'User-Agent': 'Mozilla/5.0',
               'content-type': 'application/json',
               'Referer': 'https://www.independentcottages.co.uk/cottageAdvSearch.php'
               }
    payload = {'advUserSearch': region,
               'cot': '',
               'hotTub': '',
               'sleeps': '2',
               'romantic': '',
               'newDogs': 'd',
               'sky': '',
               'changeoverDay': 'Any',
               'accomType': 'd',
               'bath': '',
               'offRoadParking': '',
               'pubNear': '',
               'cdPlayer': '',
               'swimmingPool': '',
               'golf': '',
               'nights': 'Nights',
               'gamesRoom': '',
               'searchType': 'lao',
               'stables': '',
               'realFire': '',
               'tennis': '',
               'stablingOnsite': '',
               'microwave': '',
               'children': '',
               'washingMachine': '',
               'piano': '',
               'noRooms': 'Bedrooms',
               'dishWasher': '',
               'garden': '',
               'beachNear': '',
               'publicTransport': '',
               'familyActivity': '',
               'kingsizeBed': '',
               'bikeStorage': '',
               'smoking': 'd',
               'ssg': 'd',
               'tumbleDryer': '',
               'waterside': '',
               'groundFloorLiveSleep': '',
               'wheelchairAccess': '',
               'arrivalDate': 'dd%2Fmm%2fyyy',
               'dvd': '',
               'iPod': '',
               'shower': '',
               'broadband': '',
               'farmHoliday': '',
               'etcRating': '0',
               'fishing': '',
               'submitButton': 'Search'}

    def getdata(parsedhtml):
        for result in parsedhtml.find_all('div', attrs={'class':'searchResult'}):
            datadic = {}
            datadic['LatLng'] = result.find('div', 'mapLatLong').text

            for each in result.find_all('a'):
                if each.has_attr('title'):
                    if each['title'].startswith('View'):
                        link = each['href']
                        datadic['URL'] = link
                        datadic['ref'] = link.split('-ref')[-1]
                        datadic['Name'] = link.split('/')[-1].split('-ref')[0].replace('-', ' ')
                        datadic['location'] = link.split('.co.uk/')[-1].split('/')[0].replace('-', ' ')
            texts = result.find_all('div', attrs={'class':'offerText'})

            if len(texts) > 1:
                offer = texts[0].getText()
                datadic['offer'] = offer
                datadic['price'] = offer.split(u's - £')[-1]
                datadic['nights'] = offer.split(' for ')[-1].split(' nights -')[0]
                datadic['per_night'] = int(datadic['price'])/int(datadic['nights'])
                datadic['details'] = texts[1].getText()

            else:
                offer = texts[0].getText()
                datadic['offer'] = offer
                datadic['price'] = offer.split(u's - £')[-1]
                datadic['nights'] = offer.split(' for ')[-1].split(' nights -')[0]
                datadic['per_night'] = int(datadic['price'])/int(datadic['nights'])
                datadic['details'] = ''

            #print datadic
            logthis = "INSERT INTO {TABLE_NAME} (ID,Name,URL,offer,details,nights,price,per_night,location,ref,latlng) VALUES (NULL, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)".format(TABLE_NAME=TABLE_NAME)
            cur.execute(logthis, (datadic['Name'], datadic['URL'], datadic['offer'], datadic['details'], datadic['nights'],
                                  datadic['price'], datadic['per_night'], datadic['location'], datadic['ref'], datadic['LatLng']))


    session = requests.Session()
    session.post('http://www.independentcottages.co.uk/cottageSearch.php', headers=headers, data=payload)

    url = 'http://www.independentcottages.co.uk/cottageSearch.php?s='

    request = session.get(url)
    soup = BeautifulSoup(request.text, "html5lib")

    
    noleft = soup.find('div', attrs={'id':'srHeaderLeft'}).getText()
    start, end = noleft.split('page ')[1].split(' (')[0].split(' of ')
    print(noleft)

    #get first page info while it's loaded
    getdata(soup)

    #get page range
    mod = range(20, (int(end))*20, 20)

    #get every page after 1st one
    for n in mod:
        newurl = url + str(n)
        
        request = session.get(newurl)
        newsoup = BeautifulSoup(request.text, "html5lib")

        getdata(newsoup)

    con.commit()
    con.close()




regionlist = ['north west england',
              'north east england',
              'central england',
              'north wales',
              'south wales',
              'eastern central england',
              'eastern england & east anglia',
              'south west england',
              'south and south east england',
              'south west scotland',
              'south east scotland',
              'west central scotland',
              'east central scotland',
              'scottish highlands',
              'northern ireland'
              ]

for region in regionlist[0:1]:
    print('Gathering late deals from', region)
    try:
        populate_table(region)
    except IndexError:
        print('No results for', region)
