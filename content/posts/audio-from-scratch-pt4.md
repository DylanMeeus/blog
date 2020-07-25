---
title: "Audio From Scratch With Go: stereo panning"
date: 2020-07-20T19:15:32+02:00
lastmod: 2020-07-20T19:15:32+02:00
tags : [ "audio", "go", "GoAudio" ]
categories : [ "posts" ]
type:  "posts"
highlight: false
draft: false
---

In the [previous post](https://dylanmeeus.github.io/posts/audio-from-scratch-pt3/) we have written code to change the amplitude of wave files. 

Now we'll take a look at how we can turn a mono wave file into a stereo wave file with an optional
panning, and explore how this is represented internally by the WAVE file format.


# Channels 

The raw audio data inside a WAVE file consists of multiple frames. For now, we have called them
'samples' although that is strictly speaking not entirely correct. In fact, single float in the raw
audio data only corresponds to a single sample when we assume a mono audio file.

When you have multiple channels, a single 'sample' can consist of multiple frames. As each channel
needs to play a certain 'frame' at any given point in time. 

In the WAVE file format, the channels are interleaved. For example, a stereo file would be
laid out like this:

![](/audio/interleaving.png)

Here, each sample consists of two frames. Such that frame 1 and 2 make up sample 1, frame 3 and 4
make up sample 2, and so on..

Programs know how to interpret the raw audio data because of the `fmt` chunk inside the audio file,
which specifies the number of channels that are present in the raw audio data. The maximum number of
channels in a wave file is actually as high as 65,536, which does not actually make sense for audio
data. 

Some common ones would be:

- 1-channel: mono
- 2-channel: stereo
- 3-channel: stereo + center channel 
- 4-channel: Quadrophonic
- 5-channel: "Surround sound"

For convenience though, we'll mostly work on mono and stereo files. Not only are they the most
commonly used, this also allows us to test our code without needing a more expensive setup. 


# Panning 

So what is a pan? When you pan an audio signal, you essentially make an audio signal 'louder' on
either the left or the right side. Typically in a [DAW](https://en.wikipedia.org/wiki/Digital_audio_workstation) this would be represented by an 'automation
track' between the value of -1 to 1. 

The program to apply a pan will take three parameters:

- input file
- output file
- pan (-1 to 1)

For the input file we will restrict this to mono files, and for the output files we will always
generate a stereo file. The pan variable should be between -1 (left) and 1 (right). Before we can
start applying our pan, we need to read the raw audio data from an input wave file. Remember that to
read the wave file we will use the [GoAudio](https://github.com/DylanMeeus/GoAudio) library we made
earlier:

```go
import (
        wav "github.com/DylanMeeus/GoAudio/wave"
)
```

The set up for this program is rather simple, we will use the build-in `flags` package to parse the
input from the CLI.

```go
var (
	input  = flag.String("i", "", "input file")
	output = flag.String("o", "", "output file")
	pan    = flag.Float64("p", 0.0, "pan in range of -1 (left) to 1 (right)")
)
```

Once we have our flags set up, we can parse them and read the input file. 

```go
func main() {
	flag.Parse()
	infile := *input
	outfile := *output
	panfac := *pan
	wave, err := wav.ReadWaveFile(infile)
	if err != nil {
		panic("Could not parse wave file")
	}
        ...
}
```

So far so good. We have parsed the input so we know which value to use for our pan, and we have read
the raw audio data as well. But how do we go from a value in the range of (-1) to (1) to an actual
change in loudness on the left or right-side? We can imagine that a simple function would look like
this: 

```go
type panposition struct {
	left, right float64
}

func calculatePosition(position float64) panposition {
	position *= 0.5
	return panposition{
		left:  position - 0.5,
		right: position + 0.5,
	}
}
```

Here we are using a struct that can represent the amplitude on a scale of 0 to 1 for both the left
and right channel. Such that we observe the following values:

|position|left-channel|right-channel|
|--------|------------|-------------|
|0|0.5|0.5|
|1|0|1|
|-1|1|0|

In other words, if the position is zero the sound is perfectly balanced between the left and
right-side of your headphones. And in the extreme values, the sound is either only left-sided or
right-sided.

Just like in the previous post, we actually need to alter the frames based on the position data we
found in the `calculatePosition` function. We can create a function that modifies the frames based
on the `panposition` returned in the previous function.

```go
func applyPan(frames []wav.Frame, p panposition) []wav.Frame {
	out := []wav.Frame{}
	for _, s := range frames {
		out = append(out, wav.Frame(float64(s)*p.left))
		out = append(out, wav.Frame(float64(s)*p.right))
	}
	return out
}
```

Notice how for each `frame` we actually append two `frames` to the resulting slice! That is how we
are interleaving the left and right audio channel.

Now we can finish up the main method:

```go
        ...
	pos := calculatePosition(panfac)
	scaledFrames := applyPan(wave.Frames, calculatePosition(panfac))
	wave.NumChannels = 2 // samples are now stereo, so we need dual channels
	if err := wav.WriteFrames(scaledFrames, wave.WaveFmt, outfile); err != nil {
		panic(err)
	}
```

A crucial step here is that before writing the samples we have set ran `wave.NumChannels=2`. Without
this, the wave file would be interpreted as a mono sound file and our panning effect would have been
lost. 

# Testing the code

To test this, I find it easy to use an input file without a lot of things going on. I'm mainly using
this simple [mono file](/audio/part4/mono.wav).

If we run `go run main.go -i mono.wav -o left-side.wav -p -1` we get:

[left-side.wav](/audio/part4/left-side.wav)

And when we  run `go run main.go -i mono.wav -o right-side.wav -p 1` we get:

[right-side.wav](/audio/part4/right-side.wav)

# Next steps?

There is actually a flaw with this panning function that we are using. However it is not apparent to
us yet because we can only set a pan for an entire audio source. To see why this panning function is
not perfect we need to first introduce breakpoints as a way to create automation tracks, so the focus for our next few posts will be
breakpoints. :-)

-------

# Resources

- [GoAudio](https://github.com/DylanMeeus/GoAudio)
- [Panning code](https://github.com/DylanMeeus/GoAudio/blob/master/examples/stereopan/main.go)

------

If you liked this and want to know when I write new posts, the best way to keep up to date is by [following me on
twitter](https://twitter.com/DylanMeeus). ;-)
