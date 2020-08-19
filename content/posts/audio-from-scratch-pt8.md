---
title: "Audio From Scratch With Go: Waveform synthesis"
date: 2020-08-19T20:45:50+02:00
lastmod: 2020-08-19T20:45:50+02:00
tags : [ "audio", "go", "GoAudio" ]
categories : [ "posts" ]
type:  "posts"
highlight: false
draft: false
images: ["/audio/part8/waves.png"]
draft: true
---

In the [previous posts](https://dylanmeeus.github.io/tags/goaudio/) we first looked at how we can
generate a sine wave as raw floats and interpret with ffplay. Later we explored how to read / write
.wave files and how to extract and create 'automation tracks' using breakpoints. 

As you might have noticed, we've never actually created .wave files from scratch with our own sound
data. And, that's about to change now. In this blogpost we'll look at how we can create a variety of
basic soundwaves. 

The code we'll be diving into for this post can be found in the [Github
Examples](https://github.com/DylanMeeus/GoAudio/blob/master/examples/oscillator/main.go) and as part
of the [GoAudio](https://github.com/DylanMeeus/GoAudio/blob/master/synthesizer/oscil.go) library. 

# Constructing an oscillator

An oscillator is a device (in our case software) that generates a periodic (oscillating) signal. The
sine wave is one example of such a waveform, but we'll also look at square waves, triangle waves,
and sawtooth waves. 

At the end of this post, you'll be able to generate signals that look like this:

![](/audio/part8/waves.png)

On the images, these look like connected lines, but in our digital audio signal that we will
generate, we actually have a bunch of separate dots. How many 'dots' do have in each cycle? That
depends on the sample rate we are using. 

We can figure out how to place our dots given the `sample rate`. Remember that we are using radians
in our trig functions, and a period of the wave is thus defined as: `2 * PI`. To know how to place
our dots, we can figure out part of the puzzle (the 'increment') as follows: 

```
increment = (2 * PI) / SampleRate
```

Unfortunately, this is not the entire picture. We also have the issue that our wave has a certain
frequency - which we'll have to account for in our increments. The actual function then becomes:

```
increment = ((2 * PI) / SampleRate) * freq
```

In our `Oscillator` we'll have to track these things. We'll want to know what the current frequency
is that we are generating a wave form, what the current phase in, and how to increment this phase to
get the next value along our wave.


But this solves only part of the puzzle. It's also clear now that we'll need a way to differentiate which type of waveform the user wants to
generate. For this, we can start with an "enum" of a `Shape` type. Each shape will also need to be
calculated in a different way, we can associate a `Shape` with a calculation function with 
`shapeCalcFunc = map[Shape]func(float64)float64`

```go
type Shape int

const (
	SINE Shape = iota
	SQUARE
	DOWNWARD_SAWTOOTH
	UPWARD_SAWTOOTH
	TRIANGLE
)

var (
	shapeCalcFunc = map[Shape]func(float64) float64{
		SINE:              sineCalc,
		SQUARE:            squareCalc,
		TRIANGLE:          triangleCalc,
		DOWNWARD_SAWTOOTH: downSawtoothCalc,
		UPWARD_SAWTOOTH:   upwSawtoothCalc,
	}
)
```

These are our 'elementary' shapes that we'll use for the next few posts. Although we'll extend on
them, they'll give us a solid base to start.

Putting these together, we can define an `Oscillator` struct:

```go

type Oscillator struct {
	curfreq  float64
	curphase float64
	incr     float64
	twopiosr float64 // (2*PI) / samplerate
	tickfunc func(float64) float64
}

// NewOscillator set to a given sample rate
func NewOscillator(sr int, shape Shape) (*Oscillator, error) {
	cf, ok := shapeCalcFunc[shape]
	if !ok {
		return nil, fmt.Errorf("Shape type %v not supported", shape)
	}
	return &Oscillator{
		twopiosr: tau / float64(sr),
		tickfunc: cf,
	}, nil
}
```

Notice that we are storing `twopiosr = tau / SampleRate = (2 * PI) / SampleRate` as a convenience variable. We'll be
using this in a few functions. 

# Generating waveforms

With this constructor, we have the basis for a working oscillator but it's not yet generating
anything. For this purpose we'll need a function that asks the oscillator to generate the next value
of the wave that it's producing. (It can do this indefinitely). This function will need to do a few
things: 

- Accept a frequency for the wave to generate
- Adjust the increment between frames
- Find the value at this phase
- Adjust the current phase
- Do some bounds checks on the phase (optionally)

Our function in Go becomes:

```go
func (o *Oscillator) Tick(freq float64) float64 {
	if o.curfreq != freq {
		o.curfreq = freq
		o.incr = o.twopiosr * freq
	}
	val := o.tickfunc(o.curphase)
	o.curphase += o.incr
        
        // adjust bounds
	if o.curphase >= tau {
		o.curphase -= tau
	}
	if o.curphase < 0 {
		o.curphase = tau
	}
	return val

}
```

The adjustments to our curphase is to keep it in the bounds (Although depending on the
implementation of the `sin` function this might not be necessary, I kept it here as a guard but I'm
pretty sure it's not necessary in Go).

# Calculating waveforms

The only part left to implement is the actual generation of the different shapes of waves. This is
what happens in the call `val := o.tickfunc(o.curphase)`. By using a generic function call, we can
inject the correct calculation function in the call to `NewOscillator()`.

The easiest one to implement is the Sine wave.


```go
func sineCalc(phase float64) float64 {
	return math.Sin(phase)
}
```

A close contender for being the most simple to implement is probably the square wave function. In
this case, half our period is `1` and the other half is `-1`. This probably looks familiar to you if you've
seen binary signals represented as waves before.

```go
func squareCalc(phase float64) float64 {
	val := -1.0
	if phase <= math.Pi {
		val = 1.0
	}
	return val
}
```

The triangle wave is the first one that looks more complex, with the sawtooth waves being related 
to it (you can visually see a sawtooth is being part of the triangle with a sharp cut-off.

```
func triangleCalc(phase float64) float64 {
	val := 2.0*(phase*(1.0/tau)) - 1.0
	if val < 0.0 {
		val = -val
	}
	val = 2.0 * (val - 0.5)
	return val
}

func upwSawtoothCalc(phase float64) float64 {
	val := 2.0*(phase*(1.0/tau)) - 1.0
	return val
}

func downSawtoothCalc(phase float64) float64 {
	val := 1.0 - 2.0*(phase*(1.0/tau))
	return val
}
```
