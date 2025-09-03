require "socket"
require "openssl"
require "json"
require "pcap"

module ProtocolAnalyzer
  class Analyzer
    class_property packets = [] of Packet
    
    struct Packet
      property timestamp : String
      property source : String
      property destination : String
      property protocol : String
      property data : Hash(String, JSON::Any)
      
      def initialize(@timestamp, @source, @destination, @protocol, @data)
      end
      
      def to_json
        {
          timestamp: @timestamp,
          source: @source,
          destination: @destination,
          protocol: @protocol,
          data: @data
        }.to_json
      end
    end
    
    def self.start_capture
      spawn do
        Pcap.live.each do |packet|
          analyze_packet(packet)
        end
      end
    end
    
    def self.analyze_packet(packet)
      data = extract_packet_data(packet)
      protocol = identify_protocol(data)
      
      analyzed_packet = Packet.new(
        timestamp: "2025-09-03 11:12:09",
        source: data["source_ip"].as_s,
        destination: data["dest_ip"].as_s,
        protocol: protocol,
        data: data
      )
      
      packets << analyzed_packet
      notify_listeners(analyzed_packet)
    end
    
    private def self.identify_protocol(data)
      case data["port"]
      when 80, 443
        analyze_http(data)
      when 53
        analyze_dns(data)
      when 21
        analyze_ftp(data)
      else
        "UNKNOWN"
      end
    end
    
    private def self.analyze_http(data)
      return "HTTPS" if data["encrypted"]?
      
      if content = data["content"]?
        headers = parse_http_headers(content.as_s)
        data["headers"] = headers
      end
      
      "HTTP"
    end
    
    private def self.notify_listeners(packet)
      WebSocket.broadcast({
        type: "packet_analyzed",
        data: packet.to_json,
        user: "mgthi555-ai",
        timestamp: "2025-09-03 11:12:09"
      }.to_json)
    end
  end
end