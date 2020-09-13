---
title: "Audio From Scratch With Go: Frere Jacques"
date: 2020-09-13T16:27:35+02:00
lastmod: 2020-09-13T16:27:35+02:00
tags : [ "audio", "go", "GoAudio" ]
categories : [ "posts" ]
type:  "posts"
highlight: false
draft: false
images: ["/audio/part10/adsrschema.png"]
draft: true
---

In the [last post](https://dylanmeeus.github.io/posts/audio-from-scratch-pt11) I ended by saying we
would be able to use [GoAudio](https://github.com/DylanMeeus/GoAudio) to generate some simple tunes.
In this post we will actually put that to the test. 

## Frere Jacques

When I was a kid, the first thing I was taught to play was the tune to 'Frere Jacques' on my grandparents' piano (to their dismay,
also the last thing I actually learned to play until I picked up a guitar 15 years later and played that badly). As such, I thought it'd be fitting to try to code
this song this time. The notes for playing this are taken from [true-piano-lessons.com](https://www.true-piano-lessons.com/frere-jacques.html
). The code takes the notes starting in the key of C. (Maybe since it's in Go, I should have started
in G. Feel free to change it).

## Generating notes

In the previous posts, we actually ignored the problem of turning notes into frequencies.
[GoAudio](https://github.com/DylanMeeus/GoAudio) works with given frequencies. So we'll need to
first implement a way to turn the notes into frequencies. For this, I came up with a somewhat
hackish solution but I didn't know a better way other than hardcoding it. 

As we're making the music using the equal-tempered scale we can calculate the frequencies for each
note given a reference frequency. I'm using `middle C` as the reference frequency, which can be
derived from `concert A (A440`) in this way: `middleC = (concertA * math.Pow(2, 3/12)) / 2`.

To follow along with how we derive the frequencies for each note, I suggest taking a look at
[wikipedia](https://en.wikipedia.org/wiki/Equal_temperament). The basic idea however is that we have
12 semitones in an octave, so for each octave we have to generate the 12 semitones based off a
reference frequency. Confusingly however, an octave starts at `C` and not at `A`. (it does loop
around) so we get: `C D E F G A B`. Each time we loop around and get back to C, we move up one
octave (meaning higher frequency, thus higher pitch). 

You can view a table of all frequencies from C0 (C at octave 0) up to B8 (B at octave 8)
[here](https://pages.mtu.edu/~suits/notefreqs.html).


### Heading 3

At quisque litora ullamcorper maecenas ultricies ut dignissim luctus curabitur, cras congue eget primis aliquam fringilla nulla dictum posuere, vestibulum sit magnis nisl praesent eros ipsum nunc. Ligula lacus ipsum orci aenean integer pharetra habitasse interdum, porttitor etiam hac feugiat placerat morbi posuere turpis leo, quam at amet gravida commodo fringilla erat.