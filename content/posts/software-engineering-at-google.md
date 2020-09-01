---
title: "Software Engineering at Google"
date: 2020-08-25T19:57:06+02:00
lastmod: 2020-08-25T19:57:06+02:00
tags : [ "books" ]
categories : [ "books" ]
type:  "posts"
highlight: false
draft: false
images: ["/se-at-google/cover.jpg"]
draft: false
---

If there was one book this year that it was hard to avoid hearing about, it was "Software
Engineering at Google". As such, it was only a matter of time before I jumped on the bandwagon and
decided to give it a read, but I'm happy I finally did! 

I track my highlights and notes through my kindle / goodreads, and ended up with about 80 of them.
In this blogpost, I'll just go over some of what that I thought stood out in the book in one way or
another. In
general though, the book should probably be some kind of recommended reading material for students
of software engineering at universities.

![](/se-at-google/cover.jpg)

# Software Engineering != Programming

Almost right off the bat (1% into the book according to my highlight), the book starts with a discussion on what they mean with the title
'Software Engineering'. It's something I myself have not given too much thought, I consider myself a
software engineer and _part_ of what I do is programming.

The way they phrased it, is that "Software engineering is programming
integrated over time". This statement does sum it up quite well (calculus pun intended). If programming is the art of
writing code, software engineering is the art of making sure this code continues to run in the
future. This immediately highlights what surrounds programming in the day-to-day of a software
engineer. Just as in the more 'traditional' engineering fields, once you build something to last
you want to plan ahead of time. This is where the meetings, design documents, integration tests,
etc.. enter the picture.

Once you see the difference between the two, it starts to make sense that the book
includes only a few lines of code. The book isn't about the programming aspect as much, it's about
what surrounds it to make it engineering.


# Use tools to ensure compliance

This applies to how well the engineers in a company follow things such as the styleguide and that
unit tests should be written. If you set out some rules, such as "never panic your Go code", this
should be checked automatically through static analysis rather than having it mentioned in a review.

Of course this makes a lot of sense, but in general it happens that people agree on a convention
which is written down "somewhere", but validating compliance becomes a burden and thus forgotten.
When a tool can check for compliance, this makes it easier on the developer to know that they are
doing the right thing, it makes it faster to ensure compliance on a large codebase, and furthermore
when the rules change a tool could be written to automatically rewrite parts of the codebase that
need updating. 

In itself, this sounds obvious but it can be harder to do than it sounds at first. Depending on
which language and framework you are using, these tools might not be provided out of the box,
meaning that you'll have to spend engineering time on creating these tools in the first place. For
many smaller software companies this might sound like a waste of time, as the benefit is only
visible at scale. Personally, I do think that a kind of balance needs to be struck here, for a 2-man
startup, it would be complete overkill to write your own static analysis tools for every such
decision that is made. But for larger organizations, it does sounds reasonable.


# Hyrum's Law

Hyrum's Law states that with a sufficient number of users of an API, it does not matter what the
API promises in the contract, because all observable behaviour will eventually be depended on by somebody. 
I'm not as conscious of this as I should be. Especially for an open source project this is something
to keep in mind. Whenever you change your API, even if you change something that's technically
'undocumented' or wasn't "the intended use case", you're going to make some people unhappy. 

When you control everything, meaning you develop internal tools, these kinds of suble breaking
changes might be easier to push through, as you can fix the code of whomever depends on it. When you
make such a change in an open source project depended on by thousands, or millions, the cost is way
higher. 


I can imagine scenarios where this trade-off is genuinely hard though. What if you know people are
using your API in a way that was unexpected, by relying on a bug? Should you still fix that bug? You
can create a new function without the bug, but now it might be more confusing for future users to
understand what is going on. I don't have an answer to this, I don't recall that the book had one.


# Relationships outlast projects

There are quite a few chapters in the book that talk about the 'management' side of things. Building
relationships and networking is definitely valuable, it's just good to be reminded of this every now
and then. 

# Give junior members space to grow

In one of the chapters they mention that as a tech lead it can be hard to see a junior colleague
struggle with a problem, when you know that the problem would be solved in half an hour if you
did it yourself. Here they urge you to let the junior developer try for some time, as having them
learn on their own can be a valuable experience. You don't have to forsake them of course, you can
nudge them in the right direction and assist them with things when they need it. But don't do the
work for them just because it would take them longer. Give them space and time to grow.


------

If you liked this and want to know when I write new posts, the best way to keep up to date is by [following me on
twitter](https://twitter.com/DylanMeeus).
