---
title: "Hasgo: how does it work?"
date: 2019-05-25T21:29:58+02:00
draft: false 
---

## What is Hasgo?

[Hasgo](https://www.github.com/DylanMeeus/hasgo") is a code generator that can be used to generate functions that work on slices.
We don't have generics in Go, which I think is a good thing, but we can generate code with `go:generate` to work on different types.

Hasgo does just this, we write functions and then say for which types we want to generate these functions.
For our Ints, the generation looks like this:

```go
//go:generate hasgo -T=int64 -S=Ints
type Ints []int64
```

This lets the generator know that our slice is called `Ints` but that the underlying type is `int64`. We could also have done this for
custom structs (and specify which package the generated code should belong to):

```go
//go:generate hasgo -T=person -S=persons -P=person
type persons []person
type person struct {
    firstname string
    lastname  string
    age       int
}
```

When the functions are generated, we can write code like this:
```go
func magic() {
	result := IntRange(-10,10).
		Abs().
		Map(func(i int64)int64{return i*i}).
		Filter(func(i int64)bool {return i % 2 == 0}).
		Sum()
```

This is enough of an idea of what it does to follow along, but if you're interested in what else it
can do, check it out on [github](https://www.github.com/DylanMeeus/hasgo).

## How does it work?

Before I start explaining this, let me start off by saying that this approach is not something I
thought of on my own. [Pie](https://www.github.com/elliotchance/pie) played a huge role in how I
eventually designed Hasgo. There are similarities in how Hasgo and Pie work, although they are not
identical.

Hasgo is actually a combination of two code generators. We write our functions in Go code, but these would get compiled and thus unusable.
We need the source code of those Go files to be able to generate the functions for our types. A typical source code file would look like this:

```go
package functions
func (s SliceType) Length() int {
    return len(s)
}
```

This we'd want to turn into the following code:
```go
func (s Ints) Length() int {
    return len(s)
}

func (s persons) Length() int {
    return len(s)
}
```

### A generator to power the generator

Hasgo actually has a first generator that just reads all files in the `/functions` directory and turns them into a `map[string]string`.
This is where most of the 'magic' happens. This generator only needs to be ran by people working on Hasgo and not by people using the library.

```go
var packageTemplate = template.Must(template.New("").
	Parse("// Code generated by go generate; DO NOT EDIT.\n" +
		"package main\n" +
		"\n" +
		"var hasgoTemplates = map[string]string{\n" +
		"{{ range $fn, $file := . }}" +
		"\t\"{{ $fn }}\": `{{ $file }}`,\n" +
		"{{ end }}" +
		"}\n"))

var domainTemplate = template.Must(template.New("").
	Parse("\n" +
		"const (\n ForNumbers = \"ForNumbers\"\nForStrings = \"ForStrings\"\n" +
		"ForStructs = \"ForStructs\"\n)\n" +
		"var funcDomains = map[string][]string{\n" +
		"{{ range $fn, $arr := . }}" +
		"\t\"{{ $fn }}\": []string{ {{ range $index, $dom := $arr }}" +
		" {{if $index}} ,{{end}} {{$dom}} {{end}} },\n" +
		"{{ end }}" +
"}\n"))
```

This is not my favourite piece of code in Hasgo, it's somewhat of a necessary evil.
There's a bit more to this code (albeit not much), which you can [view here](https://github.com/DylanMeeus/hasgo/blob/master/generator.go).

This step results in a `template.go` file which gets compiled and is accessible for our main generator in `hasgo.go`.

It looks somewhat like this:

```go
var hasgoTemplates = map[string]string{
	"Abs.go": `
import (
	"math"
)
func (s SliceType) Abs() (out SliceType) {
	for _, v := range s {
		out = append(out, ElementType(math.Abs(float64(v))))
	}
	return
}
`,
	"Filter.go": `
func (s SliceType) Filter(f func(ElementType) bool) (out SliceType) {
	for _, v := range s {
		if f(v) {
			out = append(out, v)
		}
	}
	return
}
// much more code...
```

### Which templates to generate?

Before our generator-generator knows what to generate, we need to register it in `functions/main.go`.
This is surprisingly simple, and allows us to not only specify which functions to include, but it also
allows us to say on which types of data our function can work.

```go
templates = map[string][]string{
		"Length.go": []string{ForNumbers, ForStrings, ForStructs},
		// more functions for great glory
}
```

### The main generator

Once we have our `template.go` generated, we can run `hasgo` and actually generate our functions.
It can be roughly summed up in these steps:

* Read function templates
* Figure out if function applies to our type (Number, String, Structs)
* Extract the imports from our template
* Replace the 'placeholders' with the correct Type / SliceType
* Combine all imports into one import statement
* Combine text and print to file

This is (luckily) pretty straightforward code, just take a look [at the source](https://github.com/DylanMeeus/hasgo/blob/master/hasgo.go). There's no magic going on (at the time of  writing this) and I'd like to
keep it magic-free. Less magic is better :smiley:

By now you should have some idea of how the generated code comes to be, so if you read this far you should be able to conceptually
understand what is going on under the hood. I might blog about the main generator, or some functions
later on. :)
