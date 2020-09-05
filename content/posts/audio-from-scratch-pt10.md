---
title: "Audio From Scratch With Go: ADSR"
date: 2020-09-05T14:01:57+02:00
lastmod: 2020-09-05T14:01:57+02:00
tags : [ "audio", "go", "GoAudio" ]
categories : [ "posts" ]
type:  "posts"
highlight: false
draft: false
images: ["/audio/part10/adsrschema.png"]
draft: false
---

With everything that we have added to our library so far we are almost capable of generated small
tunes. One thing that's missing to make it sound more 'natural' is a way for the notes to start and
stop. 

In this post we will implement a type of envelope called "ADSR", for "Attack, Decay, Sustain,
Release". Which will make the notes sound more natural as they are played in sequence.

To see why we need this, listen to this sound generated without an ADSR envelope around the
generated frames.

- [Without ADSR](/audio/part10/no_adsr.wav)
- [With ADSR](/audio/part10/adsr.wav)

If you want to read the (not pretty) code that generated this, check out this [github
gist](https://gist.github.com/DylanMeeus/83f3ae5d628d11533b8fbd47298d8434). 

# ADSR

The Attack, Decay, Sustain and Release envelope is a common type of envelope. Schematically this can
be represented as below (from wikipedia): 

![Wikipedia schematic of ADSR envelope](/audio/part10/adsrschema.png)

As we apply this envelope to a signal, the signal will change in amplitude depending on which phase
we are in of the ADSR envelope. In the image it is visible that the amplitude rises during the
attack step, reaches a peak amplitude before decreasing a bit. After decreasing it reached the
sustain amplitude, where it will stay until the note is released, and after release it decays until
the ampltide is zero. 

For our parameters, three will relate to time:

- attack (time to rise)
- decay (time to fall to sustain level)
- release (time to decay from sutan to zero)

So the Sustain parameter does not refer to time, but rather to the amplitude we will maintain. 

Turning this schematic into code, we get :

```go
func ADSR(maxamp, duration, attacktime, decaytime, sus, releasetime, controlrate float64, currentframe int) float64 {
	dur := duration * controlrate
	at := attacktime * controlrate
	dt := decaytime * controlrate
	rt := releasetime * controlrate
	cnt := float64(currentframe)

	amp := 0.0
	if cnt < dur {
		if cnt <= at {
			// attack
			amp = cnt * (maxamp / at)
		} else if cnt <= (at + dt) {
			// decay
			amp = ((sus-maxamp)/dt)*(cnt-at) + maxamp
		} else if cnt <= dur-rt {
			// sustain
			amp = sus
		} else if cnt > (dur - rt) {
			// release
			amp = -(sus/rt)*(cnt-(dur-rt)) + sus
		}
	}

	return amp
}
```

One parameter in this function that you don't find in the schematic is the need for a control rate.
The control rate will be used to turn a duration in seconds into an amount of frames. The control
rate could just be sample rate but this does not necessarily have to be the case. One such use-case
us sub-audio modulation, whereby the modulating oscillator is running below 20Hz. You can check
[this chapter](https://cmtext.indiana.edu/synthesis/chapter4_modulation.php) for a bit more on that.


# Application

To apply the ADSR envelope to a signal, for example to one that was generating using the [oscillator
we created](https://dylanmeeus.github.io/posts/audio-from-scratch-pt8.md) we have to iterate over
each frame, pass the current frame to the ADSR function, and modify the amplitude of the frame with
the result. For example, this is the complete example program included in
[GoAudio](https://github.com/DylanMeeus/GoAudio/blob/master/examples/adsr/main.go).


```go
package main

import (
	"flag"
	"fmt"

	synth "github.com/DylanMeeus/GoAudio/synthesizer"
	"github.com/DylanMeeus/GoAudio/wave"
)

func main() {
	flag.Parse()
	osc, err := synth.NewOscillator(44100, synth.SINE)
	if err != nil {
		panic(err)
	}

	sr := 44100
	duration := sr * 10

	frames := []wave.Frame{}
	var adsrtime int
	for i := 0; i < duration; i++ {
		value := synth.ADSR(1, 10, 1, 1, 0.7, 5, float64(sr), adsrtime)
		adsrtime++
		frames = append(frames, wave.Frame(value*osc.Tick(440)))
	}

	wfmt := wave.NewWaveFmt(1, 1, sr, 16, nil)
	wave.WriteFrames(frames, wfmt, "output.wav")
	fmt.Println("done writing to output.wav")
}
```

In this example, notice that our control rate is the same as our sample rate, and the adsrtime
increases together with the frames that we have processed. (We could thus pass the `i` iterating
variable to the function, but I thought making it explit was clearer).

# Resources

- [GoAudio](https://github.com/DylanMeeus/GoAudio)
- [ADSR example](https://github.com/DylanMeeus/GoAudio/blob/master/examples/adsr/main.go)

------

If you liked this and want to know when I write new posts, the best way to keep up to date is by [following me on
twitter](https://twitter.com/DylanMeeus).
