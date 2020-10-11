from selenium import webdriver
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.chrome import ChromeDriverManager
import time
from selenium.webdriver.chrome.options import Options
import requests
from bs4 import BeautifulSoup
from fake_headers import Headers
import os
import json
from facebook_scraper import get_posts
from oauth2client.service_account import ServiceAccountCredentials
import gspread
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from datetime import datetime
from fake_headers import Headers
from requests import get
from datetime import timedelta
LOGIN_URL = 'https://www.facebook.com/login.php'

def get_header():
    header = Headers(
        browser="chrome",  
        os="win", 
        headers=True  
    )
    return header.generate()

configurations = os.path.join(os.getcwd(),'setup','bot_settings.json')

def read_configuration_Data(fileName = configurations):
    try:
        f = open (fileName,'r')
    except:
        f = open (fileName,'w')
        f.close()
        print("[--] File {} Not Located. Creating new file, edit it and try again".format(fileName))
        time.sleep(15)
        sys.exit()

    data = json.load(f)
    try:
        return data['USERNAME'],data['PASSWORD'],data['PAGE'],data['REPORT_LINK']
    except Exception as e:
        print(e)
        print("[++] WRONG INPUT DATA IN 'input.json'.. Correct it and try again.")
        time.sleep(15)
        exit(1)


