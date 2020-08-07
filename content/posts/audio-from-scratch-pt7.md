---
title: "Audio From Scratch With Go: Extracting Breakpoints from songs"
date: 2020-08-08T01:01:37+02:00
lastmod: 2020-08-08T01:01:37+02:00
tags : [ "audio", "go", "GoAudio" ]
categories : [ "posts" ]
type:  "posts"
highlight: false
draft: true
images: ["/audio/part6/constantpower.JPG"]
---

So far everything we've done with breakpoints involved us creating a breakpoint file and using this
to automate part of a track. Now we'll take a look at how we can take an existing track and extract
some breakpoints from this. For this post, we'll take a look at extracting the amplitudes from the
.wave files, as this is one of the most straightforward properties that we can extract.

There is nothing here that we've not seen in the [previous
posts](https://dylanmeeus.github.io/tags/goaudio/), but rather we are going to combine what we've
already learned to create a new tool to do this. 

In a high level overview, we'll have to do this:

- iterate over our frames
- record the given amplitude (frame value)
- write to breakpoint file

In essence this would be simple enough, but we'll make two small modifications to this 
algorithm. First of all, we don't want to just generate a breakpoint for each frame, this would just
result in a list that is equal to our frame data. We'll use less space by just taking a snapshot at
a certain interval, e.g every 10ms, and take advantage of
our linear interpolation that happens when looking up the value of a breakpoint at a certain time. 

A small extention to our current breakpoint code is that we need to be able to 'batch' our frames
into slices of a given time. 

# Batching frames

The BatchFrames function will take a `Wave` and `seconds float64` as input, as this gives us enough
data to batch the frames. Given a certain SampleRate, we know how many Samples per Second we are
seeing in the file. With this information, we can find the amount of Frames per Seconds. (this holds
for mono files, for non-mono files we have to adjust for the frames -> samples conversion.)

The SampleSize can thus be expressed as follows: `SampleSize = SampleRate * seconds`

When we know our sample size, we can split the raw frames into slices of this size.

```go
func BatchFrames(data Wave, seconds float64) [][]Frame {
	if seconds == 0 {
		return [][]Frame{
			data.Frames,
		}
	}

	samples := data.Frames

	sampleSize := int(float64(data.SampleRate) * float64(seconds))

	batches := len(samples) / sampleSize
	if len(samples)%sampleSize != 0 {
		batches++
	}

	batched := make([][]Frame, batches) // this should be round up..
	for i := 0; i < len(batched); i++ {
		start := i * sampleSize
		if start > len(samples) {
			return batched
		}
		maxTake := i*sampleSize + sampleSize
		if maxTake >= len(samples)-1 {
			maxTake = len(samples)
		}
		subs := samples[start:maxTake]
		batched[i] = subs
	}
	return batched
}
```

# Extracting data from batches

Once we can split our frames into batches, we can call `BatchFrames(wave,x)` to get the requested
batches of a given duration. Then, we can find the max amplitude over all of these and keep
track of this over all batches.


The setup code is the same as usual, where we parse an input file with
[GoAudio](https://github.com/DylanMeeus/GoAudio). Except that now we'll also send the frames to the
'BatchFrames' function. (Error handling ignored for brevity)


```go
func main() {
	flag.Parse()
	infile := *input
	outfile := *output
	wave, _ := wav.ReadWaveFile(infile)

	if wave.NumChannels != 1 {
		//panic("Only mono soundfiles are supported for now")
	}

        frameDuration := 15.0 // 15 ms
	ticks := frameDuration / 1000.0
	batches := wav.BatchFrames(wave, ticks)
        ...
```

After doing this, we'll have our frames batched in 15 ms slices. We'll continue by iterating over
them and collecting the max amplitude found in each. As we'll need to write this to an output file
in the end, we'll store this in a StringBuilder for now.

One more thing we have to keep track of is which time will be inserted in the `time:value` pair for
the breakpoint file. This time value will be a 15ms increment for each batch.

We continue the main function:
```go
        ...
	strout := strings.Builder{}
	elapsed := 0.0
	for _, b := range batches {
		maxa := maxAmp(b)
		es := strconv.FormatFloat(elapsed, 'f', 8, 64)
		fs := strconv.FormatFloat(maxa, 'f', 8, 64)
		strout.WriteString(es + ":" + fs + "\n")
		elapsed += ticks
	}
	ioutil.WriteFile(outfile, []byte(strout.String()), 0644)
}
```

Finally all that is left is to fill our the `maxAmp` function by iterating over each frame in the
slice and returning the maximum amp.

```go
func maxAmp(ss []wav.Frame) float64 {
	if len(ss) == 0 {
		return 0
	}
	max := -1.0 // because they are in range -1 .. 1
	for _, a := range ss {
		if float64(a) > max {
			max = float64(a)
		}
	}
	return float64(max)
}
```

# Resources

- [GoAudio](https://github.com/DylanMeeus/GoAudio)
- [Breakpoint code](https://github.com/DylanMeeus/GoAudio/blob/master/breakpoint/breakpoint.go)

------

If you liked this and want to know when I write new posts, the best way to keep up to date is by [following me on
twitter](https://twitter.com/DylanMeeus).
