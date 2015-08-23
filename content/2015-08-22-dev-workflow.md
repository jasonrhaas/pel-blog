---
layout: post
title: Development workflow
Slug: development-workflow
category: software development
tags: git, vagrant, ansible, jira, virtualbox
---


There are many different ways to manage your git workflow, and a lot depends on the size of the team and how the team works together.  For simplicity I'm going to break it down into 3 different types of Git workflow that I have seen:


#### Everyone pushes to central branch (master)
is by far the simplest, but it makes it difficult to track new features coming into the software and can also be chaotic when working with teams.
#### Feature branch workflow
is great for small teams that don't have the need for supporting a lot of production level code hot fixes.
#### Gitflow branch workflow
is best for larger team that have developers working on new features, hot fixes, and supporting production code releases

## Feature branch workflow

For this post, I am going to focus on the **Feature branch workflow**.  I like this workflow because it allows great integration with **Pull requests** and **JIRA**.  I'm using JIRA as an example, but it could be adapted to any issue tracking software.  I mention this because **Pull requests** and **JIRA** are a nice and convenient way to keep other team members in the loop about the new features you are working on.  At any time, it is very easy to go back and reference a pull request or JIRA ticket solicit feedback on a new feature you worked on.

### Prereq's

And now on to the most important part of any guide, the examples.  I am going to walk through a new feature from start to finish, using JIRA, Git, and Pull requests.

Before we get started, this relies on having your Github account synced to your JIRA account.  For this to happen, the accounts need to be linked (see JIRA blog post above), and the email address associated with your Github repo needs to match your JIRA email address.  In Git, you can set up a default username and email address and also set specific usernames and email address for each repo.  You might want your default to be your @gmail.com address and your work related repos to be @company.com

To set up your repo (example directories and values):

```
cd ~/repos/pig
git config user.name "Porky"
git config user.email "Porky@company.com"
```

Also another thing you'll want to do to get colored output:

`git config --global color.ui auto`

I have many more git and cli type tricks but that is for another post.

### Example task, PIG-101

Someone comes to you and says, we need to support a new type of website for our scraping architecture.  Here is the high level step breakdown:

####  1. Create JIRA ticket, PIG-101. 

It is important that the prefix, in this case "PIG" matches up with the prefix of your JIRA project.  This will allow JIRA to see your Git branch that you are about to create.  In the issue be sure to identify any requirements.  I am a fan of bulleted lists for this.  For example.  

- scraper must accept .onion address
- scraper must route all tor traffic through a proxy server
- scraper must not download tor images
    
**General Guideline**.  I like to have JIRA issues be "small" amounts of manageable work.  If you are doing Agile development you may be using **Scrum** or **Kanban**, or some home-grown version of either.  In Scrum, each item gets points for how long you think it will take.  Kanban is more flexible and is time-driven vs. difficulty driven.  Even in the case of Scrum, I  recommend keeping JIRA tasks small.  There are many reasons for this, I'll name a few.

- Gets new features deployed as quickly as possible
- Works in a fast changing and evolving climate
- Increasing rate that pull requests are being generated allowing for more input and collaboration
- Like a book with short chapters, churning through JIRA tasks quickly just feels good!

##### What is a small amount of work?

**A well written JIRA task takes 1-3 days.**  If you have tasks over for longer than 3 days, you should break up the task into different pieces.  The longer you keep your work in feature branches the longer the code is not being deployed.  **Fail fast, fail early.** 


#### 2. Create new feature branch, PIG-101

It is best to branch off of a **develop** branch so that the **master** branch is left alone since the **master** branch is often the production branch.  For really small teams and for code that is not in production yet, it's OK to branch off of master.  For this example, I'll branch off of **master**.

```
cd ~/repos/pig
git checkout master
git checkout -b PIG-101
```

The `git checkout -b` creates a new branch with the name `PIG-101` and immediately switches to that branch.  From here on, all of your work for issue **PIG-101** will occur here.  If you navigate to the task in JIRA, you will see that the branch is now linked to the JIRA task.

#### 3. Write code

When it comes to committing code, **commit early, commit often.** Do not be concerned about committing broken code right now.  At this point in the development process, you should be concerned about having lots of save points so you can easily revert changes in a piecemeal way if you so desire.  In general, I try to make a commit whenever I add any functional piece of code.  In `Python`, it could be a function or a class.  In `Ansible`, it might be a playbook or a configuration file.  If  I have a test environment available (more about that next), I may run the code first to see if I made any mistakes or typos.

```
git add tor.yml
git commit -m "add playbook for tor role"
git push -u origin PIG-101
```
The commands above add a file to the git index, commit it, and push a *new* branch up to the remote repository.  After the first time, you can simply do `git push`.  Now if you go to Github or JIRA you will see the new branch and any commits associated with the feature.

