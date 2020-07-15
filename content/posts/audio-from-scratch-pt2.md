---
title: "Audio From Scratch Part2: Anatomy of a wave (file)"
date: 2020-07-13T19:15:32+02:00
lastmod: 2020-07-13T19:15:32+02:00
tags : [ "audio", "go" ]
categories : [ "posts" ]
type:  "posts"
highlight: false
draft: false
---


In our [last post](https://dylanmeeus.github.io/posts/audio-from-scratch-pt1) we have looked at how we can
create a simple binary sound file. By creating a sine wave with exponential decay, we can get the
effect of a single note playing.

It's good to know what these types of files look like. In the real world however you'll usually
encounter files that are a bit more complex. One of the common formats to find audio in is the WAVE
file format, normally denoted with the extension `.wav` or `.wave`. 

In this post we will learn how to extract information from this file, and how to write our own audio
data to a wave file. This will form a base for future posts in which we can start manipulating this
audio data.

As usual, all code can be found on [GitHub](https://www.github.com/DylanMeeus/GoAudio), albeit in a
separate library this time. If you want to know how to manipulate the audio itself rather than
dealing with writing the files, the next blog post will do just that.

## What's in a wave? 

WAVE is the 'WaveForm Audio File Format', developed jointly by IBM and Microsoft in the early 90s. A
wave file stores audio data as samples (double precision) along with metadata describing what to
expect from the audio stream, such as the amount of channels (mono, stereo, surround..), the amount
of samples, etc.. 

Usually the encoding uses PCM, Pulse-Code Modulation. Whilst not immediately necessary
for understanding this blog, the code will refer to PCM in various places. For simplicity's sake
we're going to assume that every file is encoded like this.

## Anatomy

Let's break down the content of a wave file step by step. 

### Header

The first part of the wave file is a header. Viewed as HEX you will recognize this by the values
"RIFF" and "WAVE" that stand out. For example, this is the first line of my hex editor when I open
the hex output of a wave file:

```
00000000: 5249 4646 1028 0200 5741 5645 666d 7420  RIFF.(..WAVEfmt 
```

This single line tells us a few things that are useful. First, RIFF means it is written using
little-endian, otherwise it would have been RIFX. Secondly, the WAVE and fmt message tells us that
at least those parts of the files are generated correctly.

The wave header principally exists out of three components, a `chunkID`, a `chunk size` and a
`format`. The format should always be `WAVE` for our wave files. Below is a schematic representation
of the wave header with the byte offsets anotated, as well as the size in bits.

![](/audio/WaveHeader.png)

### Fmt

Apart from the header, the wave file exists of two subchunks. One is for metadata, it describes how
the audio data in our file is going to look like. The second subchunks contains the raw audio data
itself.

Below is a representation of this 'fmt' chunk:

![](/audio/WaveFmt.png)

(perhaps better to open this in a [new window](/audio/WaveFmt.png).

Briefly explained, it contains:

- Subchunk1ID: This should contain `fmt`.
- Subchunk1Size: Size of the fmt chunk
- AudioFormat: PCM usually, indicated by the value `1`
- NumChannels: 1 = mono, 2 = stereo, ..
- SampleRate: 44100, 48000, ..
- ByteRate: SampleRate * NumChannels * (BitsPerSample / 8)
- BitsPerSample: 8, 16, 32,...

### Data

The final part of the wave file contains our actual raw audio samples, as well as two extra fields.
The first field is the `Subchunk2ID`, this should contain the value `data`. And secondly the
`Subchunk2Size`, which is the byte-size of the data. Finally it also contains the raw audio data
samples.

![](/audio/WaveData.png)


# The code

## Wave Reader

The key parts of the code for reading and writing WAVE files are all about how to transform our bits
into actual data. We will either have to transform data to floats or to ints depending on the chunk
field. 

For writing a 4 byte piece to int we can use the following code:

```go
// turn a 32-bit byte array into an int
func bits32ToInt(b []byte) int {
	if len(b) != 4 {
		panic("Expected size 4!")
	}
	var payload uint32
	buf := bytes.NewReader(b)
	err := binary.Read(buf, binary.LittleEndian, &payload)
	if err != nil {
		panic(err)
	}
	return int(payload) // easier to work with ints
}
```

Next we can use this for floats as well.


```go
func bitsToFloat(b []byte) float64 {
	var bits uint64
	switch len(b) {
	case 2:
		bits = uint64(binary.LittleEndian.Uint16(b))
	case 4:
		bits = uint64(binary.LittleEndian.Uint32(b))
	case 8:
		bits = binary.LittleEndian.Uint64(b)
	default:
		panic("Can't parse to float..")
	}
	float := math.Float64frombits(bits)
	return float
}
```

Using these functions we can then combine those into an actual reader.

```go
func readHeader(b []byte) WaveHeader {
	hdr := WaveHeader{}
	chunkID := b[0:4]
	hdr.ChunkID = b[0:4]
	if string(hdr.ChunkID) != "RIFF" {
                // Validation of the header file
		panic("Invalid file")
	}

	chunkSize := b[4:8]
	var size uint32
	buf := bytes.NewReader(chunkSize)
	err := binary.Read(buf, binary.LittleEndian, &size)
	if err != nil {
		panic(err)
	}
	hdr.ChunkSize = int(size) // easier to work with ints

	format := b[8:12]
	if string(format) != "WAVE" {
		panic("Format should be WAVE")
	}
	hdr.Format = string(format)
	return hdr
}
```

Here we can see how we check for both the `RIFF` and `WAVE` content in the header to make sure that
these are present in the correct shape.

And perhaps more crucially, we need to read the raw audio data.

```go
// Should we do n-channel separation at this point?
func parseRawData(wfmt WaveFmt, rawdata []byte) []Sample {
	bytesSampleSize := wfmt.BitsPerSample / 8
	// TODO: sanity-check that this is a power of 2? I think only those sample sizes are
	// possible

	samples := []Sample{}
	// read the chunks
	for i := 0; i < len(rawdata); i += bytesSampleSize {
		rawSample := rawdata[i : i+bytesSampleSize]
		sample := bitsToFloat(rawSample)
		samples = append(samples, Sample(sample))
	}

	return samples
}
```


All chunks follow a similar pattern, and can all be found on
[GitHub](https://github.com/DylanMeeus/GoAudio)


## Writer

For writing, the key functions for reading are just reversed. We take an int or float and turn this
into a byte slice.


For writing our int32 to bytes: 
```go
func int32ToBytes(i int) []byte {
	b := make([]byte, 4)
	in := uint32(i)
	binary.LittleEndian.PutUint32(b, in)
	return b
}
```

And similarly we could write float64s:

```go
func floatToBytes(f float64, nBytes int) []byte {
	bits := math.Float64bits(f)
	bs := make([]byte, 8)
	binary.LittleEndian.PutUint64(bs, bits)
	// trim padding
	switch nBytes {
	case 2:
		return bs[:2]
	case 4:
		return bs[:4]
	}
	return bs
}
```

The most crucial part here is writing the raw audio samples, with these helper functions this would
look like:

```go
// Turn the samples into raw data...
func samplesToRawData(samples []Sample, props WaveFmt) []byte {
	raw := []byte{}
	for _, s := range samples {
		bits := floatToBytes(float64(s), props.BitsPerSample/8)
		raw = append(raw, bits...)
	}
	return raw
}
```

## What's next?

Now that we have this library, the next blogpost can dive into how we can use this to manipulate
.wave sound files.

-------

If you enjoyed this and want to know when I write new posts, consider [folling me on
twitter](https://twitter.com/DylanMeeus)
