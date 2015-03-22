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
THEME = 'pelican-bootstrap3'