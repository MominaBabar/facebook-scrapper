######################################################## 
              PURPOSE OF PROGRAM
########################################################
This program will scrape the names of all the accounts that the facebook page has added to their "PAGES TO WATCH" list and find their most engaging post. Then the top most egaging posts of them are recorded in a google sheet which the client can access. 

It was done as a freelancing project for the client whose job was to fing the top 10 enagaging posts.


######################################################## 
             STEPS TO USE PROGRAM
########################################################


1. Download project file.
2. Open project directory and install all required modules.
   cd facebook-scrapper
   pip install dependeny-name
3. Go to setup/bot_settings.json to enter email and password of    dummy account in relavent fields. 

4. Generate key for using google sheets. Use this link: https://www.twilio.com/blog/2017/02/an-easy-way-to-read-and-write-to-a-google-spreadsheet-in-python.html
5. Copy client_secret.json file in data directory. 
6. Go to setup/bot_settings.json, add report link file. Add link to facebook page in relavent fields. 
7. Run facebook.py.
   python facebook.py
8. After program finishes you canopen google sheet link to check results. 
