use std::collections::HashMap;
use std::convert::Infallible;
use std::error::Error;
use std::io::{BufRead, BufReader, BufWriter, Read, Write};
use std::net::{SocketAddrV4, TcpListener, TcpStream};
use std::thread;

const HTTP_404_STRING: &'static [u8] =
    b"HTTP/1.1 404 Not Found\r\nConnection: Close\r\nServer: min-rhttpd 0.1\r\n\r\n404 Not Found";

pub type HttpUri = String;
pub type HttpHeaders = HashMap<String, String>;
pub type HttpParams = HashMap<String, String>;
pub type HttpBody = Option<String>;
pub type HttpResponse = Result<(String, String), String>;

pub type HttpHandlerFunc = Box<
    dyn Fn(HttpHeaders, HttpParams, HttpBody) -> HttpResponse
        + Send
        + Sync
        + 'static,
>;

pub struct MinHttpd {
    pub handlers: HashMap<HttpUri, HttpHandlerFunc>
}

impl MinHttpd {
    pub fn new() -> Self {
        Self {
            handlers: HashMap::new()
        }
    }

    pub fn route(&mut self, uri: HttpUri, handler: HttpHandlerFunc) {
        self.handlers.insert(uri, handler);
    }

    pub fn serve(&self, addr: SocketAddrV4) -> Result<Infallible, Box<dyn Error>> {
        let tcp_listener = TcpListener::bind(addr)?;
        loop {
            let (stream, addr) = tcp_listener.accept()?;
            eprintln!("[MIN-HTTPD] Accepted connection from: {}", addr);

            self.handle_connection(stream);
        }
    }

    fn handle_connection(&self, stream: TcpStream) {
        let unsafe_self = unsafe {
            std::mem::transmute::<&'_ Self, &'static Self>(&self)
        };

        thread::spawn(move || {
            match Self::handle_connection_impl(unsafe_self, stream) {
                Ok(_) => {},
                Err(e) => eprintln!("[MIN-HTTPD] Error: {}", e)
            }
        });
    }

    fn handle_connection_impl(&self, stream: TcpStream) -> Result<(), Box<dyn Error>>{
        let mut reader = BufReader::new(&stream);
        let mut writer = BufWriter::new(&stream);

        let mut line = String::new();
        reader.read_line(&mut line)?;

        let parts = line.trim().split_whitespace().collect::<Vec<_>>();
        if parts.len() != 3 {
            eprintln!("[MIN-HTTPD] Invalid HTTP request: {}", line);
            return Ok(());
        }
        let method = parts[0].to_lowercase();
        let version = parts[2].to_lowercase();

        if method != "get" && parts[0] != "post" {
            eprintln!("[MIN-HTTPD] Invalid HTTP method: {}", parts[0]);
            return Ok(());
        }
        if version != "http/1.1" && version != "http/1.0" {
            eprintln!("[MIN-HTTPD] Invalid HTTP version: {}", parts[2]);
            return Ok(());
        }

        let uri = parts[1].to_string();
        let uri_parts = uri.split("?").collect::<Vec<_>>();
        let uri = uri_parts[0].to_string();
        let params = if uri_parts.len() > 1 {
            let mut params = HashMap::new();
            for param in uri_parts[1].split("&") {
                let param_parts = param.split("=").collect::<Vec<_>>();
                if param_parts.len() != 2 {
                    eprintln!("[MIN-HTTPD] Invalid HTTP parameter: {}", param);
                    return Ok(());
                }
                params.insert(
                    param_parts[0].to_string(),
                    param_parts[1].to_string()
                );
            }
            params
        } else {
            HashMap::new()
        };

        let mut headers = HashMap::new();
        loop {
            line.clear();
            reader.read_line(&mut line)?;
            if line.trim().is_empty() {
                break;
            }
            let parts = line.trim().split(": ").collect::<Vec<_>>();
            if parts.len() != 2 {
                eprintln!("[MIN-HTTPD] Invalid HTTP header: {}", line);
                return Ok(());
            }
            headers.insert(
                parts[0].to_lowercase().to_string(),
                parts[1].to_lowercase().to_string()
            );
        }

        let body = if headers.contains_key("content-length") {
            let content_length = headers["content-length"].parse::<usize>()?;
            let mut buffer = vec![0; content_length];
            reader.read_exact(&mut buffer)?;
            Some(buffer)
        } else {
            None
        };

        let handler = self.handlers.get(&uri);
        if let Some(handler) = handler {
            let result = handler(
                headers,
                params,
                body.map(|b| String::from_utf8_lossy(b.as_ref()).to_string())
            );
            let (code, (content_type, response)) = match result {
                Ok(result) => ("200 Ok", result),
                Err(e) => {
                    eprintln!("[MIN-HTTPD] Error: {}", e);
                    ("500 Internal Server Error", ("text/plain".to_string(), e))
                }
            };

            let response = format!(
                "HTTP/1.1 {}\r\nContent-Type: {}, \r\n\r\n{}",
                code,
                content_type,
                response
            );
            writer.write_all(response.as_bytes())?;
            writer.flush()?;
        } else {
            eprintln!("[MIN-HTTPD] No handler for URI: {}", uri);
            writer.write_all(HTTP_404_STRING)?;
        }

        Ok(())
    }
}

impl Default for MinHttpd {
    fn default() -> Self {
        Self::new()
    }
}
