#!/bin/bash

# OSINT Hub System Monitor
# Current User: mgthi555-ai
# Timestamp: 2025-09-03 11:14:51

# Configuration
LOG_DIR="/var/log/osint-hub"
ALERT_THRESHOLD=90
CURRENT_USER="mgthi555-ai"
TIMESTAMP="2025-09-03 11:14:51"

# Create log directory if it doesn't exist
mkdir -p "$LOG_DIR"

# Initialize log file
LOG_FILE="$LOG_DIR/system_monitor_$(date +%Y%m%d).log"
touch "$LOG_FILE"

# Function to log messages
log_message() {
    local level="$1"
    local message="$2"
    echo "[$TIMESTAMP] [$level] [$CURRENT_USER] $message" >> "$LOG_FILE"
}

# Function to check system resources
check_resources() {
    # CPU Usage
    cpu_usage=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d. -f1)
    if [ "$cpu_usage" -gt "$ALERT_THRESHOLD" ]; then
        log_message "ALERT" "High CPU usage detected: ${cpu_usage}%"
        
        # Collect process information
        top -bn1 > "$LOG_DIR/high_cpu_processes_$(date +%s).txt"
    fi
    
    # Memory Usage
    memory_usage=$(free | grep Mem | awk '{print $3/$2 * 100.0}' | cut -d. -f1)
    if [ "$memory_usage" -gt "$ALERT_THRESHOLD" ]; then
        log_message "ALERT" "High memory usage detected: ${memory_usage}%"
        
        # Collect memory information
        free -m > "$LOG_DIR/memory_status_$(date +%s).txt"
    fi
    
    # Disk Usage
    disk_usage=$(df -h | awk '$NF=="/"{print $5}' | sed 's/%//g')
    if [ "$disk_usage" -gt "$ALERT_THRESHOLD" ]; then
        log_message "ALERT" "High disk usage detected: ${disk_usage}%"
        
        # Collect disk information
        df -h > "$LOG_DIR/disk_status_$(date +%s).txt"
    fi
}

# Function to monitor network connections
monitor_network() {
    # Check for suspicious connections
    netstat -tuna | while read line; do
        if echo "$line" | grep -q "ESTABLISHED"; then
            remote_ip=$(echo "$line" | awk '{print $5}' | cut -d: -f1)
            
            # Check against known malicious IPs
            if grep -q "$remote_ip" "$LOG_DIR/blacklist.txt"; then
                log_message "CRITICAL" "Suspicious connection detected to $remote_ip"
                
                # Collect connection details
                netstat -tuna > "$LOG_DIR/suspicious_connections_$(date +%s).txt"
            fi
        fi
    done
}

# Function to scan for vulnerabilities
scan_vulnerabilities() {
    # Check for outdated packages
    if command -v apt &> /dev/null; then
        apt list --upgradable 2>/dev/null | while read package; do
            if [ ! -z "$package" ]; then
                log_message "WARNING" "Outdated package found: $package"
            fi
        done
    fi
    
    # Check for open ports
    nmap -F localhost | while read line; do
        if echo "$line" | grep -q "open"; then
            log_message "INFO" "Open port detected: $line"
        fi
    done
}

# Main monitoring loop
while true; do
    # Update timestamp
    TIMESTAMP=$(date -u +"%Y-%m-%d %H:%M:%S")
    
    # Run checks
    check_resources
    monitor_network
    scan_vulnerabilities
    
    # Generate status report
    {
        echo "=== OSINT Hub System Status Report ==="
        echo "Timestamp: $TIMESTAMP"
        echo "User: $CURRENT_USER"
        echo "---"
        echo "CPU Usage: ${cpu_usage}%"
        echo "Memory Usage: ${memory_usage}%"
        echo "Disk Usage: ${disk_usage}%"
        echo "---"
        echo "Active Connections: $(netstat -tuna | grep ESTABLISHED | wc -l)"
        echo "Open Ports: $(netstat -tuna | grep LISTEN | wc -l)"
        echo "====================================="
    } > "$LOG_DIR/status_report_latest.txt"
    
    # Sleep for 5 minutes
    sleep 300
done