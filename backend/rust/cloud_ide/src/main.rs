use actix_web::{web, App, HttpServer, HttpResponse};
use serde::{Deserialize, Serialize};
use tokio::fs;
use std::path::PathBuf;
use uuid::Uuid;

#[derive(Debug, Serialize, Deserialize)]
struct File {
    name: String,
    language: String,
    content: String,
}

#[derive(Debug, Serialize, Deserialize)]
struct CompileRequest {
    code: String,
    language: String,
}

#[derive(Debug, Serialize, Deserialize)]
struct CompileResponse {
    success: bool,
    output: String,
    error: Option<String>,
}

async fn save_file(file: web::Json<File>) -> HttpResponse {
    let file_id = Uuid::new_v4();
    let file_path = PathBuf::from("files").join(file_id.to_string());

    if let Err(e) = fs::write(&file_path, &file.content).await {
        return HttpResponse::InternalServerError().json(serde_json::json!({
            "error": format!("Failed to save file: {}", e)
        }));
    }

    HttpResponse::Ok().json(serde_json::json!({
        "id": file_id.to_string(),
        "message": "File saved successfully"
    }))
}

async fn compile_code(req: web::Json<CompileRequest>) -> HttpResponse {
    let result = match req.language.as_str() {
        "rust" => compile_rust(&req.code).await,
        "cpp" => compile_cpp(&req.code).await,
        "python" => run_python(&req.code).await,
        "julia" => run_julia(&req.code).await,
        _ => Err("Unsupported language".to_string()),
    };

    match result {
        Ok(output) => HttpResponse::Ok().json(CompileResponse {
            success: true,
            output,
            error: None,
        }),
        Err(e) => HttpResponse::Ok().json(CompileResponse {
            success: false,
            output: String::new(),
            error: Some(e),
        }),
    }
}

async fn compile_rust(code: &str) -> Result<String, String> {
    // Implementation for Rust compilation
    todo!()
}

async fn compile_cpp(code: &str) -> Result<String, String> {
    // Implementation for C++ compilation
    todo!()
}

async fn run_python(code: &str) -> Result<String, String> {
    // Implementation for Python execution
    todo!()
}

async fn run_julia(code: &str) -> Result<String, String> {
    // Implementation for Julia execution
    todo!()
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    HttpServer::new(|| {
        App::new()
            .route("/api/ide/save", web::post().to(save_file))
            .route("/api/ide/compile", web::post().to(compile_code))
    })
    .bind("127.0.0.1:8084")?
    .run()
    .await
}