#### 4. Test code

If possible, test your code on a local virtual machine.  My testing setup involves using **VirtualBox** and **Vagrant**.  It's easy to set this up, just download [VirtualBox](https://www.virtualbox.org/) and [Vagrant](https://www.vagrantup.com/).  For this example, I'm going to configure 3 CentOS 6.5 machines to mirror my production cluster.  Here is the commands I run.  For the Ubuntu fans, the box for 14.04 is called `ubuntu/trusty64`.

```
mkdir -p ~/vagrant_pig
cd !$
vagrant init chef/centos-6.5
```

This creates a `Vagrantfile` that must be edited to configure it for our needs.  Here is the one I created for this 3 node cluster:

```
VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|

  config.ssh.forward_agent = true

  config.vm.define "pig2", primary: true do |pig2|
    pig2.vm.box = "chef/centos-6.5"
    pig2.vm.hostname = "pig2"
    pig2.vm.network "private_network", ip: "192.168.33.10"
    pig2.vm.provision :shell, path: "keys.sh"
  end

  config.vm.define "pig3", primary: true do |pig3|
    pig3.vm.box = "chef/centos-6.5"
    pig3.vm.hostname = "pig3"
    pig3.vm.network "private_network", ip: "192.168.33.11"
    pig3.vm.provision :shell, path: "keys.sh"
  end

  config.vm.define "pig4", primary: true do |pig4|
    pig4.vm.box = "chef/centos-6.5"
    pig4.vm.hostname = "pig4"
    pig4.vm.network "private_network", ip: "192.168.33.12"
    pig4.vm.provision :shell, path: "keys.sh"
  end
end
```

For the veteran hackers, you may have noticed that the syntax looks like Ruby (it is).  You may have also noticed that there is an additional shell script in there that I didn't talk about.  `keys.sh` is just a simple command that copies over my public ssh key so that I can ssh into the machine as user `vagrant`.  This is especially handy when provisioning with `Ansible`, since it needs to be able to ssh into the box to work**.

** Vagrant can also be configured to provision with Ansible during VM boot up.

After you save the `Vagrantfile`, do `vagrant up`, and it will boot all three VM's automatically.  By default, Vagrant shares the folder `vagrant_pig` with the VM, so you can access your code from there inside the VM

##### Ansible example

If you wish to provision the VM with Ansible, here's one way you could do it.

`ansible-playbook -i my.test tor.yml -u vagrant`

Where the `my.test` file has your server inventory and `vagrant` is the user to connect to the VM's with.

#### 5. Submit Pull Request

After you are happy with the new feature and having tested it, time to merge it to the main branch.  You could do a `git checkout master` and then `git merge PIG-101` but that wouldn't create a Pull Request.  So I do my actual merges on Github.  

*Note:  if there is a merge conflict you will have to resolve via the command line (or whatever other tool you use)*.

To submit a pull request:

1.  Go to the repo main page on Github.
2.  Select `PIG-101` from the drop down.
3.  Click the green button to left the branch.
4.  You will then see a page `Comparing Changes`.  Make sure your that your branch is on the right and the branch to merge into, in this case **master**, is on the left.
5.  Once you have looked at the commits and are happy, click `Create pull request`.
6.  Add a short feature description in the comments section and click `Submit pull request.`
7.  Await for feedback from co-workers to review code or simply `Merge` it in yourself.
8.  Delete branch.  After the branch has been merged, there is no need to keep it around, all the commits are now in the **master** branch.

#### 6. Update JIRA task

If you navigate to the JIRA issue, `PIG-101`, you should see the corresponding `Pull request` and `merge` in Github.  At this point you can add a short comment saying you have merged the new feature, or simply move the task to `Done`.


## Development resources

#### Git
- [Simple Git Guide](http://rogerdudler.github.io/git-guide/)
- [Feature Branch Workflow](https://www.atlassian.com/git/tutorials/comparing-workflows/feature-branch-workflow)
- [Gitflow Branching Model](http://nvie.com/posts/a-successful-git-branching-mod    el/)
- [Hitchhiker's guide to Python](http://docs.python-guide.org/en/latest/)
- [Advanced Git Guide](https://sethrobertson.github.io/GitBestPractices/)

#### Kanban
- [Brief Kanban Intro](http://kanbanblog.com/explained/)
- [More Kanban info](http://www.everydaykanban.com/what-is-kanban/)
- [JIRA specific Kanban](https://www.atlassian.com/agile/kanban)

#### JIRA
- [Linking JIRA and Github](http://blogs.atlassian.com/2014/04/connecting-jira-6-2-github/)