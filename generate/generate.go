package main

import (
	"encoding/json"
	"os"
	"time"

	"github.com/alexflint/go-arg"
)

type track struct {
	Scenario string
	Split    float64
	Spurious float64
}

type results struct {
	Tracks []track
}

func generate(n int, scenario string) *results {
	var r results
	for i := 0; i < n; i++ {
		t := track{Scenario: scenario}
		if i%2 > 0 {
			t.Split = 1.
		}
		if i%3 > 0 {
			t.Spurious = 1.
		}
		r.Tracks = append(r.Tracks, t)
	}
	return &r
}

func main() {
	var args struct {
		N        int
		Scenario string
	}
	args.N = 100
	args.Scenario = time.Now().String()
	arg.MustParse(&args)

	r := generate(args.N, args.Scenario)
	json.NewEncoder(os.Stdout).Encode(r)
}
