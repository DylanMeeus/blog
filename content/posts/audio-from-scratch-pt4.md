---
title: "Audio From Scratch: Part4, stereo panning"
date: 2020-07-20T19:15:32+02:00
lastmod: 2020-07-20T19:15:32+02:00
tags : [ "audio", "go" ]
categories : [ "posts" ]
type:  "posts"
highlight: false
draft: true
---

In the [previous post](https://dylanmeeus.github.io/posts/audio-from-scratch-pt2/) we have written code to read and write WAVE files. 
So now it's time to start using this functionality to actually manipulate some sound. In this post
the objective will be to get the audio to be panned (left or right). After a pan has been applied to
an audio signal, you will hear it play more from the left or right speaker. 

If you just want to focus on the audio manipulation and not on the file handling, you can use the
library created in the last post from github:
[github.com/DylanMeeus/GoAudio](https://github.com/DylanMeeus/GoAudio). Which is how we will be
importing it in this post as well. 


# Panning

The program to apply a pan will take three parameters:

- input file
- output file
- pan (-1 to 1)

For the input file we will restrict this to mono files, and for the output files we will always
generate a stereo file. The pan variable should be between -1 (left) and 1 (right). Before we can
start applying our pan, we need to read the raw audio data from an input wave file. Remember that to
read the wave file we will use the library from the previous post:

```
import (
        wav "github.com/DylanMeeus/GoAudio/wave"
)
```

The set up for this program is rather simple, we will use the build-in `flags` package to parse the
input from the CLI.

```
var (
	input  = flag.String("i", "", "input file")
	output = flag.String("o", "", "output file")
	pan    = flag.Float64("p", 0.0, "pan in range of -1 (left) to 1 (right)")
)
```

Once we have our flags set up, we can parse them and read the input file. 

```
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
the raw audio data as well. But how do we go from a value in the range of (-1) to (1)?
