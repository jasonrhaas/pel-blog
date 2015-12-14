Title: Open Source
Date: 2010-12-03 10:20
Modified: 2010-12-05 19:30
Category: Open Source
Tags: open source, software
Slug: open-source
Authors: Jason Haas
Summary: Open Source software projects

## Open source 

I'm a big fan of open source, and anyone that has been working with software in the last 5 years knows that a ton of cutting edge software development is happening in the world of open source.  Open source combined with Github and *NIX is a powerful thing.  I like to contribute to open source whenever I can, but more importantly I try to learn from well respected code and developers.

The software world is strange because it seems to me that many developers don't bother to _learn_ from better programmers than themselves.  I think it's just as important to  _read_ and _understand_ good code as is it is to write your own.  Here are some projects that I follow, learn from, and occasionally contribute to:

### [streamparse](https://github.com/parsely/streamparse)

Streamparse allows you to run python code in the Storm framework.  I've modeled some of my coding style after this repository since it is pretty well done and Pythonic.

### [elastalert](https://github.com/Yelp/elastalert)

A handy alerting tool for Elastic Search, I use this to monitoring my data stream in Elastic Search.  I've written some custom alerts using this framework and hope to contribute more to the project.

### [kibana](https://github.com/elastic/kibana)

I use Kibana as a real-time visualization engine for data streams.  I follow their development pretty closely.

## My Github Projects ![Alt Text]({filename}/images/GitHub-Mark-64px.png)

A lot of the open source work I've done is thanks to my company, **IST Research.**  I've been fortunate to be able to use open source code for my job and also open source code back to the community where it makes sense.  For some of these projects I'm the primary contributer, and others are ones that I use frequently have some more minor contributions.

### [JSON Transporter](https://github.com/istresearch/json-transporter)

This project came out of my need to constantly hack together Python scripts and then push the (JSON) formated data out to various data stores like ElasticSearch, MongoDB, and Hbase.  I developed this tool for my own needs, but thought that others may also get some use out of it.  *Python hackers should never have to solve the same problem twice!*

### [Traptor](https://github.com/istresearch/traptor)

Traptor is a distributed Twitter collection engine.  It relies on a ruleset that is managed in Redis and distributes the data collection out to an arbitrary number of Traptor instances.

<!-- ### [Warden](https://github.com/istresearch/warden) -->
### Warden (open sourcing soon)

Warden is a simple web API to help keep track of all your `supervisor` processes spread across all your servers.  You can learn more about this excellent tool at [supervisord.org](http://supervisord.org)

### [Scrapy Cluster](https://github.com/istresearch/scrapy-cluster)

This is the engine that powers most of the web scraping at **IST Research.** Scrapy Cluster is a distributed web scraping tool that is able to scale up data collection very easily.

### [Pelican Blog](https://github.com/jasonrhaas/pel-blog)

Source code for this Blog.  I'm using a modified theme from [Pelican Themes](https://github.com/getpelican/pelican-themes/tree/master/aboutwilson)