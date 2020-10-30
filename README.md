# strava-nator
**TL;DR**: Programmatically format and upload Samsung Health exercise data to Strava


### Background
Inspired by [this article](https://www.dcrainmaker.com/2019/03/export-data-samsung-watch-galaxy-health-app.html) and [this repo](https://github.com/shaderzz/gpxmaker).

I have been using Samsung Health and a Galaxy Active 2 for a few months to track my running and biking. I recently decided to start using Strava as well so I could join
a few groups with friends and co-workers.

I follow instructions I found to go into the Samsung Health app and link it to my Strava account. Countless articles and Reddit posts say it could take hours or days for
my historical exercise information to be uploaded to Strava.

A week went by and I'm still waiting.

So I wrote this.


### How to get Samsung Data
Follow the instructions in the article in the **Background** section to download the folder
of all the information Samsung Health has on you (gotta love GDPR).

Compress it as a `.zip` and find a way to get it from your phone to your computer.


### How to setup your Python environment
1) *optional* setup a virtualenv using Python3.7
2) `pip3 install -r requirements.txt`
3) *optional* Create a Strava app following [these instructions](https://developers.strava.com/docs/getting-started/)
4) *optional* Make a .env file with your STRAVA_CLIENT_ID and STRAVA_CLIENT_SECRET


(virtualenv's are good practice)

(you need to create a Strava app if you want the script to upload files for you)


### How to generate gpx files
What the code does so you know I'm not being sneaky with your data...

1) After being pointed to where your `.zip` file lives
2) Extract it as a subfolder in `data/`
3) Find all exercise files and group them by exercise type (run, hike, ride etc.)
4) Merge all of the files together and ignore ones without lat/long data
5) Do some grouping of timestamps to account for different GPS points in SHealth and Strava
6) Generate GPX files and add heart rate info and cadence when available
7) Save them under a custom directory in `data/<your zip file>/`

#### How you should do it
Run the command `python3 cli.py generate <path to zip>`

(you should see a printed list of the files that are created)


### How to upload gpx files
Big thanks to [this repo](https://github.com/hozn/stravalib) for giving me the code I needed to setup this part!

What the code does so you know I'm not being sneaky with your data...

1) Starts a local webserver so the script can get the API token to upload to your Strava account
2) This server is started in a separate thread so the MainThread can do its thang
3) The OAuth flow you follow in the browser sends data back to your local webserver not to me
4) Checks local txt file to make sure no duplicates are being uploaded
5) Crunches some numbers and prompts you in the terminal a few times to make sure you're ready to go
6) Starts the upload making sure to track any errors and respect Strava's rate limiting

#### How you should do it
Run the command `python3 cli.py upload <path to zip>`

(you should see a printed list of the files that are uploaded correctly)
