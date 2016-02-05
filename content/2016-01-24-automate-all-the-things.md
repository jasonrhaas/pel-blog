Title: Automate with Ansible, Vagrant, and Travis CI
Slug: automate-with-ansible-and-travis-ci
Date: 2016-01-24 19:23:51
Tags: ansible, travis, vagrant, integration, CI, infrastructure, automation, big data, zookeeper, kafka, spark, elasticsearch
Category: automation
Author: Jason Haas
Summary:  Cloud computing has allowed us to no longer be tied to physical machines or be stuck with an architecture that is out of date as soon as it is built.  Now, servers and processes are dynamic.  In this blog post, I'll talk about "infrastructure as code" using Ansible, Vagrant, and Travis CI.
Status: published

# Infrastructure as code

Building a computing infrastructure for your applications and big data stack is time consuming.  Not only is it time consuming, but it's very hard to plan for.  Your needs today will likely not be your needs a year from now.  This is especially the case if you are a growing technology company staying on the edge of the latest developments in the big data world.  We all try to plan and think ahead for future needs, but this is often less than perfect.

In the past, system administrators and engineers typically built up their servers using a combination of techniques.  Quite often this would involve customizing a particular server or image and then "cloning" it over to other servers.  But this only works if the software on each needs to be the same.  So inevitably there ends up being some kind of custom bash script or post install script to customize the build on a server by server basis.  I've seen some pretty fancy bash and perl scripts used, and while very powerful they become a nightmare to maintain.

# Ansible

Server provisioning software attempts to solve the code maintainability problem by introducing a framework and standards to manage your infrastructure.  Some popular frameworks include Chef, Puppet, and Ansible.  They all are a great way to manage your infrastructure, but Ansible stands out because it is agent-less and only requires `ssh` to provision your server.  Also -- it is written in Python, which I also like due to Python's readability and hackability.

## Dynamic inventories and group_vars

Ansible uses an **inventory** file to figure out where your servers are and what they are called.  It also has server "groups", so you can logically group your servers together.  For a big data stack this might be `zookeeper-nodes`, `kafka-nodes`, `spark-worker-nodes`, etc.  These groups are very powerful because they allow you to scale up or down your infrastructure simply by editing the inventory file.  Want to add more resources to your Spark cluster? Just add it to the inventory and re-run the Ansible playbook.

In an ansible playbook, the spark-worker-nodes group can be accessed by using the `{{ groups['spark-worker-nodes'] }}`.  You can also access individual elements of the list by adding an index, like `{{ groups['spark-worker-nodes'][0] }}`.

## Roles

Ansible roles are standalone tasks that are meant to be performed for a single piece of infrastructure.  Role names typically match up to server groups, but they don't have to.  All of these roles should be able to run _independently_.  This concept is very powerful because you now can design your Ansible playbooks to accommodate almost any number of servers and configurations.  A good practice to follow is to have the following folders under each role:

- defaults
- handlers
- meta
- tasks
- templates
- vars

If you don't have a need for one of these folders, you don't necessarily need to create it (git won't even track it if there aren't any files in it).  Underneath each folder you should have a **main.yml** file.  Why call it that?  Because ansible looks for it automatically.  You don't have to put all your code in **main.yml**.  If you wish to break it up into logical parts (such as Debian and RedHat plays), you can `include:` them inside your **main.yml** file.

### Defaults

Defaults are the default variable settings for a specific role.  These settings have the _lowest_ priority of all variables.  They are, well, defaults, and can be overwritten by re-defining the variable literally any other place in the Ansible code, and also on the command line using the `--extra-vars` flag.  The most common way to override these defaults is with **group_vars**, which I will discuss later on.  An example settings that might be in a **defaults/main.yml** file:

    ::yaml
    zookeeper_version: 3.4.6
    zookeeper_client_port: 2181
    zookeeper_install_dir: /opt/zookeeper
    zookeeper_base_dir: "{{ zookeeper_install_dir }}/default"
    zookeeper_conf_dir: "{{ zookeeper_base_dir }}/conf"
    zookeeper_data_dir: "{{ zookeeper_base_dir }}/data"
    zookeeper_log_dir: "{{ zookeeper_base_dir }}/logs"

