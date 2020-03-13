#!/usr/bin/env python3
import argparse
import requests
from sys import exit
from time import sleep
from random import choice
from threading import Thread
from bs4 import BeautifulSoup
import xlwt
import xlrd
import json

requests.packages.urllib3.disable_warnings()
USER_AGENTS = [line.strip() for line in open('user_agents.txt')]

class ScrapeEngine():
    URL = {'google': 'https://www.google.com/search?q=site:linkedin.com/in+"{}"&num=100&start={}',
           'bing': 'https://www.bing.com/search?q=site:linkedin.com/in+"{}"&first={}'}

    def __init__(self):
        self.linkedin = {}
        self.running = True

    def timer(self, time):
        sleep(time)
        self.running = False

    def search(self, search_engine, company_name, timeout, jitter):
        self.running = True  # Define search as "running" after init(), not used in DNS_Enum
        Thread(target=self.timer, args=(timeout,), daemon=True).start()  # Start timeout thread
        self.search_links = 0  # Total Links found by search engine
        self.name_count = 0  # Total names found from linkedin
        found_names = 0  # Local count to detect when no new names are found

        while self.running:
            if self.search_links > 0 and found_names == self.name_count:
                return self.linkedin

            found_names = self.name_count
            self.name_search(search_engine, self.search_links, company_name, jitter)
        return self.linkedin

    def name_search(self, search_engine, count, company_name, jitter):
        url = self.URL[search_engine].format(company_name, count)

        for link in get_links(get_request(url, 3)):
            url = str(link.get('href')).lower()

            if (search_engine+".com") not in url and not url.startswith("/"):
                self.search_links += 1

                if "linkedin.com/in" in url and self.extract_linkedin(link, company_name) :
                    self.name_count += 1
        sleep(jitter)

    def extract_linkedin(self, link, company_name):
        if debug:
            print("[*] Parsing Linkedin User: {}".format(link.text))

        if safe and company_name.lower() not in link.text.lower():
            return False

        try:
            x = link.text.split("|")[0]
            x = x.split("...")[0]

            # Extract Name (if title provided)
            if "–" in x:
                name = link.text.split("–")[0].rstrip().lstrip()
            elif "-" in x:
                name = link.text.split("-")[0].rstrip().lstrip()
            elif "|" in x:
                name = link.text.split("|")[0].rstrip().lstrip()
            else:
                name = x

            try:
                # Quick split to extract title, but focus on name
                title = link.text.split("-")[1].rstrip().lstrip()
                if "..." in title:
                    title = title.split("...")[0].rstrip().lstrip()
                if "|" in title:
                    title = title.split("|")[0].rstrip().lstrip()
            except:
                title = "N/A"
            tmp = name.split(' ')
            name = ''.join(e for e in tmp[0] if e.isalnum()) + " " + ''.join(e for e in tmp[1] if e.isalnum())

            # Catch 1st letter last name: Fname L.
            tmp = name.split(' ')

            if len(tmp[0]) <= 1 or len(tmp[-1]) <=1:
                raise Exception("\'{}\' Failed name parsing".format(link.text))
            elif tmp[0].endswith((".","|")) or tmp[-1].endswith((".","|")):
                raise Exception("\'{}\' Failed name parsing".format(link.text))

            if name not in self.linkedin:
                self.linkedin[name] = {}
                self.linkedin[name]['last'] = name.split(' ')[1].lower().rstrip().lstrip()
                self.linkedin[name]['first'] = name.split(' ')[0].lower().rstrip().lstrip()
                self.linkedin[name]['title'] = title.strip().lower().rstrip().lstrip()
                return True

        except Exception as e:
            if debug:
                print("[!] Debug: {}".format(str(e)))
        return False


def get_links(raw_response):
    # Returns a list of links from raw requests input
    links = []
    soup = BeautifulSoup(raw_response.content, 'html.parser')
    for link in soup.findAll('a'):
        try:
            links.append(link)
        except:
            pass
    return links


