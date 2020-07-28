---
title: "Audio From Scratch With Go: Breakpoints"
date: 2020-07-26T20:31:44+02:00
lastmod: 2020-07-26T20:31:44+02:00
tags : [ "audio", "go", "GoAudio" ]
categories : [ "posts" ]
type:  "posts"
highlight: false
draft: true 
---

# Audio Breakpoints

To clear up a potential mistake, this blogpost is about breakpoints for audio files, not the ones we
use for debugging code ;-). A breakpoint file forms the basis for what is often called 'envelopes' or
'automation tracks' in [DAWs](https://en.wikipedia.org/wiki/Digital_audio_workstation).

They are simple files that contain pairs of `timestamp:value` data. With this simple structure, they
allow us to specify what certain properties of the sound file should look like at various points in time. 

For example, this is a screenshot of an automation track I made in FL Studio to apply
panning on a rendition of Africa, by Toto: 

![](/audio/breakpoints/stereopan.png)
[(Open in new window)](/audio/breakpoints/stereopan.png)

Here you can compare the two sound files (easier on headphones):
- [Original](/audio/breakpoints/africa-og.wav)
- [Panned](/audio/breakpoints/africa-pan.wav)

In this post we will go over the fundamentals of working with breakpoint files, and in the next post
we will look at how we can change the panning code from the [previous
post](https://dylanmeeus.github.io/posts/audio-from-scratch-pt4) to make use of this. 

Such a pan could for example have been encoded like this: 

|time (sec)|value|
|----------|-----|
|0|1|
|5|-1|
|10|0|
|13.37|0.55|

As the first value encodes time, the first value has to be a strictly rising value (until we invent
time travel). The second value however depends on what exactly you are 'automating'. In the case of
our left-right pan we can encode it with values ranging from -1 to 1. As we've seen in the [previous
post](https://dylanmeeus.github.io/posts/audio-from-scratch-pt4) this will allow us to modify the
samples in a suitable way for getting this effect. Do note however that our panning function is not
a perfect pan yet - so we won't get quite the same result as FL Studio does. More on that later.

# Linear interpolation

As you might have noticed, the time values in our breakpoint file do not have to increment at the
same time-increments as our samples. That's great because we can keep the files smaller, but we
don't want the audio to 'jump' from left to right at a certain instant in time. If we encode the
values:

|time (sec)|value|
|----------|-----|
|0|1|
|5|-1|

We don't mean to say "start at 1, and jump to -1 at second number 5". What we actually want to say
is "Start at 1, and gradually decrease until -1". The tool to solve this is [Linear
Interpolation](https://en.wikipedia.org/wiki/Linear_interpolation). 

So now it's just a matter of finding out which two values in a breakpoint file the sample we are
processing fall inbetween of. Thus, if our sample is played `2.5` seconds into the song, we find
that the value must be half way between the values at second `0` and second `5`, leaving us with a
pan of `0` (Thus, entirely balanced left-right audio). The values `0` and `5` we will call the
`span`.

# Recipe

(As usual, all the code can be found on [Github](https://github.com/DylanMeeus/GoAudio/blob/master/breakpoint/breakpoint.go).

Having this background information on breakpoint files, we also have a rough recipe in mind for how
to work with breakpoint files. There's a few steps our breakpoint module will need to do:

- Read a breakpoint file
- Parse strings to "Time-Value" pairs
- Given a frame time, find the span it falls between
- Use linear interpolation to find the exact value

There'll be a few edge cases to take care off, but this is a rough outline of what we need. 

# Parsing breakpoint files

The first function we should implement is the function to parse an actual file to a slice of
breakpoints. We're assuming breakpoints will be passed as a file, but we'll actually take an
abstraction of this and just accept an `io.Reader` instead. 

Our breakpoint time-value pars will be encoded like `time:value`. Although you could use a different
separator if you want to, it'll just be a minor adjustment to the code.

First we can define our breakpoint type:

```go
type Breakpoint struct {
        Time, Value float64
}
```


Hence we take some input from an io.Reader, we parse it into separate lines. Then for each line we
split on our separator (`:`) and turn these values into `float64` values. These get bundled up into
our `Breakpoint` struct and then added to a slice called `[]Breakpoint` which we will return to the
user. This code could use some slice bounds checks, but this way it is easier to read for this post

```go
func ParseBreakpoints(in io.Reader) ([]Breakpoint, error) {
	data, err := ioutil.ReadAll(in)
	if err != nil {
		return nil, err
	}

	lines := strings.Split(string(data), "\n")

	brkpnts := []Breakpoint{}
	for _, line := range lines {
		line = strings.TrimSpace(line)
		if line == "" {
			continue
		}
		parts := strings.Split(line, ":")
		time := parts[0]
		value := parts[1]

		tf, err := strconv.ParseFloat(time, 64)
		if err != nil {
			return brkpnts, err
		}
		vf, err := strconv.ParseFloat(value, 64)
		if err != nil {
			return brkpnts, err
		}

		brkpnts = append(brkpnts, Breakpoint{
			Time:  tf,
			Value: vf,
		})

	}
	return brkpnts, nil
}
```

# Finding the correct value 

The other important part for our breakpoint module is to actually return a value given a slice of
breakpoints and a requested time. As mentioned earlier, this will be done with linear interpolation
on the values that we find for a given span. The first edge case we need to think about: What if
our data point lies _after_ the last entry? In this case, no interpolation nees to happen and we
just return the last value. 

The first step will be to find the correct span. We can iterate over all Time-Value pairs until we
have exceeded the `Time` part, thus knowing that the last Time we saw is the 'start' of our span.

```go
func ValueAt(bs []Breakpoint, time float64, startIndex int) (index int, value float64) {
	if len(bs) == 0 {
		return 0, 0
	}
	npoints := len(bs)

	// first we need to find a span containing our timeslot
	startSpan := startIndex // start of span
	for _, b := range bs[startSpan:] {
		if b.Time > time {
			break
		}
		startSpan++
	}
        ...
```

With this code we have found the correct startSpan, and we also have a small guard statement in case
there are no breakpoints being passed.

The first edge case can be handled here, if our `startSpan` is larger than the amount of breakpoints in
the slice, we can just return the value of the last breakpoint we encountered in the loop.

```go

	// Our span is never-ending (the last point in our breakpoint file was hit)
	if startSpan == npoints {
		return startSpan, bs[startSpan-1].Value
	}

```

Now that we have taken care of this edge case, we actually can retrieve a span. And we hit the
second edge-case, what if the two times in our breakpoint are the same? Imagine this:

|time(sec)|value|
|---------|-----|
|5|1|
|5|-1|

When this happens we have an instant jump. In this case we have to return the value associated with
the last entry. Thus in our example, The result would be `-1`. This could be the case if the user
would want a gradual rise to the value `1` in the first 5 seconds, and then an immediate jump to
`-1`. This can be detected if the 'distance' between our two timestamps is zero.

```go
	// check for instant jump
	width := right.Time - left.Time

	if width == 0 {
		return startSpan, right.Value
	}
```

Finally we get past the 'edge cases' and end up at the interpolation part. We can finish the
function with this using the `width` we calculated above:

```go
	frac := (time - left.Time) / width
	val := left.Value + ((right.Value - left.Value) * frac)
	return startSpan, val
```

Great, with this we are all set to start working on our first automation track!

# Resources

- [GoAudio](https://github.com/DylanMeeus/GoAudio)
- [Breakpoint code](https://github.com/DylanMeeus/GoAudio/blob/master/breakpoint/breakpoint.go)

------

If you liked this and want to know when I write new posts, the best way to keep up to date is by [following me on
twitter](https://twitter.com/DylanMeeus). ;-)



