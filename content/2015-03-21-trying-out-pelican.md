---
layout: post
title: Trying Out Pelican
category: blogs
tags: pelican, jekyll, fabric, python
---

So as I mentioned in my first post, I decided to start my blog using Jekyll because it seemed to be the most widely used while still being fairly lightweight. However, as I began to look at trying to customize the site, I found the structure and templating system a little bit weird and unfamiliar.

I use `Python` a lot in my day job, and after looking through the documentation pelican I liked it's Pythonic style. Also, I tended to like the Pelican themes better than the ones for Jekyll.

Since both Jekyll and pelican use markdown for their HTML generation, it's fairly easy to create blogs for both of them. I may host one at `blog.jasonrhaas.com/jek` and one at `blog.jasonrhaas.com/pel` and then just have one or the other redirect to the main domain. The only real difference for post generation is the top header information. For example, on Jekyll, it looks like this:

	:::yaml
	---
	layout: 
	title: Trying Out Pelican
	categories: [blogs]
	tags: [blogs, pelican]
	published: True
	---

And on Pelican, it looks like this:

	:::yaml
	Title: Trying Out Pelican
	Date: 2015-03-21
	Category: blogs

My plan is to control all of My blog posts in a separate repository that only contains markdown information. I will create a fabric deployment for each type of blog. For example,

	:::python
	def jek_prep():
		local("cp *.md ~/repos/jek-blog/_posts")
		# + other tasks
	def pel_prep():
		local("cp *.md ~/repos/pel-blog/content")
		# + other tasks

For reference, here is my fabric deploy for the jekyll blog.

	:::python
	from fabric.api import local

	host = 'jasonrhaas.com'

	def test():
		local("jekyll serve --watch")

	def prep():
	    local("git add -p && git commit")
	    local("git push")

	def deploy():
		local("jekyll build")
		local("scp -r _site jasonrhaas.com:~")