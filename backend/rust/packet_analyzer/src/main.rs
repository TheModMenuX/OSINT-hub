use tokio;
use pcap::{Device, Capture};
use serde::{Serialize, Deserialize};
use warp::Filter;
use chrono::{DateTime, Utc};
use std::sync::Arc;
use tokio::sync::Mutex;
use std::collections::HashMap;

#[derive(Debug, Serialize, Deserialize, Clone)]
struct PacketInfo {
    timestamp: DateTime<Utc>,
    source_ip: String,
    dest_ip: String,
    protocol: String,
    length: u32,
}

#[derive(Clone)]
struct PacketStore {
    packets: Arc<Mutex<Vec<PacketInfo>>>,
    stats: Arc<Mutex<HashMap<String, u32>>>,
}

#[tokio::main]
async fn main() {
    let store = PacketStore {
        packets: Arc::new(Mutex::new(Vec::new())),
        stats: Arc::new(Mutex::new(HashMap::new())),
    };

    let store_filter = warp::any().map(move || store.clone());

    // API routes
    let capture = warp::path!("api" / "packets")
        .and(store_filter.clone())
        .map(|store: PacketStore| {
            warp::reply::json(&store.packets.lock().unwrap())
        });

    let stats = warp::path!("api" / "stats")
        .and(store_filter.clone())
        .map(|store: PacketStore| {
            warp::reply::json(&store.stats.lock().unwrap())
        });

    // Start packet capture in background
    let store_capture = store.clone();
    tokio::spawn(async move {
        if let Ok(device) = Device::lookup() {
            if let Ok(mut cap) = Capture::from_device(device).unwrap().promisc(true).open() {
                while let Ok(packet) = cap.next_packet() {
                    let packet_info = PacketInfo {
                        timestamp: Utc::now(),
                        source_ip: "127.0.0.1".to_string(), // Simplified for example
                        dest_ip: "127.0.0.1".to_string(),
                        protocol: "TCP".to_string(),
                        length: packet.header.len,
                    };

                    let mut packets = store_capture.packets.lock().unwrap();
                    packets.push(packet_info);
                }
            }
        }
    });

    warp::serve(capture.or(stats))
        .run(([127, 0, 0, 1], 3030))
        .await;
}