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


### How to generate gpx files
What the code does so you know I'm not being sneaky with your data...

1) After being pointed to where your `.zip` file lives
2) Extract it as a subfolder in `data/`
3)
