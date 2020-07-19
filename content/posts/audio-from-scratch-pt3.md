---
title: "Audio From Scratch: Part3, changing the amplitude"
date: 2020-07-18T19:15:32+02:00
lastmod: 2020-07-18T19:15:32+02:00
tags : [ "audio", "go" ]
categories : [ "posts" ]
type:  "posts"
highlight: false
draft: false
---

In the [previous post](https://dylanmeeus.github.io/posts/audio-from-scratch-pt2/) we have written code to read and write WAVE files. 
So now it's time to start using this functionality to actually manipulate some sound. The goal of
this post is simple, we want to change the amplitude of a given .wave file.

For this, I will import the library we wrote in [Part 2](https://dylanmeeus.github.io/posts/audio-from-scratch-pt2/).

The code for this post is also on
[Github](https://github.com/DylanMeeus/GoAudio/tree/master/examples/amplitude).


# Changing amplitudes

The program to change the amplitude will require three inputs:

- input file: .wave input
- output file: .wave output
- ampfac: factor by which we scale the amplitude

For parsing these arguments we will use the build-in `flags` package. 

```go
var (
	input  = flag.String("i", "", "input file")
	output = flag.String("o", "", "output file")
	amp    = flag.Float64("a", 1.0, "amp mod factor")
)

```

Next we want to parse these values, and read the audio data from the input file. 

```go
func main() {
	flag.Parse()
	infile := *input
	outfile := *output
	scale := *amp
	wave, err := pkg.ReadWaveFile(infile)
	if err != nil {
		panic("Could not parse wave file")
	}
        ...
}
```

So now how do we go about actually changing the amplitude of the audio file we just read?

Well, inside the audio file we have raw audio data (of type `Sample = float64`). These float64
sample values represent the amplitudes at different points in time. So in order to manipulate the
amplitude we have to manipulate these values. 

We  can fill out the main method like so: 

```go
	scaledSamples := changeAmplitude(wave.Samples, scale)
	if err := pkg.WriteSamples(scaledSamples, wave.WaveFmt, outfile); err != nil {
		panic(err)
	}
	fmt.Println("done")

}
```

Here we have just called a function "changeAmplitude" that requires us to pass Samples and a scale
factor, and returns us new samples. 

As mentioned, we can just alter the samples themselves to change the amplitudes. 

```go
func changeAmplitude(samples []pkg.Sample, scalefactor float64) []pkg.Sample {
	for i, s := range samples {
		samples[i] = pkg.Sample(float64(s) * scalefactor)
	}
	return samples
}
```

And that's all there is to it. Given a scale factor that the user passes, we multiple each sample by
this factor to get a new sample. At the end, we return our new samples and write them to the output
file. The actual writing of these samples to a wave file is again taken care of by our
[GoAudio library](https://github.com/DylanMeeus/GoAudio). 

# Running the code

We are now ready to run the code, we can pass an input file, name an output file, and a scale
factor to change the audio, for example to double the amplitudes of a sound file we would use the
following command:

```
go run main.go -i sound.wav -o out.wav -a 2
```

Which results in this: 

[original](/audio/maybe-next-time.wav)
[doubled](/audio/double.wav)

This is quite faint, so here is the original source multiplied by 5:

[x5](/audio/five.wav)

Distortion also kicked in here. :-) 

-------

If you liked this and want to know when I write new posts, the best way to keep up to date is by [following me on
twitter](https://twitter.com/DylanMeeus). ;-)
