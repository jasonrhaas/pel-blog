Title: Turn your Mac into a lean, software developing machine
Slug: turn-your-mac-into-a-lean-software-developing-machine
Date: 2015-09-06
Tags: mac, OSX, productivity, sublime, vim, sourcetree, flycut, caffeine
Category: productivity
Author: Jason Haas

I've been doing software development on a Macbook Pro for a little while now, and I gotta say there are a TON of great free packages and tools that make development that much more enjoyable.  I'm not going to get into a Windows/Mac/Linux debate here, lets just say Mac OSX wins, with Linux a close second.  All of the production code that I run runs in Linux, and most of all runs natively on my Mac as well.  That with the combination of all the other nice feature of the Mac make it unmatched for software development.

OK so I want to talk about some tools and nifty tricks that I use on a fairly regular basis.

## Sublime Text 3

If you do most of your development on a Mac already, you probably know about Sublime Text.  It's a lightweight and *fast* editor with a *ton* of free plugins for just about everything you can imagine.  I do most of my work in `python` and use `git` for version control, so this list will be a little skewed towards those technologies.

### Color Sublime

[Colorsublime](http://colorsublime.com) has about a billion different built in color themes, and you can actually preview them right in Sublime before even installing them by using the Sublime Text 3 command pallet.

### Git Gutter

[Git Gutter](https://github.com/jisaacks/GitGutter) is another fantastic plugin compares your working copy of a file to the version in the git index.  

This is similar to doing `git diff` on the command line.  By default it compares against **HEAD** but this can be changed to compare against specific branches, tags, or commits.

### Sublime Linter

[Sublime Linter](https://github.com/SublimeLinter/SublimeLinter3) is a *framework* for using code linters in **Sublime Text**.  Any linters you wish to use need to be installed separately.  For ``python``, there are many linters but I recommend using **pyflakes** at a minimum.  It's also a good idea to use the **pep8** linter to make sure you are following the PEP8 Python standards.

ProTip:  I recommend changing the settings to for **Sublime Linter** to manual mode.  By default it lints every file you have open *in real time*, which I've found can cause Sublime to hiccup and lag -- very annoying.  To change the settings --

Open up the command palette, and select **SublimeLinter:  Choose Lint Mode --> Manual**

### ReStructuredText Improved

[ReStructuredText Improved](https://packagecontrol.io/packages/RestructuredText%20Improved) is a nice plugin that does syntax highlight of your ReStructuredText.  It integrates very nicely into Sublime and is very unobtrusive, unlike some of the **Markdown** plugins for Sublime that I have seen.


### Honorable mentions

Some other plugins I use...

- Bracket Highlighter
- Sidebar (sidebar enhancements)
- PyDOC (links to python documentation by right clicking on code)


## FlyCut

FlyCut is a great little piece of software that keeps a copy-paste buffer within easy reach.  By default, just hit `shift+command+v` to pull up the dialog.  This is such a simple thing but it saves an *immense* amount of time.  You can download it on the Mac App Store.

## Caffeine

If you ever get annoying at your computer dimming its screen and going to sleep when you want the screen to stay on, this little app is for you.  Again -- a really simple piece of software that really improves Mac usage.  Basically you just click the **coffee** button when you want your Mac to stay awake.

## Spectacle

Another simple, extremely useful peice of software is **Spectacle**.  This application lets you easily place and re-size your windows with a bunch of keyboard shortcuts.  Actually -- this is such a good idea that Apple has decided to incorporate something very similar into their #El-Capitan OSX release coming later in the Fall.

## f.lux

If you work late like I do, that blueish screen can be pretty harsh on the eyes.  Check out f.lux -- it gradually makes the screen go redder as the night wears on.  It is easier on the eyes and also helps you get to sleep faster after a long night of coding.

## SourceTree

This is a GUI interface for `git`, made by Atlassian.  Now -- I know what you're thinking -- "it's not command line!  CLI is way more powerful!"  Yes -- that is true, and I use the command line for `git` most of the time.  However, if you have a bunch of changes and really want to do diffs on what changed, and potentially break the chunks into smaller commits, SourceTree beats the CLI.  I know this can be done via `git add -p`, but the GUI interface is just better for this. 