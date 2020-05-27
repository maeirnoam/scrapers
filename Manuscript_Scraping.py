from bs4 import BeautifulSoup
import lxml
import requests
from PIL import Image
import io
import re
import os
from fpdf import FPDF
from urllib.request import Request, urlopen


def scrape_manuscripts(link):
    """

    :param link: such as : 'https://www.loc.gov/collections/manuscripts-in-st-catherines-monastery-mount-sinai/?fa=partof%3Amanuscripts+in+st.+catherine%27s+monastery%2C+mount+sinai%3A+microfilm+5012%3A+syriac&st=list&c=156'
    :return:
    """
    page = requests.get(link)
    # page = Request(link, headers={'User-Agent': 'Mozilla/5.0'})
    soup = BeautifulSoup(page.content, 'html.parser')
    all_mss = soup.find_all('span', {'class': 'item-description-title'})
    all_a = []
    for i in all_mss:
        temp = i.find_all('a')
        all_a.append(temp)
    ms_name = re.compile(r'(Syriac Manuscripts \d+)', re.DOTALL | re.MULTILINE)
    manuscripts = {}
    for i in range(len(all_a)):
        href = (all_a[i][0]['href'])
        name = re.search(ms_name, str(all_a[i][0].contents[0])).group()
        manuscripts.update({name: href})
    return manuscripts

def scrape_manifest(link):
    """

    :param link: such as: 'https://www.loc.gov/item/00279386292-ms'
    :return: the link for the json manifest of the specific manuscript
    """
    page = requests.get(link)
    soup = BeautifulSoup(page.content, 'html.parser')
    manifest_reg = re.compile(r'https.*?manifest.json')
    all_a = soup.find_all('a')
    for i in all_a:
        try:
            href = re.match(manifest_reg, i['href'])
            manifest = href.group()
            print('a number {} ref: {}'.format(all_a.index(i), manifest))
        except:
            continue
    return manifest


def scrape_images(ms_name, manifest):
    """

    :param manifest: such as: https://www.loc.gov/item/00279386292-ms/manifest.json
    :param ms_name: such as: Sinai Syr. 16
    :return:
    """
    pdf = FPDF()
    scrapeLink = manifest
    page = requests.get(scrapeLink)
    soup = BeautifulSoup(page.content, 'html.parser')
    json_contents = soup.contents
    temp = str(json_contents[0])
    full_images = re.compile(
        r'(https://tile.loc.gov/image-services/iiif/service:amed:amedmonastery:\d+-ms:\d+/full/pct:50/0/default.jpg)')
    images = re.findall(full_images, temp)
    for i in range(len(images)):
        imgName = '{}.jpg'.format(i + 1)
        req = Request(images[i], headers={'User-Agent': 'Mozilla/5.0'})
        webpage = urlopen(req).read()
        io_img = io.BytesIO(webpage)
        img = Image.open(io_img)
        img.save('{}/{}'.format(ms_name, imgName))
        pdf.add_page()
        pdf.image('{}/{}'.format(ms_name, imgName), h=210, w=190)
    pdf.output("{}/merged_jpgs.pdf".format(ms_name), "F")
    print('done scraping images to files')


def chars_to_jpg(x):
    return int(x[:-4])


def jpgs_to_pdf(ms_name):
    pdf = FPDF()
    imagelist = os.listdir(ms_name)
    for filename in sorted(imagelist, key=chars_to_jpg):
        with open('{}/{}'.format(ms_name, filename), 'rb') as thefile:
            pdf.add_page()
            pdf.image('{}/{}'.format(ms_name, filename), h=210, w=190)
    pdf.output("merged_jpgs.pdf", "F")
    print('done combining images to pdf')

def scrape_jpgs(ms_name, ms_number, first_page_link, last_page_link):
    """
    :param ms_name: ms_name = 'Syriac Manuscripts 256'
    :param ms_number: ms_number = '00279388227'
    :param first_page_link: first_page = 'https://tile.loc.gov/image-services/iiif/service:amed:amedmonastery:00279388227-ms:0001/full/pct:50/0/default.jpg'
    :param last_page_link: last_page = 'https://tile.loc.gov/image-services/iiif/service:amed:amedmonastery:00279388227-ms:0175/full/pct:50/0/default.jpg'
    :return: 
    """
    page_reg = re.compile(
        r'(https://tile.loc.gov/image-services/iiif/service:amed:amedmonastery:)(.+?)(-ms:)(\d+?)(/.+?)(.jpg)',
        re.DOTALL | re.MULTILINE | re.UNICODE)
    first = first_page_link
    last = last_page_link
    first_page = re.search(page_reg, first)
    last_page = re.search(page_reg, last)
    pages = [f"{i:04d}" for i in range(int(first_page.group(4)), int(last_page.group(4)))]

    images = []
    for i in pages:
        link = '{}{}{}{}{}{}'.format(first_page.group(1), ms_number, first_page.group(3), i,
                                     first_page.group(5), first_page.group(6))
        images.append(link)

    for i in range(len(images)):
        print(images[i])
        imgName = '{}.jpg'.format(i + 1)
        req = Request(images[i], headers={'User-Agent': 'Mozilla/5.0'})
        webpage = urlopen(req).read()
        io_img = io.BytesIO(webpage)
        img = Image.open(io_img)
        os.makedirs(ms_name, exist_ok=True)
        img.save('{}/{}'.format(ms_name, imgName))

link = 'https://www.loc.gov/collections/manuscripts-in-st-catherines-monastery-mount-sinai/?fa=partof%3Amanuscripts+in+st.+catherine%27s+monastery%2C+mount+sinai%3A+microfilm+5012%3A+syriac&st=list&c=156'
manuscripts_dict = scrape_manuscripts(link)
for (ms, address) in zip(manuscripts_dict.keys(), manuscripts_dict.values()):
    manifest = scrape_manifest(address)
    os.makedirs(ms)
    scrape_images(ms, manifest)