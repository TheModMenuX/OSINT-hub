package main

import (
    "encoding/json"
    "net"
    "net/http"
    "time"
)

type PortScan struct {
    Port    int  `json:"port"`
    Open    bool `json:"open"`
    Service string `json:"service"`
}

func scanPort(host string, port int) PortScan {
    address := fmt.Sprintf("%s:%d", host, port)
    conn, err := net.DialTimeout("tcp", address, time.Second)
    
    if err != nil {
        return PortScan{Port: port, Open: false}
    }
    
    defer conn.Close()
    return PortScan{
        Port: port,
        Open: true,
        Service: getServiceName(port),
    }
}

func main() {
    http.HandleFunc("/api/scan", func(w http.ResponseWriter, r *http.Request) {
        target := r.URL.Query().Get("target")
        if target == "" {
            http.Error(w, "Target parameter required", http.StatusBadRequest)
            return
        }

        commonPorts := []int{80, 443, 22, 21, 25, 3306, 5432}
        results := make([]PortScan, 0)

        for _, port := range commonPorts {
            results = append(results, scanPort(target, port))
        }

        json.NewEncoder(w).Encode(results)
    })

    http.ListenAndServe(":8081", nil)
}