def get_request(link, timeout):
    # HTTP(S) GET request w/ user defined timeout
    head = {
        'User-Agent': '{}'.format(choice(USER_AGENTS)),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'}
    return requests.get(link, headers=head, verify=False, timeout=timeout)


def main(args):
    found_names = {}
    search = ['google', 'bing']
    banner()
    if args.email_format == 1:
        print("Email format jsmith@company.xyz chosen")
    elif args.email_format == 2:
        print("Email format johnsmith@company.xyz chosen")
    elif args.email_format == 3:
        print("Email format johns@company.xyz chosen")
    elif args.email_format == 4:
        print("Email format smithj@company.xyz chosen")
    elif args.email_format == 5:
        print("Email format john.smith@company.xyz chosen")
    elif args.email_format == 6:
        print("Email format smith.john@company.xyz chosen")

    q = 1
    w = 2 # NOTE: Variable W is for when working within spreadsheet. Python starts at 0 and counts upwards from there. Excel starts at 1, causing there to be a downwards shift in cells within formulas.
    wb = xlwt.Workbook()
    ws = wb.add_sheet('Scraped LinkedIn Employees', cell_overwrite_ok=True)
    compname = args.company_name
    compname = compname[:-4] + "Scraped.xls"

    col_offset = 10
    col_fname = 0
    col_lname = 1
    col_job = 2
    col_email = 3
    col_pwned = 4
    col_breaches = 5
    col_passwords = 6

    f_name = "First Name:"
    l_name = "Last Name:"
    job_name = "Job Title:"
    email_name = "Email:"

    pwned_name = "Pwned:"
    breaches_name = "Breaches:"
    passwords_name = "Passwords Breached:"

    ws.write(0, col_fname, f_name)
    ws.write(0, col_lname, l_name)
    ws.write(0, col_job, job_name)
    ws.write(0, col_email, email_name) 
    
    if args.hibp != "":
        ws.write(0, col_pwned, pwned_name)
        ws.write(0, col_breaches, breaches_name)
        ws.write(0, col_passwords, passwords_name)

    f_size = len(f_name)
    l_size = len(l_name)
    job_size = len(job_name)
    email_size = len(email_name)
    pwned_size = len(pwned_name)
    breaches_size = len(breaches_name)
    passwords_size = len(passwords_name)

    for site in search:

        lkin = ScrapeEngine().search(site, args.company_name, args.timeout, args.jitter)

        if lkin:
            breaches_pass = []
            hibp_url = "https://haveibeenpwned.com/api/v3/breaches"
            response = requests.get(hibp_url, headers={'hibp-api-key':args.hibp})
            response_json = json.loads(response.content)

            for breach in response_json:
                if "Passwords" in breach["DataClasses"]:
                    breaches_pass.append(breach["Name"])

            for name, data in lkin.items():
                 
                fname = data['first']
                lname = data['last']
                job = data['title']

                if len(fname) > f_size:
                    f_size = len(fname)
                if len(lname) > f_size:
                    l_size = len(lname)
                if len(job) > job_size:
                    job_size = len(job)
                
                ws.write(q, col_fname, fname)
                ws.write(q, col_lname, lname)
                ws.write(q, col_job, job)


                if args.email_format == 1:
                    email = fname[0]+lname+"@"+args.email_domain
                    # jsmith first_initial last
                elif args.email_format == 2:
                    email = fname+lname+"@"+args.email_domain
                    # johnsmith first last
                elif args.email_format == 3:
                    email = fname+lname[0]+"@"+args.email_domain
                    # johns first last_initial
                elif args.email_format == 4:
                    email = lname+fname[0]+"@"+args.email_domain
                    # smithj
                elif args.email_format == 5:
                    email = fname+"."+lname+"@"+args.email_domain
                    # john.smith
                elif args.email_format == 6:
                    email = lname+"."+fname+"@"+args.email_domain
                    # smith.john
                elif args.email_format == 7:
                    email = lname+"@"+args.email_domain
                    #smith


                if len(email) > email_size:
                    email_size = len(email)

                ws.write(q, col_email, email)


                if args.hibp != "":
                    hibp_url = "https://haveibeenpwned.com/api/v3/breachedaccount/"
                    hibp_email = email
                    hibp_request = hibp_url + hibp_email

                    sleep(1.5)

                    response = requests.get(hibp_request, headers={'hibp-api-key':args.hibp})

                    response_code = response.status_code

                    print(response_code,email)

                    if response_code == 200:
                        ws.write(q, col_pwned, "Y")

                        response_json = json.loads(response.content)

                        breaches_string = ""
                        passwords_string = ""

                        breached_n = len(response_json)

                        for i in range(0, breached_n):
                            breach = response_json[i]["Name"]

                            # Adds breach to breach list.
                            breaches_string += breach
                            if i != breached_n-1:
                                breaches_string += ", "

                            # If breach contains passwords, adds it to pass_breach list.
                            if breach in breaches_pass:

                                if len(passwords_string) != 0:
                                    passwords_string += " - "

                                passwords_string += breach


                        if len(breaches_string) > breaches_size:
                            breaches_size = len(breaches_string)
                        if len(passwords_string) > passwords_size:
                            passwords_size = len(passwords_string)


                        # Writes breached services.
                        ws.write(q, col_breaches, breaches_string)
                        ws.write(q, col_passwords, passwords_string)


                    else:
                        ws.write(q, col_pwned, "N")

                w = w + 1
                q = q + 1

                id = data['first'] + ":" + data['last']

                if name and id not in found_names:
                    found_names[id] = data

        ws.col(col_fname).width = 257 * f_size + col_offset
        ws.col(col_lname).width = 257 * l_size + col_offset
        ws.col(col_job).width = 257 * job_size + col_offset
        ws.col(col_email).width = 257 * email_size + col_offset
        ws.col(col_pwned).width = 257 * 8 + col_offset
        ws.col(col_breaches).width = 257 * breaches_size + col_offset
        ws.col(col_passwords).width = 257 * passwords_size + col_offset

        wb.save(compname)
    print("Scrape Complete!")
def banner():
    print("""

 /$$                             /$$     /$$       /$$           /$$                       /$$
| $$                            | $$    | $$      |__/          | $$                      | $$
| $$        /$$$$$$   /$$$$$$  /$$$$$$  | $$       /$$ /$$$$$$$ | $$   /$$  /$$$$$$   /$$$$$$$
| $$       /$$__  $$ /$$__  $$|_  $$_/  | $$      | $$| $$__  $$| $$  /$$/ /$$__  $$ /$$__  $$
| $$      | $$$$$$$$| $$$$$$$$  | $$    | $$      | $$| $$  \ $$| $$$$$$/ | $$$$$$$$| $$  | $$
| $$      | $$_____/| $$_____/  | $$ /$$| $$      | $$| $$  | $$| $$_  $$ | $$_____/| $$  | $$
| $$$$$$$$|  $$$$$$$|  $$$$$$$  |  $$$$/| $$$$$$$$| $$| $$  | $$| $$ \  $$|  $$$$$$$|  $$$$$$$
|________/ \_______/ \_______/   \___/  |________/|__/|__/  |__/|__/  \__/ \_______/ \_______/
                                                                                              
Based off of https://github.com/m8r0wn/CrossLinked
Modified by Ronnie Bartwitz and @Horshark on Github
""")

if __name__ == '__main__':
    VERSION = "1.0"
    args = argparse.ArgumentParser(description="", formatter_class=argparse.RawTextHelpFormatter, usage=argparse.SUPPRESS)
    args.add_argument('-t', dest='timeout', type=int, default=25,help='Timeout [seconds] for search threads (Default: 25)')
    args.add_argument('-j', dest='jitter', type=float, default=0,help='Jitter for scraping evasion (Default: 0)')
    args.add_argument('-s', "--safe", dest="safe", action='store_true',help="Only parse names with company in title (Reduces false positives)")
    args.add_argument('-e', "--email-domain", required=True, dest="email_domain", help="Include the email domain for email-generation (Example: microsoft.com) ")
    args.add_argument('-p', "--hibp", type=str, required=False, dest="hibp", default="", help="Runs all of the emails through HaveIBeenPwned's API and will list pwned accounts, API key is a required argument.")
    args.add_argument('-f', "--email-format", dest="email_format", required=True,type=int,default=1, help="Generates emails based on various formats, 1=jsmith 2=johnsmith 3=johns 4=smithj 5=john.smith 6=smith.john 7=smith")
    args.add_argument(dest='company_name', nargs='+', help='Target company name')
    args = args.parse_args()
    safe = args.safe
    debug = False
    args.company_name = args.company_name[0]
    try:
        main(args)
    except KeyboardInterrupt:
        print("[!] Key event detected, closing...")
        exit(0)
