Title: Automate all the things with Ansible, Vagrant, and Travis CI
Slug: automate-all-the-things-with-ansible-and-travis-ci
Date: 2016-01-24 19:23:51
Tags: ansible, travis, vagrant, integration, CI, infrastructure, automation, big data, zookeeper, kafka, spark, elasticsearch
Category: automation
Author: Jason Haas
Summary:  Cloud computing has allowed us to no longer be tied to physical machines or be stuck with an architecture that is out of date as soon as it is built.  Now, servers and processes are dynamic.  In this blog post, I'll talk about "infrastructure as code" using Ansible, Vagrant, and Travis CI.
Status: draft

# Infrastructure as code

Building a computing infrastructure for your applications and big data stack is time consuming.  Not only is it time consuming, but it's very hard to plan for.  Your needs today will likely not be your needs a year from now.  This is especially the case if you are a growing technology company staying on the edge of the latest developments in the big data world.  We all try to plan and think ahead for future needs, but this is often less than perfect.   

In the past, system administrators and engineers typically built up their servers using a combination of techniques.  Quite often this would involve customizing a particular server or image and then "cloning" it over to other servers.  But this only works if the software on each needs to be the same.  So inevitably there ends up being some kind of custom bash script or post install script to customize the build on a server by server basis.  I've seen some pretty fancy bash and perl scripts used, and while very powerful they become a nightmare to maintain.

# Ansible

Server provisioning software attempts to solve the code maintainability problem by introducing a framework and standards to manage your infrastructure.  Some popular frameworks include Chef, Puppet, and Ansible.  They all are a great way to manage your infrastructure, but Ansible stands out because it is agent-less and only requires `ssh` to provision your server.  Also -- it is written in Python, which I also like due to Python's readability and hackability.  Here are some of the key reasons you should use Ansible.

## Dynamic inventories and group_vars

Ansible uses an **inventory** file to figure out where your servers are and what they are called.  It also has server "groups", so you can logically set up your servers into groups.  For a big data stack this might be `zookeeper-nodes`, `kafka-nodes`, `spark-worker-nodes`, etc.  These groups are very powerful because they allow you to scale up or down your infrastructure simply by editing the inventory file.  Want to add more resources to your Spark cluster, just add it to the inventory and re-run the Ansible playbook.

In an ansible playbook, the spark-worker-nodes group can be accessed by using the `{{ groups['spark-worker-nodes'] }}`.  You can also access individual elements of the list by adding an index, like `{{ groups['spark-worker-nodes'][0] }}`.

## Roles

Ansible roles are standalone tasks that are meant to be performed for a single piece of infrastructure.  Typical roles in a big data stack might be **elasticsearch**, **zookeeper**, **kafka**, **storm**, **spark**, etc.  All of these roles should be able to run _independently_.  This concept is very powerful because you now can design your Ansible playbooks to accommodate almost any number of servers and configurations.  A good practice to follow is to have the following folders under each role:

- defaults
- handlers
- meta
- tasks
- templates
- vars

If you don't have a need for one of these folders, you don't necessarily need to create it (git won't even track it if there aren't any files in it).  Underneath each folder you should have a **main.yml** file.  Why call it that?  Because ansible looks for a **main.yml** automatically.  You don't have to put all your code in **main.yml**.  If you wish to break it up into logical parts (such as Debian and RedHat plays), you can `include` them inside your **main.yml** file.

Description of different folders:

### Defaults

All the default variable settings for a specific role.  These settings have the _lowest_ priority of all variables.  They are, well, defaults, and can be overwritten by re-defining the variable literally any other place in the Ansible code, and also on the command line using the `--extra-vars` flag.  The most common way to override these defaults is with **group_vars**, which I will discuss later on.

### Handlers

Handlers are handy for doing things like restarting a process when a file changes.  Just define your handlers in the **main.yml** and then use them in your main playbook under the **tasks** folder.  For example, here is a simple handler to restart zookeeper (running under supervisord):

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

TODO

### Templates

TODO

### Vars

TODO

## Creating your site playbook

I prefer keep my Ansible code simple and manage as few .yml files as possible.  To do this, I like to have all of my roles and plays in one or maybe two top level playbooks.  Just pick and choose which roles you want and put it all in a **site-infrastructure.yml**, being sure to `tag` every play appropriately.  Note that as of this writing, Ansible 2.0 reads tags dynamically, so if you want to use tags to control how plays get run (I highly recommend this), you need to put them at your top level playbook otherwise Ansible will iterate through every single play in your code looking for your `--tag` that you wanted to run.

## Using --tags and --limit

When you want to run your top level playbook, you can choose to run everything like this, `ansible-playbook -i production site-inventory.yml` or limit which plays get run by using the `--tags` or `--limit` flags on the command line.  For example, `ansible-playbook -i production site-inventory.yml --limit aws` or `ansible-playbook -i production site-inventory.yml --tags site-kafka`.

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

# Don't break the build

![Alt Text]({filename}/images/brokebuild.jpg)

