#! /usr/bin/env python

from flask import Flask
from flask import render_template
from datetime import datetime
import git
import requests
import os

app = Flask(__name__)

@app.context_processor
def load():
    g = git.Git('.')
    return {
        'now': datetime.now(),
        'updated': g.log().split("Date:")[-1].strip().split('\n')[0].split(' -')[0]
    }


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


@app.route("/")
def index():
    return render_template('about.html')


@app.route("/resume")
def resume():
    context = {
        'jobs': []
    }

    # Add Google
    if datetime.now() > datetime(month=6, day=1, year=2019):
        context['jobs'].append({
            "title": "Software Engineer, Tools and Infrastructure",
            "department": "Google Cloud Platform",
            "company": "Google",
            "timeline": "June 2019 - Present",
            "points": [],
        })
    else:
        context['jobs'].append({
            "title": "Incoming Software Engineer, Tools and Infrastructure",
            "department": "Google Cloud Platform",
            "company": "Google",
            "timeline": "Starting June 2019",
            "points": [],
        })

    # Add ARC-TS
    arc_ts = {
        "title": "Computer Consultant/Engineer",
        "department": "Advanced Research Computing",
        "company": "the University of Michigan",
        "points": [
            "Designed system infrastructure for continuous integration development across 1300+ high-performing computing (HPC) clusters",
            "Engineerined container application allowing for a horizontal scalable system",
            "Prototyped a continuous integration (CI) framework to increase workplace productivity"
        ]
    }
    if datetime.now() < datetime(month=5, day=31, year=2019):
        arc_ts['timeline'] = "May 2016 - Present"
    else:
        arc_ts['timeline'] = "May 2016 - May 2019"
    context['jobs'].append(arc_ts)

    # Add Boeing
    context['jobs'].append({
        "title": "Information Technology Intern",
        "department": "Cyber Intelligence Technologies",
        "company": "The Boeing Company",
        "timeline": "May 2018 - Aug 2018",
        "points": [
            'Diminished system downtime by implementing a web portal to monitor application status',
            'Integrated backend support to import service data into web portal application data',
            'Investigated network security procedures to streamline cyber security incident responses'
        ],
    })

    # Add CSV
    context['jobs'].append({
        "title": "Software Developer Intern",
        "department": "",
        "company": "City Side Ventures",
        "timeline": "May 2016 - Dec 2016",
        "points": [
            "Delivered production Django web applications to startups preparing for Series A funding",
            "Established development workflow to increase deadline success rate from 70% to 90%",
            "Collaborated with a large team of developers in an agile environment"
        ]
    })
    # Add ITS
    context['jobs'].append({
        "title": "Intern",
        "department": "Information Technology Services",
        "company": "the University of Michigan",
        "timeline": "May 2016 - Aug 2016",
        "points": [
            "Implemented core components for a diversity, equity, and inclusion website for faculty",
            "Orchestrated modular development environment for easy turn-over and management",
            "Deployed robust, automated test suites to alleviate development processes"
        ]
    })
    return render_template("resume.html", **context)


@app.route("/projects")
def projects():
    context = {
        'projects': [[]]
    }

    def append_project(projects, project):
        if len(projects[-1]) == 3:
            projects.append([])
        projects[-1].append(project)

    # Passgen
    project = {
        "name": "Passgen",
        "img": "passgen.png",
        "description": "A command-line tool to create secure passwords. Built in C++ and highly portable.",
        "link": "https://github.com/dantespe/Passgen"
    }
    append_project(context['projects'], project)

    # Caen
    project = {
        "name": "CAEN",
        "img": "caen.png",
        "description": "A Dockerfile used to simiultate on-campus CAEN envirnoment. Used to run code in a sandbox.",
        "link": "https://github.com/dantespe/caen"
    }
    append_project(context['projects'], project)

    return render_template("projects.html", **context)


@app.route("/music")
def music():
    NUM_ARTIST = 10
    NUM_SONGS = 50

    context = {
        'artists': [],
        'songs': []
    }

    endpoint = "https://ws.audioscrobbler.com/2.0"
    api_key = os.environ["LAST_FM_API_KEY"]
    username = os.environ["LAST_FM_USERNAME"]

    params = {
        'method': 'user.gettopartists',
        'api_key': api_key,
        'user': username,
        'period': 'overall',
        'limit': NUM_ARTIST,
        'format': 'json'
    }

    response = requests.get(endpoint, params=params)
    try:
        for artist in response.json()['topartists']['artist']:
            context['artists'].append({
                "name": artist['name'],
                "rank": artist['@attr']['rank'],
                "img": artist["image"][1]["#text"]
            })
    except:
        pass

    params['method'] = "user.gettoptracks"
    params['limit'] = NUM_SONGS
    response = requests.get(endpoint, params=params)

    try:
        for song in response.json()['toptracks']['track']:
            context['songs'].append({
                "title": song['name'],
                "artist": song['artist']["name"],
                "rank": song['@attr']['rank'],
                "img": song["image"][1]["#text"]
            })
    except:
        pass
    print(response.url)

    return render_template("music.html", **context)
