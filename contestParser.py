from contests import Contest
from datetime import datetime
import requests
def Codeforces():
    upcoming=[]
    ContestApi=requests.get('https://codeforces.com/api/contest.list')
    ApiJsonResponse=ContestApi.json()
    for contest in ApiJsonResponse['result']:
        if(contest['phase']=='FINISHED'):
            break
        ContestObj=Contest(contest['name'],'',datetime.utcfromtimestamp(int(contest['startTimeSeconds'])).strftime('%Y-%m-%d %H:%M:%S'),'http://www.codeforces.com') 
        upcoming.append(ContestObj)
    return upcoming
