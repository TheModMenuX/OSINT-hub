use actix_web::{web, App, HttpServer, Result};
use serde::{Deserialize, Serialize};
use std::process::Command;
use std::time::Duration;
use tokio::time::timeout;
use uuid::Uuid;
use std::fs;

#[derive(Deserialize)]
struct CodeRequest {
    code: String,
    language: String,
}

#[derive(Serialize)]
struct CodeResponse {
    output: String,
    execution_time: f64,
}

async fn run_code(req: web::Json<CodeRequest>) -> Result<web::Json<CodeResponse>> {
    let temp_dir = format!("/tmp/cloud_ide_{}", Uuid::new_v4());
    fs::create_dir(&temp_dir)?;

    let (file_name, run_cmd) = match req.language.as_str() {
        "python" => ("main.py", vec!["python", "main.py"]),
        "rust" => ("main.rs", vec!["rustc", "main.rs", "-o", "main", "./main"]),
        "cpp" => ("main.cpp", vec!["g++", "main.cpp", "-o", "main", "./main"]),
        "julia" => ("main.jl", vec!["julia", "main.jl"]),
        _ => return Ok(web::Json(CodeResponse {
            output: "Unsupported language".to_string(),
            execution_time: 0.0,
        })),
    };

    let file_path = format!("{}/{}", temp_dir, file_name);
    fs::write(&file_path, &req.code)?;

    let start_time = std::time::Instant::now();
    
    let output = timeout(Duration::from_secs(10), async {
        Command::new(run_cmd[0])
            .args(&run_cmd[1..])
            .current_dir(&temp_dir)
            .output()
    }).await;

    fs::remove_dir_all(temp_dir)?;

    match output {
        Ok(Ok(output)) => {
            let execution_time = start_time.elapsed().as_secs_f64();
            let stdout = String::from_utf8_lossy(&output.stdout);
            let stderr = String::from_utf8_lossy(&output.stderr);
            
            Ok(web::Json(CodeResponse {
                output: format!("Output:\n{}\nErrors:\n{}", stdout, stderr),
                execution_time,
            }))
        },
        _ => Ok(web::Json(CodeResponse {
            output: "Execution timed out or failed".to_string(),
            execution_time: 10.0,
        })),
    }
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    HttpServer::new(|| {
        App::new()
            .service(web::resource("/api/run-code")
                .route(web::post().to(run_code)))
    })
    .bind("127.0.0.1:8084")?
    .run()
    .await
}