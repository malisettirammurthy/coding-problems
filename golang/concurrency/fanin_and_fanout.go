package main

import (
	"fmt"
	"sync"
	"time"
)

// Generator produces numbers into a channel (fan-out source)
func generateNumbers(count int) <-chan int {
	out := make(chan int)
	go func() {
		defer close(out)
		for i := 1; i <= count; i++ {
			out <- i
		}
	}()
	return out
}

// Worker processes a number (simulates work)
func worker(in <-chan int, workerID int) <-chan int {
	out := make(chan int)
	go func() {
		defer close(out)
		for n := range in {
			fmt.Printf("Worker %d processing %d\n", workerID, n)
			time.Sleep(100 * time.Millisecond) // Simulate work
			out <- n * 2                       // Double the number
		}
	}()
	return out
}

// Merge combines results from multiple channels (fan-in)
func merge(cs ...<-chan int) <-chan int {
	var wg sync.WaitGroup
	out := make(chan int)

	output := func(c <-chan int) {
		defer wg.Done()
		for n := range c {
			out <- n
		}
	}

	wg.Add(len(cs))
	for _, c := range cs {
		go output(c)
	}

	go func() {
		wg.Wait()
		close(out)
	}()
	return out
}

func main() {
	// Fan-out: Generate numbers and distribute to multiple workers
	in := generateNumbers(5)

	c1 := worker(in, 1)
	c2 := worker(in, 2)
	c3 := worker(in, 3)

	// Fan-in: Merge results from workers
	for result := range merge(c1, c2, c3) {
		fmt.Printf("Received result: %d\n", result)
	}

	fmt.Println("Done!")
}
