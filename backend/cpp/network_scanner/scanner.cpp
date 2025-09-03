#include <boost/asio.hpp>
#include <boost/beast/core.hpp>
#include <boost/beast/http.hpp>
#include <boost/property_tree/ptree.hpp>
#include <boost/property_tree/json_parser.hpp>
#include <iostream>
#include <vector>
#include <thread>
#include <mutex>

namespace http = boost::beast::http;
namespace asio = boost::asio;
using tcp = asio::ip::tcp;

class NetworkScanner {
private:
    struct PortInfo {
        int port;
        bool is_open;
        std::string service;
    };

    std::mutex results_mutex;
    std::vector<PortInfo> scan_results;

    bool scan_port(const std::string& host, int port) {
        try {
            asio::io_context io_context;
            tcp::socket socket(io_context);
            tcp::resolver resolver(io_context);
            tcp::resolver::query query(host, std::to_string(port));
            
            asio::connect(socket, resolver.resolve(query));
            return socket.is_open();
        } catch (...) {
            return false;
        }
    }

    std::string get_service_name(int port) {
        static const std::map<int, std::string> services = {
            {80, "HTTP"},
            {443, "HTTPS"},
            {22, "SSH"},
            {21, "FTP"},
            {25, "SMTP"},
            {3306, "MySQL"},
            {5432, "PostgreSQL"}
        };
        
        auto it = services.find(port);
        return it != services.end() ? it->second : "Unknown";
    }

public:
    void scan_host(const std::string& host) {
        std::vector<std::thread> threads;
        std::vector<int> ports = {80, 443, 22, 21, 25, 3306, 5432};

        for (int port : ports) {
            threads.emplace_back([this, host, port]() {
                bool is_open = scan_port(host, port);
                std::lock_guard<std::mutex> lock(results_mutex);
                scan_results.push_back({port, is_open, get_service_name(port)});
            });
        }

        for (auto& thread : threads) {
            thread.join();
        }
    }

    std::string get_results_json() {
        boost::property_tree::ptree root;
        boost::property_tree::ptree results_array;

        for (const auto& result : scan_results) {
            boost::property_tree::ptree result_node;
            result_node.put("port", result.port);
            result_node.put("open", result.is_open);
            result_node.put("service", result.service);
            results_array.push_back(std::make_pair("", result_node));
        }

        root.add_child("results", results_array);

        std::stringstream ss;
        boost::property_tree::write_json(ss, root);
        return ss.str();
    }
};

int main() {
    try {
        asio::io_context ioc{1};
        tcp::acceptor acceptor{ioc, {{}, 8082}};
        
        while (true) {
            tcp::socket socket{ioc};
            acceptor.accept(socket);

            std::thread{[&socket]() {
                NetworkScanner scanner;
                
                boost::beast::flat_buffer buffer;
                http::request<http::string_body> req;
                http::read(socket, buffer, req);

                auto target = req.target().to_string();
                if (target.substr(0, 10) == "/api/scan?") {
                    std::string host = target.substr(10);
                    scanner.scan_host(host);

                    http::response<http::string_body> res{http::status::ok, req.version()};
                    res.set(http::field::server, "C++ Network Scanner");
                    res.set(http::field::content_type, "application/json");
                    res.body() = scanner.get_results_json();
                    res.prepare_payload();
                    http::write(socket, res);
                }
            }}.detach();
        }
    } catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << std::endl;
        return 1;
    }
    return 0;
}