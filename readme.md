# L33tLinked

Hello dear reader! Welcome to my modification of CrossLinked (Can be found here: https://github.com/m8r0wn/CrossLinked ). Crosslink/L33tLinked is a LinkedIn scraping tool that utilizes both Google and Bing to grab LinkedIn profiles. Whats the use for this? Well, collecting all known employees in a comapny can be used on a red-team op for searching for employees that are involved in Data Breaches. It's simple enough to take the info you'll recieve here and run the info through the Dehashed/Have I Been Pwned API to determine if the user was affected by a data breach!

## Setup
```bash
git clone https://github.com/Sq00ky/L33tLinked.git
cd L33tLinked
pip3 install -r requirements.txt
```
## Current Syntax
```bash
python3 leetlinked.py <companyname> -f ""
# Syntax above will output a file called <company>Scraped.xls
```

## Todo:

```
Implement more email formats, lastnamef, firstlast, fl, etc.
Implement HIBP API 
Completely re-write tool so it's not based on someone elses 
```

Modified by Ronnie Bartwitz / Ronnie Bartwitz