Since Ansible is a provisioning tool, you need an operating system to test on.  Evidently with Ansible you end up with a lot of little bugs to sort all while testing your code.  [This](http://devopsreactions.tumblr.com/post/135373866575/bug-fixed-should-be-ok-now-no-wait) tends to happen a lot when using Ansible.  So -- how to sort through all those bugs?  Well you don't want to be changing your local machine or any production machines without feeling the wrath of your local sysadmin.  Vagrant to the rescue!

# Vagrant

Vagrant is a scripting language that allows you to manage different configurations for as many virtual machines as you need.  It supports Virtualbox and VMWare out of the box.  I personally use Vagrant + Virtualbox because its free and works really well.  As of Vagrant 1.8+, they now support VM snapshots, which is very nice for testing different setups and environments.  I'll walk through a simple Vagrant setup with two independent VMs, although this scales to create any number of VM's that you wish.

## Vagrantfile

The script file that tells Vagrant which VM's to setup and how to provision them is the **Vagrantfile**.  The file is written in Ruby so it is programmable and is there to do your bidding.  For scalable VM testing, I chose to have the Vagrantfile actually read from a **vagrant_hosts** and parse it to figure out the VM name, IP, and type.  For example, the **vagrant_host** file may look like:

    :::
    127.0.0.1        localhost
    192.168.33.101   vagrant-as-01  vas01  ubuntu
    192.168.33.102   vagrant-as-02  vas02  ubuntu

Another thing I do in my Vagrantfile is overwrite the **/etc/hosts** file with my **vagrant_hosts** file so that the VM's know how to talk to each other on the network.  Lastly, I copy over my ssh public key so that I can ssh into the VM's using `ssh vagrant@vagrant-as-01`.  Normally if you are just testing VM's without provisioning with Ansible you could use the `vagrant ssh` command which uses a built in private key that comes with Vagrant.  However, to use Ansible via your local console to provision Vagrant, you need to be able to `ssh` in, ideally without a password.  These actions are accomplished by doing:

    :::ruby
    # Configuration applying to all VMs
    config.vm.provision :shell, inline: "cat /vagrant/vagrant_hosts > /etc/hosts"
    config.vm.provision :shell, inline: "cat /vagrant/id_rsa.pub >> /home/vagrant/.ssh/authorized_keys"

Note the comment that says these actions will be applied to all VM's.  If you want to do something to an individual VM, you have to break it out in another ruby loop:

    :::ruby
    # Set up IP addresses and hostnames from 'hosts' file
    # It assumes 'localhost' is on the first line
    hosts = File.readlines('vagrant_hosts')
    hosts[1..-1].each do |h|
      unless /(#|^\s*$)/.match(h)   # ignore commented out hosts and blank lines
        config.vm.define h.split(%r{\s+})[1] do |node|
          if h.split(%r{\s+})[-1] == 'centos'
            node.vm.box = CENTOS_BOX
          elsif h.split(%r{\s+})[-1] == 'ubuntu'
            node.vm.box = UBUNTU_BOX
            node.ssh.shell = "bash -c 'BASH_ENV=/etc/profile exec bash'"
          end
          node.vm.hostname = h.split(%r{\s+})[1]
          node.vm.network "private_network", ip: h.split(%r{\s+})[0]
          node.vm.provision "shell", inline: "service supervisord restart || true", run: "always"
        end
      end
    end

To clarify a few spots in the code snippet above, `hosts[1..-1].each do |h|` sets up `.each` loop that iterates from index 1 (not 0 since that is localhost) to the end of the file.  To find out what type of VM it is, it parses the line looking for "centos" or "ubuntu".  The line `node.ssh.shell = "bash -c 'BASH_ENV=/etc/profile exec bash'"` is a special trick I discovered to resove the infamous [stdin is not a tty](https://github.com/mitchellh/vagrant/issues/1673) Vagrant bug when provisioning Ubuntu VMs.

This line `node.vm.provision "shell", inline: "service supervisord restart || true", run: "always"` is a workaround that I'm doing to restart the **supervisord** process upon VM booting.  I like to use supervisord to manage all my running applications since its a nice central place to check status on all the custom software or applications I've installed.

## Testing Ansible with Vagrant

After you run `vagrant up` your VM's should be pretty much good to go.  You may want to also add the IP addresses and hostnames in your **vagrant_hosts** file so you can access them via hostname rather than IP address.  Make sure you can ssh into the machines as **vagrant** user and you are ready to start provisioning with Ansible!

When you run your Ansible code, be sure to run it like `ansible-playbook -i inventory playbook.yml -u vagrant` since by default Ansible will try to connect using your current username which does not exist on the Vagrant VM.

## Automated Builds with Travis CI

Making a change to code and manually running tests gets old really fast.  Not to mention it's subject to human error.  Automating the test process not only speeds up development in the long run, but will catch errors quickly and reliably (assuming your tests are good).  This practice of "continuous integration" or "continuous delivery" can also be applied to the "infrastructure as code" approach.

The first thing to do is to run a `--syntax-check` on your code.  This catches any trivial errors and will cause your build to fail very fast so you can fix the bug quickly.  Next, you can actually provision the VM that Travis gives you to test with.  Lastly, you can run some high levels tests on your tools to make sure they are actually working as they should.

- For Elastic Search, index a small document
- For Kafka, write something to a topic
- For Hadoop, make a file or run a map reduce job
- For Hbase, write something to the database

You get the idea.
