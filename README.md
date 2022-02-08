
# TMWRK WeatherApp

**Notice:** If this is **NOT** your first time pulling this repo, we highly recommend doing a fresh pull by cleaning out the repo you had pulled previously.

![image](https://user-images.githubusercontent.com/26980980/142302197-2fa0c125-19cb-496d-a485-95709bde2cd6.png)

The TMWRK WeatherApp is a sophisticated, cutting edge application that does more than just display the current weather. The front page of the app features cards with the following:
- A card of the searched/tab-selected city colored sky blue (day) or dark blue (night) for "today's" weather
- A card of the searched/tab-selected city colored indigo for "tomorrow's" weather
- A card of a geolocated city with a backdrop of the city
- A list of cards featuring weekly forecast for the searched/tab-selected city

This application also allows you to customize settings such as themes, preferred time (standard/military), and preferred unit of measurement (Fahrenheit/Celsius). Plus you can choose how you store cities in your bookmarks and reorder these cities. Furthermore, there's an intuitive search bar with an autocomplete dropdown, where you can add a newly-searched city to the front of the bookmark.

**More features:** If that's not enough, this application also has sidebar buttons that open windows for the tab-selected city:
- Wikipedia article
- Historical data
- Dining locations nearby
- Hourly forecast

# Installation / Requirements
This software requires the following dependencies:

`pip install PyQt5`
`pip install pyowm`
`pip install qtawesome`
`pip install qt-material`
`pip install geocoder`
`pip install requests`
`pip install pytz`
`pip install yelpapi`
`pip install matplotlib`
`pip install pillow`

Or alternatively, run this command located in this `WeatherApp/` directory:

`pip install -r requirements.txt`

# Usage
To begin, run `main.py`.

<!-- Introduce features on application startup! -->
### Application on startup
When you first run this app, a splash screen will appear indicating that the app is initializing.
![1](https://user-images.githubusercontent.com/26980980/141867696-88d6b1d6-036a-43ae-a6de-302781dafdba.gif)


<!-- Show themes! -->
### Tons of theme accents available
This application features 7 different accents. Also as you can see, the main displays are the search bar, the weather display, the side bar, and a bar for a list of city tabs.
![2](https://user-images.githubusercontent.com/26980980/141867837-2be14980-d45d-4d94-a33b-0f54efad8520.gif)


<!-- Show how to change settings! -->
### Changing settings
Clicking the settings button on the sidebar, you'll see that you can even change the default settings to features like dark theme and accent colors.
![3](https://user-images.githubusercontent.com/26980980/141867862-e52c1143-e889-4753-acf9-c36b53869e9f.gif)


<!-- Show how to search for cities -->
### Searching for cities
You can type in the following formats:
- <CITY_NAME, STATE_CODE>
  - San Francisco, CA
  - Nashville, TN
  - New York, NY
- <CITY_NAME, COUNTRY_CODE>
  - London, GB
  - Paris, FR
  - Tokyo, JP

To display the weather, click a city or hit enter in the dropdown after typing in the desired city in any of those format.
If the city isn't already in the tabs section, it'll be added at the very front.
![4](https://user-images.githubusercontent.com/26980980/141867917-a8f5da48-8a08-4b0b-a2cc-1d3421199eb8.gif)


<!-- Show how to manage bookmarks -->
### Viewing bookmarks
When you open bookmarks window, you'll see all of your stored cities.
In this window, you can reorder the cities and even remove cities.
![5](https://user-images.githubusercontent.com/26980980/141867956-70464251-5248-43aa-8c87-52c724146681.gif)


<!-- Show Wikipedia article for city -->
### Viewing city on Wikipedia
You can conveniently view your currently selected city on Wikipedia.
![6](https://user-images.githubusercontent.com/26980980/141868034-71afeeae-fec8-4337-8d8c-2f68d9053f74.gif)


<!-- Show hourly forecast -->
### Viewing hourly forecast
You can view weather by the hour for your selected city.
![7](https://user-images.githubusercontent.com/26980980/141868122-19fd6d22-6082-4ebc-8dfd-7b0620b95508.gif)


<!-- Show dining -->
### Viewing dining locations near selected city
You can also conveniently look up restaurants near the selected city.
![8](https://user-images.githubusercontent.com/26980980/141868370-70d0e09c-a7d5-4a09-9001-b1808f78edf2.gif)


<!-- Show historical data -->
### Viewing historical data for selected city
You can see a history of weather-related data for your selected city.
![9](https://user-images.githubusercontent.com/26980980/141868424-c91338ae-b71d-446b-96c0-e8178af32bfc.gif)


<!-- Conclude -->
### We hope you enjoy the WeatherApp
We strive for the best user-experience.
![10](https://user-images.githubusercontent.com/26980980/141868537-6a960893-28e2-4133-88d1-df03e5831e39.gif)


# Members of this project that put the teamwork in TMWRK
- Thomas (@Thomas-Neuefeind)
- Mahim (@mmathur20)
- William (@WillNJohnson)
- Robert (@RobertUTK)
- Kellen (@kellenrl)
