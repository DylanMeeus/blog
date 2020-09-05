---
title: "Audio From Scratch With Go: ADSR"
date: 2020-09-05T14:01:57+02:00
lastmod: 2020-09-05T14:01:57+02:00
tags : [ "audio", "go", "GoAudio" ]
categories : [ "posts" ]
type:  "posts"
highlight: false
draft: false
images: ["/audio/part9/halfsampling.png"]
draft: true
---

With everything that we have added to our library so far we are almost capable of generated small
tunes. One thing that's missing to make it sound more 'natural' is a way for the notes to start and
stop. 

In this post we will implement a type of envelope called "ADSR", for "Attack, Decay, Sustain,
Release". Which will make the notes sound more natural as they are played in sequence.

To see why we need this, listen to this sound generated without an ADSR envelope around the
generated frames.

## Heading 2

Sollicitudin ornare odio blandit aenean enim lacus accumsan elementum vestibulum porta mauris lorem, ullamcorper class fermentum sem hendrerit ante augue penatibus scelerisque felis leo proin,ad nascetur venenatis sodales dignissim viverra suspendisse turpis convallis condimentum sapien.

### Heading 3

At quisque litora ullamcorper maecenas ultricies ut dignissim luctus curabitur, cras congue eget primis aliquam fringilla nulla dictum posuere, vestibulum sit magnis nisl praesent eros ipsum nunc. Ligula lacus ipsum orci aenean integer pharetra habitasse interdum, porttitor etiam hac feugiat placerat morbi posuere turpis leo, quam at amet gravida commodo fringilla erat.
