
from bs4 import BeautifulSoup
import re
import requests 
import pandas as pd

login_url = "https://www.nevo.co.il/Authentication/UserLogin.aspx"
url = "ENTER YOUR URL FOR SEARCH RESULT"
domain = "https://www.nevo.co.il"
folder_path = "ENTER YOUR PATH"

session = requests.session()

# Perform login
def get_payload():
    log_in_data = BeautifulSoup(requests.get(login_url).text, 'html.parser')
    viewstate = log_in_data.find('input', {'name':'__VIEWSTATE'})['value']
    viewstategenerator = log_in_data.find('input', {'name':'__VIEWSTATEGENERATOR'})['value']
    return {
    "ctl00$ContentPlaceHolder1$LoginForm1$Login1$UserName": "ENTER YOUR USER NAME",
    "ctl00$ContentPlaceHolder1$LoginForm1$Login1$Password": "ENTER YOUR PASSWORD",
    '__VIEWSTATE':viewstate,
    "__VIEWSTATEGENERATOR":viewstategenerator,
    "__EVENTTARGET":"",
    "__EVENTARGUMENT":"",
    "ctl00$ContentPlaceHolder1$LoginForm1$Login1$LoginButton":"התחבר"}

result = session.post(login_url, data = get_payload())

# Scrape url
count = 0 
sentences = {}
while True:
    response = session.get(url)
    data = response.text
    soup = BeautifulSoup(data, "html.parser")
    docs = soup.find_all('div',{'role':"article"})
    for doc in docs:
        word_link = doc.find('div', {'class':'documentsLinks'}).find('a',{'title':'הורדת Word'})
        pdf_link = doc.find('div',{'class':'documentsLinks'}).find('a',{'title':'הורדת PDF'})
        title = doc.find('h5').text
        case_number = re.search('[0-9]+-([0-9][0-9]-)?[0-9][0-9]', title)
        court = re.search('\(.*\)', title)
        defendant_name = re.search('נ\'.*',title, re.S)
        date = doc.find('div', {'class':'resultProperties'}).find('span', string=re.compile('[0-9][0-9]/[0-9][0-9]/[0-9][0-9]')).text
        #print(date)
        defendant_fname = ""
        defendant_lname = ""
        if hasattr(case_number, 'group'):
            case_number = case_number.group(0)
        else:
            case_number = str(count)
        if hasattr(court, 'group'):
            court = court.group(0).strip("()")
        else:
            court =""
        if hasattr(defendant_name, 'group'):
            defendant_name = defendant_name.group(0).splitlines()[1].strip()
        else:
            defendant_name =" "
        if len(defendant_name.split(" ",1))==2:
            defendant_fname=defendant_name.split(" ",1)[0]
            defendant_lname = defendant_name.split(" ", 1)[1]
        else:
            defendant_fname=defendant_name.split(" ",1)[0]
        #print(word_link)
        print(title)
        #print(case_number)
        #print(court)
        #print(defendant_name)
        if word_link:
            with open(folder_path+case_number+'.doc', 'wb') as file:
                #print(domain+word_link.get('href'))
                responsetemp = session.get(domain+word_link.get('href'))
                file.write(responsetemp.content)
            count+=1
        else: 
            if pdf_link:
                with open(folder_path+case_number+'.pdf', 'wb') as file:
                    print(domain+pdf_link.get('href'))
                    responsetemp = session.get(domain+pdf_link.get('href'))
                    file.write(responsetemp.content)
                count+=1
        sentences[count] = [case_number, court, date, defendant_fname, defendant_lname]
    url_tag = soup.find('a',{'id':'ContentPlaceHolder1_SearchResultsTemplate1_Paging2_btnNext'})
    if url_tag.get('href'):
        url = domain + url_tag.get('href')
        #print(url)
    else:
        break
print(count)
sentences_df = pd.DataFrame.from_dict(sentences, orient="index", columns=['caseNumber', 'court','sentenceDate', 'defendantFName', 'defendantLName'])
sentences_df.to_csv(folder_path+"ENTER YOUR FILE NAME.csv",  encoding="utf_8-sig")