class Facebook():

    def __init__(self, email, password, page,report_link, browser='Chrome'):
        self.email = email
        self.password = password
        self.users = []
        self.report_link = report_link
        self.top_posts = []
        self.page = page
        user_profile_path = os.path.join(os.getcwd(),'data','profiles',self.email.replace("@",'').replace(".",'')+"_profile")
        if not os.path.exists(user_profile_path):
            os.mkdir(user_profile_path)
        if browser == 'Chrome':
            option = Options()
            option.add_argument("--disable-infobars")
            option.add_argument("start-maximized")
            option.add_argument("--disable-extensions")
            prefs = {"profile.default_content_setting_values.notifications" : 2}
            option.add_experimental_option("prefs",prefs)
            option.add_argument("user-data-dir={}".format(user_profile_path))
            self.driver = webdriver.Chrome(options=option,executable_path=os.path.join(os.getcwd(),'data','chromedriver.exe'))
        elif browser == 'Firefox':
            self.driver = webdriver.Firefox(executable_path=GeckoDriverManager().install())
        self.driver.get(LOGIN_URL)
        time.sleep(1)

    def clean(self):
        file1 = open(os.path.join(os.getcwd(),'data','users.txt'),"w+") 
        file1.writelines([]) 
        file1.close()
        file1 = open(os.path.join(os.getcwd(),'data','usernames.txt'),"w+") 
        file1.writelines([]) 
        file1.close()
        print("[+] cleaned files.")
    
    def save(self, data):
        with open(os.path.join(os.getcwd(),'data','users.txt'), 'a+') as f:
            for item in data:
                f.write("%s\n" % item)
            f.close()
        print('[+] Saved pages.')
    def read_posts(self):
        fileName = os.path.join(os.getcwd(),'data','data.json')
        try:
            f = open (fileName,'r')
        except:
            f = open (fileName,'w')
            f.close()
            print("[--] File {} Not Located. Creating new file, edit it and try again".format(fileName))
            time.sleep(15)
            sys.exit()
        data = json.load(f)
        try:
            return data
        except Exception as e:
            print(e)
            print("[++] WRONG INPUT DATA IN 'input.json'.. Correct it and try again.")
            time.sleep(15)
            exit(1)
    def read_Data(self):
        fileName = os.path.join(os.getcwd(),'data','posts.json')
        try:
            f = open (fileName,'r')
        except:
            f = open (fileName,'w')
            f.close()
            print("[--] File {} Not Located. Creating new file, edit it and try again".format(fileName))
            time.sleep(15)
            sys.exit()
        data = json.load(f)
        try:
            return data
        except Exception as e:
            print(e)
            print("[++] WRONG INPUT DATA IN 'input.json'.. Correct it and try again.")
            time.sleep(15)
            exit(1)
    
    def saveusernames(self,data):
        with open(os.path.join(os.getcwd(),'data','usernames.txt'), 'a+') as f:
            for item in data:
                f.write("%s\n" % item)
            f.close()
        print('[+] Saved usernames.')
    
    def saveposts(self,data):
        temp = self.read_Data()
        temp.extend(data)
        saved = temp
        with open(os.path.join(os.getcwd(),'data','posts.json'), 'w') as outfile:
            json.dump(saved, outfile)
        print('[+] Saved posts.')
    
    def login(self):
        el,st = 0,time.time()
        while el<20:
            if self.driver.current_url == "https://www.facebook.com/":
                print("[+] Logged in successfully.")
                return
            try:
                email_element = self.driver.find_element_by_id('email')
                email_element.send_keys(self.email) 
                password_element = self.driver.find_element_by_id('pass')
                password_element.send_keys(self.password) 
                login_button = self.driver.find_element_by_id('loginbutton')
                login_button.click() 
                time.sleep(5) 
                print("[+] Logged in successfully.")
                return
            except:
                pass
            el = time.time() - st
        print("[+] login failed.")
        while 1:pass
    
    def get_pages(self):
        print("[+] Getting pages list")
        url = self.page+"/insights/?referrer=page_insights_tab_button&amp%3Bcquick=jsc_c_v&amp%3Bcquick_token=AQ77ZBqlDpNQ6S7C&amp%3Bctarget=https%3A%2F%2Fwww.facebook.com"
        self.driver.get(url)
        time.sleep(10)
        x = self.driver.find_elements_by_xpath("//div[@class='rq0escxv l9j0dhe7 du4w35lb']")
        if(len(x)>0):
            #print("[+] iframe exists..")
            x = x[3].find_element_by_tag_name("div").find_element_by_tag_name("div").find_element_by_tag_name("div")
            u = x.find_elements_by_xpath("//div[@class='ina5je9e d2edcug0 datstx6m']")
            frame = u[0].find_element_by_tag_name("iframe")

            self.driver.switch_to.frame(frame)
            self.driver.implicitly_wait(30)

        v = self.driver.find_elements_by_tag_name("div")
        username = v[0].find_element_by_id("globalContainer")
        username = username.find_element_by_id("content")
        d = username.find_element_by_id("profile_page_insights_hubble")
        #d = d.find_element_by_id("u_0_z")
        cl = d.find_elements_by_class_name("_5don")
        f = cl[0].find_elements_by_xpath("//div[@class='_5dop _4-u2  _4-u8']")
        f = cl[0].find_elements_by_xpath("//table[@class='_5k45']")
        table = f[0]
        table = table.find_element_by_tag_name("tbody")
        username = table.find_elements_by_tag_name("td")
        last = None
        attempts = 0
        while True:
            try:
                last = username[len(username)-1].find_element_by_class_name("_58oy")
                if(last is None):
                    break
                last.click()
                time.sleep(3)
                username = table.find_elements_by_tag_name("td")
            except:
                break
        
        for i in range(0,len(username)):
            if(i%5==0):
                try:
                    y = username[i].find_element_by_class_name("_42ef")
                    name = y.find_element_by_tag_name("div").get_attribute("innerHTML")
                    if(name!="Papinha do BB"):
                        self.users.append(name)
                    if(len(self.users)==10):
                        self.save(self.users)
                        self.users = []
                except:
                    self.save(self.users)
                    break
    
    def get_profiles(self):
        text_file = open(os.path.join(os.getcwd(),'data','users.txt'), "r")
        lines = text_file.read().split('\n')
        u = lines
        u = u[:len(u)-1]
        print("[+] Got Pages. Total Pages: ",len(u))
        check = []
        for i in range(0,len(u)):
            check.append(False)
        usernames = []
        count = 0
        a = ""
        for i in u:
            print("[+] for user no: "+str(count)+" for user: "+str(i))
            
            url ="https://www.facebook.com/search/pages?q="+i+"&epa=SERP_TAB"
            self.driver.get(url)
            time.sleep(5)
            attempts = 0
            while(attempts<5):
                try:
                   
                    print("[+] attempt no.: ",attempts)
                    username = self.driver.find_element_by_tag_name("div")
                    x = self.driver.find_elements_by_xpath("//div[@class='rq0escxv l9j0dhe7 du4w35lb']")
                    if(len(x)>0):
                        #print("[+] found old div.")
                        x = x[3].find_element_by_tag_name("div").find_element_by_tag_name("div").find_element_by_tag_name("div").find_element_by_tag_name("div")
                        x = x.find_elements_by_xpath("//div[@aria-label='Preview of a search result']")
                        
                        x = x[0].find_element_by_tag_name("div").find_element_by_tag_name("div").find_element_by_tag_name("div").find_element_by_tag_name("div")
                        x = x.find_element_by_tag_name("div").find_element_by_tag_name("div").find_element_by_tag_name("div").find_element_by_tag_name("div")
                        x = x.find_element_by_tag_name("div").find_element_by_tag_name("div").find_element_by_tag_name("div").find_element_by_tag_name("div")
                        x = x.find_element_by_xpath("//div[@class='nc684nl6']")
                    
                        x = x.find_element_by_tag_name("a")
                        a = x.get_attribute("href")
                    else:
                        #print("[+] not found old div.")
                        x = self.driver.find_elements_by_tag_name("div")
                        username = x[0].find_element_by_id("globalContainer")
                        username = username.find_element_by_id("content")
                        d = username.find_element_by_id("browse_result_area")
                        x = d.find_element_by_xpath("//div[@class='_401d']")
                        x = x.find_element_by_xpath("//div[@class='_glj']")
                        
                        x = x.find_element_by_tag_name("a")
                        a = x.get_attribute("href")
                    
                    #print(a)
                    index = a.rfind(".com/")
                    index1 = a.rfind("/")
                    name = a[index+5:index1]
                    print("username: ",name)
                    
                    usernames.append(name)
                    check[count] = True
                    if(len(usernames)==10):
                        self.saveusernames(usernames)
                        usernames = []
                    break
                except:
                    attempts+=1
            count +=1
        d = 0
        for i in range(0,len(check)):
            if(check[i] == False):
                print("[+] colud not find user: "+str(u[i]))
            else:
                d+=1
            
        self.saveusernames(usernames)
        print("Total accounts: ", len(check))
        print("[+] Got Usernames for pages: ",d)
    
    def get_posts(self):
        saved = []
        with open(os.path.join(os.getcwd(),'data','posts.json'), 'w') as outfile:
            json.dump(saved, outfile)
        text_file = open(os.path.join(os.getcwd(),'data','usernames.txt'), "r")
        lines = text_file.read().split('\n')
        u = lines
        u = u[:len(u)-1]
        print("[+] Finding Recent Post for {} pages.".format(len(u)))
        top = []
        c = 0
        start_date = datetime.now() - timedelta(days=7)
        start_date = start_date.date()
        all_list = []
        k = 0
        print("[+] Posts from After: ", start_date)
        for i in u:
            try:
                top = []
                print("[+] for user no.: "+k+"for: "+i)
                k+=1
                data = {}
                data['username'] = i
                for post in get_posts(i,pages=50):
                    posts = {}
                    #print("[+] Getting info...")
                    post_timestamp = post['time'].timestamp()
                    post_date = datetime.fromtimestamp(post_timestamp).date() 
                    #print("[+] post date: ",post_date)
                    if(post_date<start_date):
                        break
                    posts["_id"] = "https://www.facebook.com/"+i+"/posts/"+str(post['post_id'])
                    posts["likes"] = post['likes']
                    posts["comments"] = post['comments']
                    posts["profile_link"] = "https://www.facebook.com/"+i
                    top.append(posts)
                data['recent_posts'] = top 
                #print(data)
                all_list.append(data)  
                self.saveposts(all_list)
                all_list = []
                
            except:
                pass
        print("[+] Got All Recent Posts.")
            
    def get_reactions(self):
        print("[+] Getting Top Post...")
        r=""
        saved = []
        with open(os.path.join(os.getcwd(),'data','data.json'), 'w') as outfile:
            json.dump(saved, outfile)
        top_posts = []
        data = self.read_Data()
        count = 0
        for i in data:
            print("[+] for user no: "+str(count)+" for username: "+ i["username"]))
            count+=1
            if(len(i['recent_posts'])==0):
                print("[+] No recent posts")
            else:
                print("[+] Recent posts: ", len(i['recent_posts']))
                for j in i['recent_posts']:
                    print(j['_id'])
                    self.driver.get(j['_id'])
                    time.sleep(3)
                    at = 0
                    j['reactions']  = j['likes']
                    j['engagement_rate'] = j['reactions'] + j['comments']
                    while(at<10):
                        print("Attempt no.: ",at)
                        try:

                            x = self.driver.find_elements_by_xpath("//div[@class='rq0escxv l9j0dhe7 du4w35lb']")
                            if(len(x)>0):
                                #print("[+] old div")
                                x = x[3].find_element_by_tag_name("div").find_element_by_tag_name("div").find_element_by_tag_name("div")
                                
                                x = x.find_element_by_xpath("//div[@class='du4w35lb l9j0dhe7']").find_element_by_tag_name("div")
                                x = x.find_element_by_xpath("//div[@class='j83agx80 cbu4d94t']").find_element_by_tag_name("div")
                                x = x.find_element_by_xpath("//div[@class='stjgntxs ni8dbmo4 l82x9zwi uo3d90p7 h905i5nu monazrh9']").find_element_by_tag_name("div").find_element_by_tag_name("div").find_element_by_tag_name("div").find_element_by_tag_name("div")
                                x = x.find_element_by_xpath("//div[@class='bp9cbjyn j83agx80 buofh1pr ni8dbmo4 stjgntxs']").find_element_by_tag_name("span")
                                x = x.find_element_by_xpath("//span[@class='gpro0wi8 cwj9ozl2 bzsjyuwj ja2t1vim']")
                                x = x.find_element_by_xpath("//span[@class='pcp91wgn']")
                                
                                r = x.get_attribute("innerHTML")
                            else:
                                #print("[+] new div")
                                """
                                """
                                username = self.driver.find_element_by_id("globalContainer")
                                username = username.find_element_by_id("content")
                                
                                x = username.find_element_by_xpath("//div[@class='clearfix']")
                                x = x.find_element_by_xpath("//div[@class='_1qkq _1ql0']")
                                
                                x = x.find_element_by_xpath("//div[@class='clearfix']")
                                x = x.find_element_by_xpath("//div[@class='_2pie _14i5 _1qkq _1qkx']")
                                x = x.find_element_by_xpath("//div[@class='_1xnd']")
                                
                                x = x.find_element_by_xpath("//div[@class='permalinkPost']")
                                x = x.find_element_by_xpath("//div[@class='_3ccb']")
                                
                                x = x.find_element_by_xpath("//div[@class='_4299']")
                                
                                x = x.find_element_by_xpath("//span[@class='_81hb']")
                                r = x.get_attribute("innerHTML")
                            if('K' in r):
                                ind = r.rfind('K')
                                r = r[0:ind]
                                r = (float)(r)
                                r = r*1000
                            elif('M' in r):
                                ind = r.rfind('M')
                                r = r[0:ind]
                                r = (float)(r)
                                r = r*1000000
                            else:
                                r = (float)(r)
                            
                            j['reactions'] = r
                            j['engagement_rate'] = r + j['comments']
                            print("Reactions: ",r)
                            print("Comments: ", j['comments'])
                            break
                        except:
                            at+=1
                            pass
                   
                top = sorted(i['recent_posts'], key = lambda k: k['engagement_rate'],reverse=True)
        
                top_posts.append(top[0])
            
            
        top_posts = sorted(top_posts, key = lambda i: i['engagement_rate'],reverse=True)
        saved = top_posts[0:10]
        with open(os.path.join(os.getcwd(),'data','data.json'), 'w') as outfile:
            json.dump(saved, outfile)    
        print("[+] Got Top Posts.")    
        self.driver.quit()           
    def report_generate(self):
        self.top_posts = self.read_posts()
        CLIENT_SECRET_FILE = os.path.join(os.getcwd(), "data", "client_secret.json")
        scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name(CLIENT_SECRET_FILE, scope)
        client = gspread.authorize(creds)
        sheet = client.open("Facebook_Report").sheet1
        sheet.update_cell(1, 1, "Profile_link")
        sheet.update_cell(1, 2, "Engagement rate")
        sheet.update_cell(1, 3, "Post id")
        sheet.update_cell(1, 4, "Reactions")
        sheet.update_cell(1, 5, "Comments")
        for i in range(0,len(self.top_posts)):
            sheet.update_cell(i+2,1,self.top_posts[i]['profile_link'])
            sheet.update_cell(i+2,2,self.top_posts[i]['engagement_rate'])
            sheet.update_cell(i+2,3,self.top_posts[i]['_id'])
            sheet.update_cell(i+2,4,self.top_posts[i]['reactions'])
            sheet.update_cell(i+2,5,self.top_posts[i]['comments'])
        print('Google sheet made.')
        print("You can access google sheet at: ")
        print(self.report_link)   
        
if __name__ == '__main__':
    data = read_configuration_Data()
    fb = Facebook(email=data[0], password=data[1],page=data[2],report_link=data[3] browser='Chrome')
    fb.clean()
    fb.login()
    fb.get_pages()
    fb.get_profiles()
    fb.get_posts()
    fb.get_reactions()
    fb.report_generate()



