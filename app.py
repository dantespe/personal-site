#! /usr/bin/env python
from flask import Flask, request, render_template
from datetime import datetime
from settings import Settings
import os
import requests

from pyextras.cache import Cache
from config import (
    NUM_ARTISTS,
    NUM_SONGS,
    LAST_FM_KEY,
    LAST_FM_UPDATED
)

# Use the App Engine Requests adapter. This makes sure that Requests uses
# URLFetch.
if Settings.get("PRODUCTION"):
    import requests_toolbelt.adapters.appengine
    requests_toolbelt.adapters.appengine.monkeypatch()

app = Flask(__name__)
cache = Cache()

@app.context_processor
def load():
    return {
        'now': datetime.now(),
        'updated': datetime(month=12, day=21, year=2018)
    }


@app.errorhandler(404)
def page_not_found(e):
    context = {
        'error': True,
        'url': request.base_url
    }
    return render_template("404.html", **context), 404


@app.route("/")
def index():
    context = {
        'header': "About"
    }
    return render_template('about.html', **context)


@app.route("/resume")
def resume():
    context = {
        'header': "Resume",
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
        'header': "Projects",
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


def update_last_fm_data(num_artists=NUM_ARTISTS, num_songs=NUM_SONGS):
    endpoint = "https://ws.audioscrobbler.com/2.0"
    api_key = Settings.get("LAST_FM_API_KEY")
    username = Settings.get("LAST_FM_USERNAME")

    params = {
        'method': 'user.gettopartists',
        'api_key': api_key,
        'user': username,
        'period': 'overall',
        'limit': num_artists,
        'format': 'json'
    }

    data = {
        "artists": [],
        "songs": []
    }
    try:
        response = requests.get(endpoint, params=params)

        for artist in response.json()['topartists']['artist']:
            data['artists'].append({
                "name": artist['name'],
                "rank": artist['@attr']['rank'],
                "img": artist["image"][1]["#text"]
            })
    except:
        print("Failed to updated the cache for artists.")

    params['method'] = "user.gettoptracks"
    params['limit'] = num_songs
    try:
        response = requests.get(endpoint, params=params)
        for song in response.json()['toptracks']['track']:
            data['songs'].append({
                "title": song['name'],
                "artist": song['artist']["name"],
                "rank": song['@attr']['rank'],
                "img": song["image"][1]["#text"]
            })
    except:
        print("Failed to updated the cache for songs.")

    cache.add(LAST_FM_KEY, data, timeDelta=1)
    cache.add(LAST_FM_UPDATED, datetime.now(), timeDelta=1)


@app.route("/music")
def music():
    if LAST_FM_KEY not in cache or cache.isExpired(LAST_FM_KEY):
        update_last_fm_data()

    context = {
        'header': "My Music",
        'artists': cache.get(LAST_FM_KEY)["artists"],
        'songs': cache.get(LAST_FM_KEY)["songs"],
        'last_updated': cache.get(LAST_FM_UPDATED, raiseError=False)
    }

    return render_template("music.html", **context)


@app.route("/contact")
def contact():
    context = {
        "header": "Contact",
        "contacts": []
    }

    # Instagram
    context['contacts'].append({
        "button": "fa-instagram",
        "link": "https://www.instagram.com/dspencer2019"
    })

    # Github
    context['contacts'].append({
        "button": "fa-github",
        "link": "https://www.github.com/dantespe"
    })

    # LinkedIn
    context['contacts'].append({
        "button": "fa-linkedin",
        "link": "https://www.linkedin.com/in/dante-spencer-290781b8/"
    })

    # Email
    context['contacts'].append({
        "button": "fa-envelope",
        "link": "mailto:dantespe@umich.edu"
    })

    return render_template("contact.html", **context)
