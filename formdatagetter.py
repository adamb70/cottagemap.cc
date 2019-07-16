from bs4 import BeautifulSoup

words = '''
<input type="hidden" name='searchType' id="searchType"  value="lao" />
<input type="hidden" name='sleeps' id="sleeps"  value="2" />
<input type="hidden" name='noRooms' id="noRooms"  value="" />
<input type="hidden" name='nights' id="nights"  value="" />

<input type="hidden" name='smoking' id="smoking"  value="d" />
<input type="hidden" name='newDogs' id="newDogs"  value="d" />
<input type="hidden" name='children' id="children"  value="" />
<input type="hidden" name='wheelchairAccess' id="wheelchairAccess"  value="" />
<input type="hidden" name='groundFloorLiveSleep' id="groundFloorLiveSleep"  value="" />
<input type="hidden" name='changeoverDay' id="changeoverDay"  value="Any" />
<input type="hidden" name='etcRating' id="etcRating"  value="0" />
<input type="hidden" name='arrivalDate' id="arrivalDate"  value="" />

<input type="hidden" name='realFire' id="realFire"  value="" />
<input type="hidden" name='hotTub' id="hotTub" value="" />
<input type="hidden" name='swimmingPool' id="swimmingPool" value="" />
<input type="hidden" name='garden' id="garden" value="" />
<input type="hidden" name='tennis' id="tennis" value="" />
<input type="hidden" name='fishing' id="fishing" value="" />
<input type="hidden" name='kingsizeBed' id="kingsizeBed" value="" />

<input type="hidden" name='offRoadParking' id="offRoadParking" value="" />
<input type="hidden" name='piano' id="piano" value="" />
<input type="hidden" name='gamesRoom' id="gamesRoom" value="" />

<input type="hidden" name='beachNear' id="beachNear" value="" />
<input type="hidden" name='pubNear' id="pubNear" value="" />
<input type="hidden" name='golf' id="golf" value="" />
<input type="hidden" name='stables' id="stables" value="" />
<input type="hidden" name='stablingOnsite' id="stablingOnsite" value="" />
<input type="hidden" name='publicTransport' id="publicTransport" value="" />
<input type="hidden" name='bikeStorage' id="bikeStorage" value="" />
<input type="hidden" name='waterside' id="waterside" value="" />
<input type="hidden" name='broadband' id="broadband" value="" />
<input type="hidden" name='bath' id="bath" value="" />
<input type="hidden" name='shower' id="shower" value="" />
<input type="hidden" name='dishWasher' id="dishWasher" value="" />
<input type="hidden" name='iPod' id="iPod" value="" />
<input type="hidden" name='dvd' id="dvd" value="" />
<input type="hidden" name='cdPlayer' id="cdPlayer"  value="" />
<input type="hidden" name='sky' id="sky" value="" />
<input type="hidden" name='washingMachine' id="washingMachine" value="" />
<input type="hidden" name='tumbleDryer' id="tumbleDryer" value="" />
<input type="hidden" name='microwave' id="microwave" value="" />
<input type="hidden" name='cot' id="cot" value="" />
<input type="hidden" name='romantic' id="romantic" value="" />
<input type="hidden" name='familyActivity' id="familyActivity" value="" />
<input type="hidden" name='farmHoliday' id="farmHoliday" value="" />
<input type="hidden" name='ssg' id="ssg" value="d" />
<input type="hidden" name='accomType' id="accomType" value="d" />


'''

html = BeautifulSoup(words, features='lxml')

mydict = {}

for n in html.find_all('input'):
    mydict[n['name']] = n['value']

print(str(mydict).replace(', ', ',\n'))
