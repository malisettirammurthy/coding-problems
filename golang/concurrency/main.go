package main

import (
	"fmt"
	"math/rand"
	"sync"
	"time"
)

// Order processing example in Go for concurrency demonstration

type Order struct {
	ID     int
	Status string
	mu     sync.Mutex
}

var (
	totalUpdates int
	updateMutex  sync.Mutex
)

func main() {
	// var wg sync.WaitGroup
	wg := sync.WaitGroup{}
	wg.Add(3)

	orders := generateOrders(20)

	// go func() {
	// 	defer wg.Done()
	// 	processOrders(orders)
	// }()

	for i := 0; i < 3; i++ {
		go func() {
			defer wg.Done()
			for _, order := range orders {
				updateOrderStatus(order)
			}
		}()
	}

	wg.Wait()
	reportOrderStatus(orders)
	fmt.Println("All operations completed. Exiting.")
	fmt.Printf("Total Updates: %d\n", totalUpdates)
}

func updateOrderStatus(order *Order) {
	order.mu.Lock()
	time.Sleep(
		time.Duration(rand.Intn(300)) *
			time.Millisecond,
	)
	status := []string{
		"Processing", "Shipped", "Delivered",
	}[rand.Intn(3)]
	order.Status = status
	fmt.Printf(
		"Updated order %d status: %s\n",
		order.ID, status,
	)
	order.mu.Unlock()

	updateMutex.Lock()
	defer updateMutex.Unlock()

	currentUpdates := totalUpdates
	time.Sleep(5 * time.Millisecond)
	totalUpdates = currentUpdates + 1

}

func processOrders(orders []*Order) {
	for _, order := range orders {
		time.Sleep(
			time.Duration(rand.Intn(500)) *
				time.Millisecond,
		)
		fmt.Printf("Processing Order %d\n", order.ID)
	}
}

func generateOrders(count int) []*Order {
	orders := make([]*Order, count)
	for i := 0; i < count; i++ {
		orders[i] = &Order{ID: i + 1, Status: "Pending"}
	}
	return orders
}

func reportOrderStatus(orders []*Order) {
	fmt.Println("\n--- Order Status Report ---")
	for _, order := range orders {
		fmt.Printf(
			"Order %d: %s\n",
			order.ID, order.Status,
		)
	}
	fmt.Println("---------------------")
}