Things like version numbers, port numbers, install directories are nice to put in the defaults section.

### Handlers

Handlers are handy for doing things like restarting a process when a file changes.  Just define your handlers in the **main.yml** and then use them in your main playbook under the **tasks** folder.  For example, here is a simple handler to restart zookeeper (running under supervisord):

    ::yaml
    - name: restart zookeeper
      supervisorctl:
        name=zookeeper
        state=restarted

In your tasks playbooks, this handler can be used by adding a `notify: restart zookeeper` in one of the plays.  For example,

    ::yaml
    - name: setup zoo.cfg
      template: 
        dest={{ zookeeper_conf_dir }}/zoo.cfg
        src=zoo.cfg.j2
      notify:
        - restart zookeeper
      tags: zookeeper

### Meta

The meta folder is meant to handle any dependencies that your role has.  For example, zookeeper requires Java and in our installation and  supervisord for managing the process.  So the meta file looks like this:

    ::yaml
    ---
    dependencies:
      - { role: supervisord, when: "supervisord_has_run is not defined" }
      - { role: java, when: "java_has_run is not defined" }

Note that the `when: "java_has_run is not defined"` part is a sneaky trick that I'm using so that Ansible does not keep re-running the same role on a specific server if it as already been run.  At the end of the Java role, I create an "Ansible fact" called `java_has_run` and set it to `true`.  If that fact exists on the specific server, Java will not be run again on that machine.  At the end of the Java role, I have this play:

    ::yaml
    - name: Set fact java_has_run
      set_fact:
        java_has_run: true

### Tasks 

