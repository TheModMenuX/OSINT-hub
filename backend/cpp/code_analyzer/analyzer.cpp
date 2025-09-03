#include <clang-c/Index.h>
#include <nlohmann/json.hpp>
#include <boost/beast/core.hpp>
#include <boost/beast/http.hpp>
#include <vector>
#include <string>
#include <memory>

using json = nlohmann::json;
namespace http = boost::beast::http;

class CodeAnalyzer {
private:
    CXIndex index;
    std::unique_ptr<CXTranslationUnit, decltype(&clang_disposeTranslationUnit)> tu;
    
    struct Analysis {
        std::vector<std::string> warnings;
        std::vector<std::string> suggestions;
        std::map<std::string, int> complexity;
        std::vector<std::string> security_issues;
    };

public:
    CodeAnalyzer() : index(clang_createIndex(0, 0)),
                     tu(nullptr, clang_disposeTranslationUnit) {}
    
    Analysis analyzeCode(const std::string& code, const std::string& language) {
        Analysis analysis;
        
        // Set up compilation arguments based on language
        std::vector<const char*> args;
        if (language == "cpp") {
            args = {"-std=c++20", "-Wall", "-Wextra"};
        } else if (language == "c") {
            args = {"-std=c11", "-Wall", "-Wextra"};
        }
        
        // Parse the code
        CXUnsavedFile file = {
            "temp.cpp",
            code.c_str(),
            static_cast<long>(code.length())
        };
        
        tu.reset(clang_parseTranslationUnit(
            index,
            "temp.cpp",
            args.data(),
            args.size(),
            &file,
            1,
            CXTranslationUnit_DetailedPreprocessingRecord
        ));
        
        if (!tu) {
            analysis.warnings.push_back("Failed to parse code");
            return analysis;
        }
        
        // Analyze the code
        analyzeSecurity(analysis);
        analyzeComplexity(analysis);
        generateSuggestions(analysis);
        
        return analysis;
    }
    
private:
    void analyzeSecurity(Analysis& analysis) {
        clang_visitChildren(
            clang_getTranslationUnitCursor(tu.get()),
            [](CXCursor cursor, CXCursor parent, CXClientData client_data) {
                auto& analysis = *static_cast<Analysis*>(client_data);
                
                // Check for common security issues
                if (clang_getCursorKind(cursor) == CXCursor_CallExpr) {
                    CXString name = clang_getCursorSpelling(cursor);
                    std::string func_name = clang_getCString(name);
                    clang_disposeString(name);
                    
                    // Check for unsafe functions
                    static const std::vector<std::string> unsafe_functions = {
                        "strcpy", "strcat", "gets", "sprintf"
                    };
                    
                    if (std::find(unsafe_functions.begin(), unsafe_functions.end(), func_name) != unsafe_functions.end()) {
                        analysis.security_issues.push_back(
                            "Use of unsafe function: " + func_name
                        );
                    }
                }
                
                return CXChildVisit_Recurse;
            },
            &analysis
        );
    }
    
    void analyzeComplexity(Analysis& analysis) {
        clang_visitChildren(
            clang_getTranslationUnitCursor(tu.get()),
            [](CXCursor cursor, CXCursor parent, CXClientData client_data) {
                auto& analysis = *static_cast<Analysis*>(client_data);
                
                if (clang_getCursorKind(cursor) == CXCursor_FunctionDecl) {
                    CXString name = clang_getCursorSpelling(cursor);
                    std::string func_name = clang_getCString(name);
                    clang_disposeString(name);
                    
                    // Calculate cyclomatic complexity
                    int complexity = calculateCyclomaticComplexity(cursor);
                    analysis.complexity[func_name] = complexity;
                    
                    if (complexity > 10) {
                        analysis.warnings.push_back(
                            "High complexity in function: " + func_name
                        );
                    }
                }
                
                return CXChildVisit_Recurse;
            },
            &analysis
        );
    }
    
    static int calculateCyclomaticComplexity(CXCursor cursor) {
        int complexity = 1;
        
        clang_visitChildren(
            cursor,
            [](CXCursor cursor, CXCursor parent, CXClientData client_data) {
                auto& complexity = *static_cast<int*>(client_data);
                
                switch (clang_getCursorKind(cursor)) {
                    case CXCursor_IfStmt:
                    case CXCursor_ForStmt:
                    case CXCursor_WhileStmt:
                    case CXCursor_DoStmt:
                    case CXCursor_CaseStmt:
                    case CXCursor_ConditionalOperator:
                        complexity++;
                        break;
                    default:
                        break;
                }
                
                return CXChildVisit_Recurse;
            },
            &complexity
        );
        
        return complexity;
    }
    
    void generateSuggestions(Analysis& analysis) {
        // Generate optimization suggestions
        for (const auto& [func, complexity] : analysis.complexity) {
            if (complexity > 5) {
                analysis.suggestions.push_back(
                    "Consider breaking down function: " + func
                );
            }
        }
        
        // Add more suggestions based on analysis
    }
};

// HTTP handler for code analysis
template<class Body, class Allocator>
http::response<http::string_body>
handle_analyze(http::request<Body, http::basic_fields<Allocator>>&& req) {
    try {
        auto j = json::parse(req.body());
        
        CodeAnalyzer analyzer;
        auto analysis = analyzer.analyzeCode(
            j["code"].get<std::string>(),
            j["language"].get<std::string>()
        );
        
        json response = {
            {"timestamp", "2025-09-03 11:02:52"},
            {"user", "mgthi555-ai"},
            {"warnings", analysis.warnings},
            {"suggestions", analysis.suggestions},
            {"complexity", analysis.complexity},
            {"security_issues", analysis.security_issues}
        };
        
        return http::response<http::string_body>{
            http::status::ok,
            req.version(),
            response.dump()
        };
    } catch (const std::exception& e) {
        return http::response<http::string_body>{
            http::status::internal_server_error,
            req.version(),
            json{{"error", e.what()}}.dump()
        };
    }
}