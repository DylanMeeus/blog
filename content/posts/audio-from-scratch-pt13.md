---
title: "Audio From Scratch With Go: Note to frequency"
date: 2020-10-05T21:38:02+02:00
lastmod: 2020-10-05T21:38:02+02:00
tags : [ "audio", "go", "GoAudio" ]
categories : [ "posts" ]
type:  "posts"
highlight: false
draft: false
images: ["/audio/part12/audacity.png"]
draft: true
---

In the [last post](https://dylanmeeus.github.io/posts/audio-from-scratch-pt12/) the tune to 'Brother
Jacob' was generated using GoAudio. We started of by actually generating all the notes and their
corresponding frequencies, and mapping them to a corresponding string, such that when we played `A4`
we would get a frequency of `440`. 

There were two problems with this from what I can tell, the first is that this approach is
potentially repetitive. Each time we want to generate some music, we're likely to generate a mapping
of notes to frequencies. Having this as an external part of the code rather than the GoAudio library
is the first problem.

The second problem is that this approach was not flexible nor easy to read. Yes, the mapping did
work, but can you easily see which octave the notes are being generated in? 

As a reminder, here is the original code:


```go
func generateNotes() map[string]float64 {
	ni := 0
	concertA := 440.
	middleC := (concertA * math.Pow(2, 3./12.)) / 2.
	FR := middleC
	notemap := map[string]float64{}
	for i := 0; i < 24; i++ {
		FK := FR * math.Pow(2, float64(i)/12.)
		note := notes[ni%len(notes)]
		octave := 4 + i/12
		var octs string
		if octave != 0 {
			octs = strconv.Itoa(octave)
		}
		notemap[note+octs] = FK
		ni++
	}
	notemap["WAIT"] = 0.
	return notemap
}
```

Which octaves are generated here? Well, given that we find the frequency of middle C, which we calculated from
A440, we can tell that we are starting at `C4` and moving up 24 semitones in the for-loop means we are
moving across two octaves. Each octave being 12 semitones, thus we are covering both the fourth and
fifth octave in this segment of code. 

# Improving generateNotes()

The first problem is easily solved, the code that we are examining in the following section is now
covered by [GoAudio](https://github.com/DylanMeeus/GoAudio). If you want to skip the rest of this
post, you can just [view this
file](https://github.com/DylanMeeus/GoAudio/blob/master/synthesizer/synth.go#L64). 

The second problem, which was to deal with the readability and flexibility of the code is tackled
next. First, rather than keeping a map of all possible frequencies for all octaves in all notes, we
will calculate it on the spot. This is more wasteful of our CPU resources, but if a user
wanted to keep the full spectrum available they could keep the map locally, no need to pollute the
library with this. 

Our botched together code from the last post does get us pretty close to a working solution here,
To generate a frequency of a note in any octave, we have to change this line:

```go
    FK := FR * math.Pow(2, float64(i)/12.)
```

Here we are stuck in octave 4 by default (due to FR) and we stay in octave 4 for as long as `i`is
below 12. There are 12 semitones in an octave, so when we try to generate the frequency for `i = 13`
we are generated it one octave higher, or `1 + 1/12`. This is the key to extending the formula to
work for any octave. As our reference will still be A440, we have to calculate it with an offset of
4 in mind. This gives us the following piece:

```go
	FR * math.Pow(2, float64(octave-4)+(float64(i)/12.))
```

Now that we have this in place, we still need to figure out how to turn a note (A,B,..G) into
something that we can plug into the formula. That's easier than it sounds, a note here correlates to
a certain semitone, which in the equation above is represented by (i). Remember that in the previous
post we were literally iterating through all semitones, thus notes, to generate all their
frequencies. 

Thus, we add a mapping from note -> integer:

```go
	noteIndex = map[string]int{
		"a":  0,
		"a#": 1,
		"bb": 1,
		"b":  2,
		"c":  3,
		"c#": 4,
		"db": 4,
		"d":  5,
		"d#": 6,
		"eb": 6,
		"e":  7,
		"f":  8,
		"f#": 9,
		"gb": 9,
		"g":  10,
		"g#": 11,
		"ab": 11,
	}
```

The sharps are denoted by `#`, and the flats are denoted by `b`. Thus `c# = db = 4`. 