The tasks folder is where the actual procedure to install your software lives.  Your **tasks/main.yml** file is where you can utilize any of the Ansible [modules](http://docs.ansible.com/ansible/modules_by_category.html) and take advantage of all your variables, whether those are defined in **defaults**, **group_vars**, the **inventory**, or the command line.  Here is a partial snippet of a zookeeper **tasks/main.yml** file:

		::yaml

    - name: create zookeeper install directory
      file:
        path={{ item }}
        state=directory
        mode=0744
      with_items:
        - "{{ zookeeper_install_dir }}"
      tags: zookeeper

    - name: check for existing install
      stat: path={{ zookeeper_install_dir }}/zookeeper-{{ zookeeper_version }}
      register: zookeeper
      tags: zookeeper

    - name: download zookeeper
      get_url:
        url="{{ repository_infrastructure }}/zookeeper-{{ zookeeper_version }}.tar.gz"
        dest=/tmp/zookeeper-{{ zookeeper_version }}.tgz
        mode=0644
        validate_certs=no
      when: zookeeper.stat.isdir is not defined
      tags: zookeeper

    - name: extract zookeeper
      unarchive:
        src=/tmp/zookeeper-{{ zookeeper_version }}.tgz
        dest={{ zookeeper_install_dir }}
        copy=no
      when: zookeeper.stat.isdir is not defined
      tags: zookeeper

Anything surrounded by `{{ }}` is an Ansible variable.  That variable can be defined a number of ways.  The first place it's seen is the `{{ item }}` variable.  This is an Ansible special(?) variable that is used for doing "for" loops.  In the case of the "create zookeeper install directory" above, it really not neccessary since there is only one folder created.  However, if I wanted to add more I could just tack on more items in the `with_items` yaml list like this:

    ::yaml
    with_items:
      - "{{ zookeeper_install_dir }}"
      - "{{ some_other_dir }}"

The other Ansible trick that is used in the tasks above is the ``when:`` conditional.  In Ansible you can run plays only when the ``when:`` conditional meets some criteria.  In the case above, the "download zookeeper" task is only run `when: zookeeper.stat.isdir is not defined`.  The `zookeeper` variable is defined in the previous task and checks whether a directory already exists.  Some other common ways to use the `when:` clause are:

- Running on different OS's (Debian vs. Redhat)
- Only run when a variable is `true`
- Only run when a variable is `defined`

Example of running specific Debian or Redhat plays:

    ::yaml
    - include: setup-RedHat.yml
      when: ansible_os_family == 'RedHat'

    - include: setup-Debian.yml
      when: ansible_os_family == 'Debian'

In this case, there are separate playbooks for Debian and Redhat, and each one is only run on the appropriate OS.  The same thing can be used for OS specific variables:

    ::yaml
    - name: Include OS-specific variables.
      include_vars: "{{ ansible_os_family }}.yml"

### Templates

Templates are files that typically end in a **.j2** extension and are used when you have a file that may need to change based on some variables you have defined in the Ansible code base.  Templates are very handy to manage configuration settings for Linux software since almost all tools that run on Linux have some sort of configuration text file that can be customized.  Here is a snippet from a Kafka **server.properties.j2** template file:

    ::text
    {% for host in kafka_host_list %}
    {%- if host == inventory_hostname -%}broker.id={{ loop.index }}{%- endif -%}
    {% endfor %}

    message.max.bytes={{ kafka_message_max }}
    replica.fetch.max.bytes={{ kafka_replica_fetch_max_bytes }}
    port={{ kafka_port }}
    host.name={{ inventory_hostname }}
    advertised.host.name={{ inventory_hostname }}
    advertised.port={{ kafka_port }}

Notice the `{{ }}` variables that are used in the template file.  There are a few "special" variables in here that deserve special attention.  `inventory_hostname` is a reserved Ansible variable that maps to the hostname defined in the Ansible inventory file.  It will match whatever host Ansible is currently running on.

The first chunk of code above is a fancy for loop that iterates through all elements of the `kafka_host_list` variable and sets the `broker_id` Kafka setting equal to the index of the host.  Also note that the `kafka_host_list` variable has to be defined somewhere.  In the case of this code it is defined at the playbook like and is:

    ::text
    kafka_host_list: "{{ groups['kafka-nodes'] }}"

The `groups['kafka-nodes']` list is another special Ansible variable that is used to grab all of the hosts in the **kafka-nodes** group inside the inventory file.  So your inventory for Kafka might look like this:

    ::text
    [kafka-nodes]
    prod-as-01
    prod-as-02
    prod-as-03

In this case `groups['kafka-nodes']` would contain all of those hostnames.  You can access each one individually by using an index number, like this: `groups['kafka-nodes'][0]`.

Back to the for loop above, that code would set the **prod-as-01** host to `broker.id=1`, **prod-as-02** host to `broker.id=2`, and **prod-as-03** to `broker.id=3`.

The rest of the Kafka template code above is simply using Ansible variables defined mostly in the **defaults/main.yml** file populate the fields.

### Vars

Variables are used everywhere in Ansible.  For me, it's actually the most confusing part about using Ansible at first.  Here are (most of) the places variables can be set:

- role defaults
- role vars
- playbook role vars
- inventory vars
- host_vars
- group_vars
- command line vars

The Ansible documentation has some good examples of how, when, and where to use variables, but I still think it is a bit confusing for someone new to Ansible.

General guidelines for using variables:

- Role defaults are lowest precedence
- Role defaults are "meant" to be overridden
- group_vars for site specific variables, API keys, accounts
- host_vars for host specific variables 
- `--extra-vars` for command line one-off playbook runs


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

This way if you run `ansible-playbook -i production site-infrastructure.yml --tags deps-kafka` it will run both zookeeper and kafka.

# Don't break the build

![Alt Text]({filename}/images/brokebuild.jpg)

Since Ansible is a provisioning tool, you need an operating system to test on.  Inevitably with Ansible you end up with a lot of little bugs to sort all while testing your code.  [This](http://devopsreactions.tumblr.com/post/135373866575/bug-fixed-should-be-ok-now-no-wait) tends to happen a lot when using Ansible.  So -- how to sort through all those bugs?  Well you don't want to be changing your local machine or any production machines without feeling the wrath of your local sysadmin.  Vagrant to the rescue!

# Vagrant

Vagrant is a VM scripting tool that allows you to manage different configurations for as many virtual machines as you need.  It supports Virtualbox and VMWare out of the box.  I personally use Vagrant + Virtualbox because its free and works really well.  As of Vagrant 1.8+, they now support VM snapshots, which is very nice for testing different setups and environments.  I'll walk through a simple Vagrant setup with two independent VMs, although this scales to create any number of VM's that you wish.

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

To clarify a few spots in the code snippet above, `hosts[1..-1].each do |h|` sets up `.each` loop that iterates from index 1 (not 0 since that is localhost) to the end of the file.  To find out what type of VM it is, it parses the line looking for "centos" or "ubuntu".  The line `node.ssh.shell = "bash -c 'BASH_ENV=/etc/profile exec bash'"` is a special trick I discovered to resolve the infamous [stdin is not a tty](https://github.com/mitchellh/vagrant/issues/1673) Vagrant bug when provisioning Ubuntu VMs.

This line `node.vm.provision "shell", inline: "service supervisord restart || true", run: "always"` is a workaround that I'm doing to restart the **supervisord** process upon VM booting.  I like to use supervisord to manage all my running applications since its a nice central place to check status on all the custom software or applications I've installed.

## Testing Ansible with Vagrant

After you run `vagrant up` your VM's should be pretty much good to go.  You may want to also add the IP addresses and hostnames in your **vagrant_hosts** file so you can access them via hostname rather than IP address.  Make sure you can ssh into the machines as **vagrant** user and you are ready to start provisioning with Ansible!

When you run your Ansible code, be sure to run it like `ansible-playbook -i inventory site-infrastructure.yml -u vagrant` since by default Ansible will try to connect using your current username which does not exist on the Vagrant VM.

## Automated Builds with Travis CI

![Alt Text]({filename}/images/travis.png)

Making a change to code and manually running tests gets old really fast.  Not to mention it's subject to human error.  Automating the test process not only speeds up development in the long run, but will catch errors quickly and reliably (assuming your tests are good).  This practice of "continuous integration" or "continuous delivery" can also be applied to the "infrastructure as code" approach.

The first thing to do is to run a `--syntax-check` on your code.  This catches any trivial errors and will cause your build to fail very fast so you can fix the bug quickly.  Next, you can actually provision the VM that Travis gives you to test with.  For Ansible, I recommend breaking this up into different pieces using the `--tags` option so that you can take advantage of concurrency if your CI software supports it. Lastly, you can run some high level tests on your tools to make sure they are actually working as they should.

- For Elastic Search, index a small document
- For Kafka, write something to a topic
- For Hadoop, make a file or run a map reduce job
- For Hbase, write something to the database

You get the idea.

Here is an example **.travis.yml** file that I've used to test Ansible code:

    ::yaml
    sudo: required
    dist: trusty
    addons:
      hosts:
        - travis-trusty
    language: python
    python: '2.7'
    before_install:
      - sudo apt-get update -qq
      - sudo apt-get install -qq python-apt
    install:
      - pip install ansible
    env:
      - TAGS='site-common'
      - TAGS='site-zookeeper'
      - TAGS='deps-kafka'
      - TAGS='ELK'
      - TAGS='scrapy-services'
      - TAGS='scrapy-cluster'
      - TAGS='deps-storm'
      - TAGS='deps-hadoop'
      - TAGS='site-docker-engine'

    matrix:
      fast_finish: true
    script:
      - ansible-playbook -i testing site-infrastructure.yml --tags $TAGS --syntax-check
      - ansible-playbook -i testing site-infrastructure.yml --tags $TAGS --connection=local --become

Note that this requires creating a special **testing** inventory file that uses **travis-trusty** as the hostname for everything.  Also - by taking advantage of Travis TAGS and ansible `--tags`, I can effectively run multiple Ansible builds concurrently which should speed up the overall build status.

# Conclusion

If you have to manage more that one server, you should probably be using some sort of provisioning framework.  Ansible is certainly a good choice, and is becoming increasingly popular relative to other tools such as Chef or Puppet.

Using a combination of Vagrant VM's and CI tools like Travis are essential to making sure you don't break the build.  Vagrant is great for development and Travis is great for those one line changes that "shouldn't" break the build but should get tested anyway.

Inspiration for most of the examples and code snippets was taken from the [ansible-symphony](https://github.com/istresearch/ansible-symphony) repository and most of the development for this code was done for [IST Research](http://istresearch.com).  If you enjoyed this post and want to work with the latest in IT and big data technology, `python`, or Java, shoot me email or get in touch with me on LinkedIn or Twitter!
