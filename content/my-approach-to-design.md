Title: My Approach to Design
Slug: my-approach-to-design
Date: 2015-11-29 16:40:12
Tags: python, design, zen
Category: Software Design
Author: Jason Haas
Summary: My approach to design, whether its software, hardware, or systems, is always to achieve the design goals while producing the simplest, efficient, and most maintainable solution.  Some of the most successful products and software applications are ones that are easy to get started with and are intuitive to use.  Here are some thoughts and paradigms that guide my design philosophy.

# The Zen of Python

If you are a python programmer, or doing any technical design for that matter, I highly recommend checking out *The Zen of Python*.  If you are on OSX or Linux, open up a terminal and type `python -c 'import this'`.  You should see this:

    :::text
    The Zen of Python, by Tim Peters

    Beautiful is better than ugly.
    Explicit is better than implicit.
    Simple is better than complex.
    Complex is better than complicated.
    Flat is better than nested.
    Sparse is better than dense.
    Readability counts.
    Special cases aren't special enough to break the rules.
    Although practicality beats purity.
    Errors should never pass silently.
    Unless explicitly silenced.
    In the face of ambiguity, refuse the temptation to guess.
    There should be one-- and preferably only one --obvious way to do it.
    Although that way may not be obvious at first unless you're Dutch.
    Now is better than never.
    Although never is often better than *right* now.
    If the implementation is hard to explain, it's a bad idea.
    If the implementation is easy to explain, it may be a good idea.
    Namespaces are one honking great idea -- let's do more of those!
    
If written well, Python almost reads like plain english, and it is clear to another programmer what is going on with the code fairly quickly.  If I have to spend more than 10 minutes trying to figure out how a class method or function is working, it's probably poorly written.  My take on some of these points:

## Beautiful is better than ugly

I spend extra time making sure my code *looks* good.  Its not just about ascetics, its about maintainability.  One day, myself or someone else is going to have to modify this code, and you don't want them to have to waste time figuring out what the code is doing.  It's kind of like cleaning up your apartment because guests come over to visit.  Some examples:

Bad
    
    :::python
    d = {}
    d['some'] = 1
    d['thing'] = 2
    
Better

    :::python
    d = dict(some=1, thing=2)

Best

    :::python
    d = {
        'some': 1,
        'thing': 2
    }

One could argue that approach #2 is the simplest to type and takes the least amount of space in your text editor.  Although convenient, I think that the #3 looks better, and is easier to see how the dictionary would look after converting to a JSON string.

## Explicit is better than implicit

This is one of the foundations of Python -- if you are going to do something, it should be spelled out in the code.  There shouldn't be any magic going on that can be hard to track down if there are bugs.  Python enforces being explicit in most cases, but design decisions that the programmer makes can influence how explicit the code really is.  Some examples:

### Inheritance vs. Composition

Certainly there is a case for both Inheritance and Composition in Object Oriented Programming and Python in general.  However, in terms of being *Explicit*, composition wins.  Inheritance is very convenient -- you inherit a Parent class and then all of a sudden you have some new magic methods to use!  This is clear in the Python interpreter by doing running the `dir(a)` command on an instance of the clild class.  But -- to figure this out in your text editor you need to most likely hunt around in different places trying to find out where the inherited methods are coming from.  This is annoying and not that *Explicit*.  With composition, you are forced to be explicit.  You likely will have to import specific classes using `from some_module import AwesomeClass`.  At that point anytime something in the `AwesomeClass` namespace is used, it will be clear in the code where it is being used like `AwesomeClass.more_awesome()`.

### Using *args and **kwargs

This is another one that definitely has its uses, but I prefer to stay away from it unless absolutely necessary (decorator functions, inheritance) due to its ambiguity.  `*args` and `**kwargs` allows the user of a function to pass an arbitrary number of arguments into your function.  Since the function does not enforce any arguments, it needs to handle all the cases where random arguments could be passed in.  This could require a bunch of code that could get messy and may be hard to maintain.  If many arguments need to be passed in, better to use a `list` or a `dict` and explicitly define that in the function doc string.

## The Art of Unix Programming

*The Art of Unix Programming* is another great resource for providing some guidelines on good UNIX and programming practices.  These guidelines can benefit any programmer or hacker.  Especially if someone is coming from a Windows or strictly Java background, this could be particularly useful.  Some of my favorite paradigms are:

- This is the Unix philosophy: Write programs that do one thing and do it well. Write programs to work together. Write programs to handle text streams, because that is a universal interface.
- Design and build software, even operating systems, to be tried early, ideally within weeks. Don't hesitate to throw away the clumsy parts and rebuild them.
- Programmer time is expensive; conserve it in preference to machine time.
- Avoid hand-hacking; write programs to write programs when you can.

Bear in mind that a lot of this is coming out of a circa 1978 time period.  These ideas are especially relevant today -- I guess there's a reason UNIX has been around so long.

# Closing thoughts

The next time someone comes to you for a idea or has a technical solution, consider these thoughts from the *Zen of Python*.

- If the implementation is hard to explain, it's a bad idea.
- If the implementation is easy to explain, it may be a good idea.

# Resources

- [Hitchhikers Guide to Python](http://docs.python-guide.org/en/latest/)
- [The Art of Unix Programming](http://www.catb.org/esr/writings/taoup/html/)
