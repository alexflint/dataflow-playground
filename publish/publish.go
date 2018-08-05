package main

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"os"
	"time"

	"cloud.google.com/go/pubsub"
	arg "github.com/alexflint/go-arg"
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
	ctx := context.Background()

	var args struct {
		Project        string
		Topic          string
		NumTracks      int
		ScenarioPrefix string
		Interval       time.Duration
		N              int
	}
	args.Project = "alex-bigquery"
	args.Topic = "sim-results"
	args.NumTracks = 20
	args.ScenarioPrefix = "pubsub-scenario-" + time.Now().Format("15:04:05")
	args.Interval = time.Second
	args.N = 10
	arg.MustParse(&args)

	fmt.Printf("publishing %d messages for scenario %q...\n", args.N, args.ScenarioPrefix)

	client, err := pubsub.NewClient(ctx, args.Project)
	if err != nil {
		fmt.Printf("Could not create pubsub client: %v\n", err)
		os.Exit(1)
	}

	topic := client.Topic(args.Topic)
	for i := 0; i < args.N; i++ {
		fmt.Printf("publishing message %d of %d...", i+1, args.N)

		dataset := generate(args.NumTracks, args.ScenarioPrefix+fmt.Sprintf("--%d", i))
		buf, err := json.Marshal(dataset)
		if err != nil {
			fmt.Println(err)
			os.Exit(1)
		}

		result := topic.Publish(ctx, &pubsub.Message{
			Data: buf,
		})

		// Block until the result is returned and a server-generated
		// ID is returned for the published message.
		id, err := result.Get(ctx)
		if err != nil {
			log.Fatal(err)
		}

		fmt.Printf("published a message; msg ID: %v\n", id)
		time.Sleep(args.Interval)
	}

	fmt.Println("done")
}
