import bs4
import requests

def get_categories():
    req = requests.get("https://hire.withgoogle.com/public/jobs/grimmcocom") 
    soup = bs4.BeautifulSoup(req.content, features="html.parser") 
    return [div.attrs['data-department'] for div in soup.find_all("div", {"class": "bb-public-jobs-list__department-container"})]

def get_jobs_in_category(category):
    req = requests.get("https://hire.withgoogle.com/public/jobs/grimmcocom") 
    soup = bs4.BeautifulSoup(req.content, features="html.parser") 
    group = soup.find("div", {'data-department': lambda department: department and department.lower() == category.lower()})
    if not group:
        return None
    items = group.find_all('li')
    return [[item.find("span", {"class": "bb-public-jobs-list__job-item-title"}).getText(), item.find("span", {"class": "bb-public-jobs-list__job-item-location"}).getText(), item.find("a", {"class": "bb-public-jobs-list__item-link"}).attrs['href']] for item in items]
