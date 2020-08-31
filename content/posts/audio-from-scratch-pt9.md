---
title: "Audio From Scratch: Waveform tables"
date: 2020-08-31T21:01:02+02:00
lastmod: 2020-08-31T21:01:02+02:00
tags : [ "audio", "go", "GoAudio" ]
categories : [ "posts" ]
type:  "posts"
highlight: false
draft: false
images: ["/audio/part8/waves.png"]
draft: false
draft: true
---

In the [previous post](https://dylanmeeus.github.io/posts/audio-from-scratch-pt8) the aim was to
synthesize different waveforms, such as triangle waves and square waves. While this implementation
gives us a good start, it is not as performant as we would like. All these waveforms were cyclical,
so there was not an actual need to always calculate the right value in the moment.

The solution when you don't want to recalculate something over and over is caching, and in the case
of audio progamming we are going to store the waveform in a 'table', through which we can look up
the values with an Oscillator. In general we will want to store one cycle of the waveform at a
chosen fidelity, where the fidelity / precision is determined by how many points we store. 

As we are chunking the wave in smaller points, we might not be able to retrieve the exact value of
the wave at a given timestamp. To solve this, we will use linear interpolation to estimate a value
for the missing timestamp, similar to how we resolved finding the correct value for
[breakpoints](https://dylanmeeus.github.io/posts/audio-from-scratch-pt5).

## Building the table 

Fundamentally there are two parts to this problem, first we need to figure out how to store the
waveform in a table, and next we need to figure out how we can read this data from the table at the
correct frequency.

-- Try to animate a wave being chunked?

For storing the waveform, we will want to store `X` data points along the wave. These data points
are the samples that we are taking. In an analog signal we have a continous wave, when we convert it
to a digital signal it becomes discrete, but for a large enough `X` it becomes indistinguishable
from the real signal. (This equivalence will help us down the road as well, when we start reasoning
about manipulation of this signal).

To figure out the spacing between each point we can use `step = (2*PI)/X`. Once we have this, we
loop from `0 -> X` and generate the expected value. For the sine wave, this then becomes:


```go
type Gtable struct {
	data []float64
}

func NewSineTable(length int) *Gtable {
	g := &Gtable{}
	if length == 0 {
		return g
	}
	g.data = make([]float64, length+1) // one extra for the guard point.
	step := tau / float64(Len(g))
	for i := 0; i < Len(g); i++ {
		g.data[i] = math.Sin(step * float64(i))
	}
	// store a guard point
	g.data[len(g.data)-1] = g.data[0]
	return g
}
```

The last bit, where the final entry in our table is equal to the first entry will help us with the
linear interpolation in our oscillator. It's not too important to worry about this for now. Also
remember that in the code, we use `tau = 2 * PI`.


### Heading 3

At quisque litora ullamcorper maecenas ultricies ut dignissim luctus curabitur, cras congue eget primis aliquam fringilla nulla dictum posuere, vestibulum sit magnis nisl praesent eros ipsum nunc. Ligula lacus ipsum orci aenean integer pharetra habitasse interdum, porttitor etiam hac feugiat placerat morbi posuere turpis leo, quam at amet gravida commodo fringilla erat.
