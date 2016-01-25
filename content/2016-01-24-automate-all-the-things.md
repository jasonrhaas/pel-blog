Title: Automate all the things with Ansible, Vagrant, and Travis CI
Slug: automate-all-the-things-with-ansible-and-travis-ci
Date: 2016-01-24 19:23:51
Tags: ansible, travis, vagrant, integration, CI, infrastructure, automation, big data
Category: automation
Author: Jason Haas
Summary:  Cloud computing has allowed us to no longer be tied to physical machines or be stuck with an architecture that is out of date as soon as it is built.  Now, servers and processes are dynamic.  In this blog post, I'll talk about "infrastructure as code" using Ansible and automated testing with Travis CI.
Status: published

# Infrastructure as code

Building a computing infrastructure for your applications and big data stack is time consuming.  Not only is it time consuming, but it's very hard to plan for.  Your needs today will likely not be your needs a year from now.  This is especially the case if you are a growing technology company staying on the edge of the latest develops in the big data world.  We all try to plan and think ahead for future needs, but this is often less than perfect.   

In the past, system administrators and engineers typically built up their servers using a combination of techniques.  Quite often this might involve customizing a particular server or image and then "cloning" it over to other servers.  But this only works if the software on each needs to be the same.  So inevitably there ends up being some kind of custom bash script or post install scripts to customize the build to a specific server.  I've seen some pretty fancy bash and perl scripts used, and while very powerful they become a nightmare to maintain.

# Ansible

Server provisioning software attempts to solve the code maintainability problem by introducing a framework and standards to manage your infrastructure.  Some popular frameworks include Chef, Puppet, and Ansible.  They all are a great way to manage your infrastructure, but Ansible stands out because it is agent-less and only requires `ssh` to provision your server.  Also -- it is written in Python, which I also like due to Python's readability and hackability.  Here are some of the key reasons you should use Ansible.

## Dynamic inventories and group_vars

Ansible uses an **inventory** file to figure out where your servers are and what they are called.  It also has server "groups", so you can logically set up your servers into groups.  For a big data stack this might be `zookeeper-nodes`, `kafka-nodes`, `spark-worker-nodes`, etc.  These groups are very powerful because they allow you to scale up or down your infrastructure simply by editing the inventory file.  Want to add more resources to your Spark cluster, just add it to the inventory and re-run the Ansible play.

In an ansible playbook, the spark-worker-nodes group can be accessed by using the `{{ groups['spark-worker-nodes'] }}`.  You can also access individual elements of the list by adding an index, like `{{ groups['spark-worker-nodes'][0] }}`.

## Roles

Ansible roles are standalone tasks that are meant to be performed for a single piece of infrastructure.  Typical roles in a big data stack might be **elasticsearch**, **zookeeper**, **kafka**, **storm**, **spark**, etc.  All of these roles should be able to run _independently_.  This concept is super powerful because you now can design your Ansible playbooks to accomodate almost any number of servers and configurations.  A good practice to follow is to have the following folder under each role:

- defaults
- handlers
- meta
- tasks
- templates
- vars

If you don't have a need for one of these folders, you don't necessarily need to create it (git won't even track it if there aren't any files in it).  Underneath each folder you should have a **main.yml** file.  Why call it that?  Because ansible looks for a **main.yml**.  You don't have to put all your code in **main.yml**.  If you wish to break it up into logical part (such as Debian and RedHat plays), you can `include` them inside your **main.yml** file.

Description of different folders:

### Defaults

All the default variable settings for a specific role.  These settings have the _lowest_ priority of all variables.  They are, well, defaults, and can be overwritten by re-defining the variable literally any other place in the Ansible code, and also on the command line using the `--extra-vars` flag.  The most common way to override these defaults are with **group_vars**, which I will discuss later on.

### Handlers

Handlers are handy for doing things like restarting a process when a file changes.  Just define your handlers in the **main.yml** and then use them in your main playbook under the **tasks** folder.  For example, here a simple handler to restart zookeeper (running under supervisord):

    :::yaml
    - name: restart zookeeper
      supervisorctl:
        name=zookeeper
        state=restarted

In your tasks playbooks, this handle can be used by adding a `notify: restart zookeeper` in one of the plays.  For example,

    :::yaml
    - name: setup zoo.cfg
      template: 
        dest={{ zookeeper_conf_dir }}/zoo.cfg
        src=zoo.cfg.j2
      notify:
        - restart zookeeper
        - wait for zookeeper port
      tags: zookeeper

### Meta

The meta folder is meant to handle any dependencies that your role has.  For example, zookeeper requires Java and in our installation, supervisord for managing the process.  So the meta file looks like this:

    :::yaml
    ---
    dependencies:
      - { role: supervisord, when: "supervisord_has_run is not defined" }
      - { role: java, when: "java_has_run is not defined" }

Note that the `when: "java_has_run is not defined"` part is a sneaky trick that I'm using so that Ansible does not keep re-running the same role on a specific server if it as already been run.  At the end of the Java role, I create an "Ansible fact" called `java_has_run` and set it to `true`.  If that fact exists on the specific server, Java will not be run again on that machine.  At the end of the Java role, I have this play:

    :::yaml
    - name: Set fact java_has_run
      set_fact:
        java_has_run: true

### Tasks 

### Templates

### Vars

## Creating your site playbook

I prefer keep my Ansible code simple and manage as few .yml files as possible.  To do this, I prefer to have all of my roles and plays in one or maybe two top level playbooks.  Just pick and choose which roles you want and put it all in a **site-infrastructure.yml**, being sure to `tag` every play appropriately.  Note that as of this writing, Ansible 2.0 reads tags dynamically, so if you want to use tags to control how plays get run (I highly recommend this), you need to put them at your top level playbook otherwise Ansible will iterate through every single play in your code looking for your `--tag` that you wanted to run.

## Using --tags and --limit

When you want to run your top level playbook, you can choose to run everything like this, `ansible-playbook -i production site-inventory.yml` or limit which plays get run by using the `tags` or `--limit` flags on the command line.  For example, `ansible-playbook -i production site-inventory.yml --limit aws` or `ansible-playbook -i production site-inventory.yml --tags site-kafka`.

Remember that each play can have multiple tags.  This allows you to pair things logically together.  You might want to always run the zookeeper role when you run kafka, since kafka relies on zookeeper.  In that case you might have:

    :::yaml
    - name: Run zookeeper role
      hosts: zookeeper-nodes
      vars:
       - zookeeper_host_list: "{{ groups['zookeeper-nodes'] }}"
      roles: [ zookeeper ]
      tags:
        - site-zookeeper
        - deps-kafka

    - name: Run kafka role
      hosts: kafka-nodes
      vars:
       - kafka_host_list: "{{ groups['kafka-nodes'] }}"
       - zookeeper_host_list: "{{ groups['zookeeper-nodes'] }}"
      roles: [ kafka ]
      tags:
        - site-kafka
        - deps-kafka

This way if you run `ansible-playbook -i production site-inventory.yml --tags deps-kafka` it will run both zookeeper and kafka.
