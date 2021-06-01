from bs4 import BeautifulSoup
import requests
import pandas
import argparse
import connect

parser = argparse.ArgumentParser()
parser.add_argument("--max_page_num", help="Enter the number of web pages you want to parse:", type=int)
parser.add_argument("--dbname", help="Enter the number of web pages you want to parse:", type=str)
args = parser.parse_args()

headers = {'user-agent': 'your-own-user-agent/0.0.1'}

oyo_link = "https://www.oyorooms.com/hotels-in-bangalore/?page="

scraped_info_list = []

Max_page_num = args.max_page_num

connect.connect(args.dbname)

for page_num in range(1, Max_page_num):

    url = oyo_link + str(page_num)

    print("GET Request for: " + url)

    req = requests.get(url, headers=headers)

    content = req.content

    soup = BeautifulSoup(content, "html.parser")

    all_hotels = soup.find_all("div", {"class": "hotelCardListing"})

    for hotels in all_hotels:
        hotel_dict = {}

        hotel_dict["name"] = hotels.find("h3", {"class": "listingHotelDescription__hotelName"}).text
        hotel_dict["address"] = hotels.find("span", {"itemprop": "streetAddress"}).text
        hotel_dict["price"] = hotels.find("span", {"class": "listingPrice__finalPrice"}).text
        try:
            hotel_dict["rating"] = hotels.find("span", {"class": "hotelRating__ratingSummary"}).text
        except AttributeError:
            hotel_dict["rating"] = None

        parent_amenities_element = hotels.find("div", {"class": "amenityWrapper"})

        amenities_list = []

        for amenity in parent_amenities_element.find_all("div", {"class": "amenityWrapper__amenity"}):
            amenities_list.append(amenity.find("span", {"class": "d-body-sm"}).text.strip())

        hotel_dict["amenities"] = ", ".join(amenities_list[:-1])

        scraped_info_list.append(hotel_dict)
        connect.insert(args.dbname, tuple(hotel_dict.values()))
        

df = pandas.DataFrame(scraped_info_list)
print("Creating cvs file...")
df.to_csv("Oyo.csv")
connect.get_info(args.dbname)
