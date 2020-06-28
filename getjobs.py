import requests
import json

def get_all_jobs():
    """ Get a listing of all of the jobs that GRIMM has posted
        Returns a list of dictionaries containing:
            desc
            additional
            url
            category
            location
    """
    req = requests.get("https://api.lever.co/v0/postings/grimm-co?&mode=json")
    # error checking
    if req.status_code != 200:
        raise Exception # TODO: make this the right kind of exception
    js = json.loads(req.content)
    # the keys that matter: additionalPlain descriptionPlain hostedUrl
    jobs = list()
    # no change to the objects, so no TOCTOU. This is not the pythonic way to do it, but I can only handle so many try/excepts.
    for job in js:
        keys = job.keys()
        jobcontent = dict()
        if "text" in keys:
            jobcontent["title"] = job["text"]
        if "descriptionPlain" in keys:
            jobcontent["desc"] = job["descriptionPlain"]
        if "additionalPlain" in keys:
            jobcontent["additional"] = job["additionalPlain"]
        if "hostedUrl" in keys:
            jobcontent["url"] = job["hostedUrl"]
        if "categories" in keys:
            # ugh more ugly code don't do this
            if "commitment" in job["categories"].keys(): 
                jobcontent["category"] = job["categories"]["commitment"]
            if "location" in job["categories"].keys():
                jobcontent["location"] = job["categories"]["location"]
        jobs.append(jobcontent)
    return jobs

def get_categories():
    """ Get a list of categories for open jobs at GRIMM """
    req = requests.get("https://api.lever.co/v0/postings/grimm-co?&mode=json")
    # error checking
    if req.status_code != 200:
        raise Exception # TODO: make this the right kind of exception
    js = json.loads(req.content)
    categories = set()
    for job in js:
        try:
            categories.add(job["categories"]["commitment"])
        except KeyError:
            pass
    return categories

def get_jobs_in_category(category):
    req = requests.get("https://api.lever.co/v0/postings/grimm-co?&mode=json")
    # error checking
    if req.status_code != 200:
        raise Exception # TODO: make this the right kind of exception
    js = json.loads(req.content)
    jobs = list()
    # no change to the objects, so no TOCTOU. This is not the pythonic way to do it, but I can only handle so many try/excepts.
    for job in js:
        if job["categories"]["commitment"] != category:
            continue
        keys = job.keys()
        jobcontent = dict()
        if "text" in keys:
            jobcontent["title"] = job["text"]
        if "descriptionPlain" in keys:
            jobcontent["desc"] = job["descriptionPlain"]
        if "additionalPlain" in keys:
            jobcontent["additional"] = job["additionalPlain"]
        if "hostedUrl" in keys:
            jobcontent["url"] = job["hostedUrl"]
        if "categories" in keys:
            # ugh more ugly code don't do this
            if "commitment" in job["categories"].keys(): 
                jobcontent["category"] = job["categories"]["commitment"]
            if "location" in job["categories"].keys():
                jobcontent["location"] = job["categories"]["location"]
        jobs.append(jobcontent)
    return jobs

def formatjob(job):
    """ take in the job dictionary and return a pretty string """
    outstr = f"""
Job Title: {job["title"]}
Category: {job["category"]}
Location: {job["location"]}
Job Desc: {job["desc"]}
Additional: {job["additional"]}
URL: {job["url"]}
"""
    return outstr

