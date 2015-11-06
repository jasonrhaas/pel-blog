#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

AUTHOR = u'Jason Haas'
SITENAME = u'Tech Brew'
SITEURL = ''

PATH = 'content'

TIMEZONE = 'Europe/Paris'

DEFAULT_LANG = u'en'

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

# Include image folder
STATIC_PATHS = ['images', 'pages']

# Blogroll
LINKS = (('jasonrhaas.com', 'http://jasonrhaas.com'),
         # ('Python.org', 'http://python.org/'),
         # ('Jinja2', 'http://jinja.pocoo.org/'),
         # ('Bootstrap', 'http://getbootstrap.com/'),
         )

# Social widget
SOCIAL = (('Github', 'http://github.com/jasonrhaas'),
          ('Twitter', 'https://twitter.com/jasonrhaas'),
          ('LinkedIn', 'http://linkedin.com/in/jasonrhaas'),)

DEFAULT_PAGINATION = False

# Uncomment following line if you want document-relative URLs when developing
#RELATIVE_URLS = True
THEME = 'aboutwilson'

# pelican-sober settings
PELICAN_SOBER_ABOUT = "My name is Jason, and I <3 Python + Git"
PELICAN_SOBER_STICKY_SIDEBAR = False
PELICAN_SOBER_TWITTER_CARD_CREATOR = 'jasonrhaas'

# Other Theme settings
GITHUB_URL = 'http://github.com/jasonrhaas'
TWITTER_URL = 'http://twitter.com/jasonrhaas'
TWITTER_USERNAME = 'jasonrhaas'

# DISPLAY_PAGES_ON_MENU = True

# SITESUBTITLE = u'Just another tech blog'
