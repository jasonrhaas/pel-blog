Title: Git Fab Part 1
Slug: git-fab-part-1
Date: 2015-08-09
Tags: git
Category: software development
Author: Jason Haas 

If you're luckly enough to live in the modern era of version control, you probably rely on `git` on a daily basis.  When I started to get into software, I had tinkered around with CVS, SVN, and a tool called Accurev.  Before I left my last company, I started to learn `git`.  Almost immediately I saw how it was powerful beyond traditional version control tools.  However, I see a lot of software developers not taking advantage of it's full functionality.

If you are not using `git revert`, `git reset`, `git log -p`, git commit -p` `git cherry-pick`, etc, you are probably not taking full advantage of git's capabilities.  If you are commenting out code, you are probably doing it wrong.  Commit often and have faith that git has your back.

Also -- there are great tools to use alongside the command line for git:

- **Atlasian's SourceTree**
	- It's not as powerful as the CLI, but it does come in handy.  Especially when you want to take a break from typing and do some pointing and clicking.  Also -- I really like the tree view that it gives you.  It makes it easy to see where each branch is and if your local copy is ahead or behind origin.
- **zsh**
	- The `prezto` plugin for `zsh` has some great helpers and also a gigantic git alias list.  If you are just starting out with git this may help.  I already had some aliases that I got used to, so I didn't end up using this.
- **custom aliases**
	
Here are some aliases I use for git.  

	:::bash
	alias ga='git add'
	alias gb='git branch -v'
	alias gc='git commit'
	alias gco='git checkout'
	alias gd='git diff'
	alias gl='git log --all --decorate --graph --oneline'
	alias glt='git log --graph --pretty=format:'\''%Cred%h%Creset -%C(yellow)%d%Creset %s %Cgreen(%cr) %C(bold blue)<%an>%Creset'\'' --abbrev-commit --date=relative'
	alias gp='git push'
	alias gr='git remote -v'
	alias gs='git status'
