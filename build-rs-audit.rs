use std::env;
use std::process::{Command, Output};
use std::fs::metadata;

fn get_default_editor() -> String {
    match env::var("EDITOR") {
        Ok(editor) => editor,
        Err(_) => {
            eprintln!(
                "environment variable `EDITOR` not set, falling back to default"
            );
            #[cfg(target_os = "windows")]
            {
                "notepad".to_string()
            }
            #[cfg(target_os = "macos")]
            {
                "open".to_string()
            }
            #[cfg(target_os = "linux")]
            {
                "nano".to_string()
            }
        }
    }
}

fn get_cargo_home() -> (String, bool) {
    match env::var("CARGO_HOME") {
        Ok(cargo_home) => (cargo_home, true),
        Err(_) => {
            let home = env::var("HOME").expect("neither `HOME` nor `CARGO_HOME` set");
            let cargo_home = format!("{}/.cargo", home);
            (cargo_home, false)
        }
    }
}

fn main() {
    // get default editor
    let editor: String = get_default_editor();
    eprintln!("using editor: `{}`", editor);
    let editor_error: String = format!("failed to start up editor: `{}`", editor);

    // use `cargo-fetch` to pre-fetch all dependencies
    eprintln!("running `cargo fetch`");
    let fetch_success: bool = Command::new("cargo")
        .args(&["fetch"])
        .spawn()
        .expect("failed to spawn `cargo fetch`")
        .wait()
        .expect("failed to wait for `cargo fetch`")
        .success();
    if !fetch_success {
        panic!("failed to fetch dependencies");
    }

    // list all dependencies
    eprintln!("listing all dependencies");
    let tree_result: Output = Command::new("cargo")
        .args(&["tree", "--prefix=none", "--all-features"])
        .output()
        .expect("failed to execute `cargo tree`");
    if !tree_result.status.success() {
        panic!("failed to list all dependencies");
    }

    let tree_result: String = String::from_utf8_lossy(&tree_result.stdout).to_string();
    let mut dependencies: Vec<String> = tree_result.split("\n")
        .filter(|line| {
            // exclude duplicate dependencies
            !line.contains("(*)")
            // exclude local dependencies
            && !line.contains("/")
        })
        .map(|line| line.trim().split(" ").collect::<Vec<_>>())
        .filter(|parts| parts.len() >= 2)
        .map(|parts| format!("{}-{}", parts[0], &parts[1][1..]))
        .collect::<Vec<_>>();
    dependencies.sort();
    dependencies.dedup();

    // locate the cargo directory
    eprintln!("{} dependencies loaded", dependencies.len());
    let (cargo_home, for_sure): (String, bool) = get_cargo_home();
    if for_sure {
        eprintln!("found `CARGO_HOME`: {}", cargo_home);
    } else {
        eprintln!("found `HOME`, assuming `CARGO_HOME` to be: {}", cargo_home);
    }
    let cargo_registry_src_dir: String = format!("{}/registry/src", cargo_home);

    let read_registry_err: String = format!(
        "cannot read registry directory: {}",
        cargo_registry_src_dir
    );

    // read the registry directory
    let registry_directories: Vec<String> = std::fs::read_dir(cargo_registry_src_dir)
        .expect(&read_registry_err)
        .map(|x| x.expect(&read_registry_err))
        .filter(|x| x.file_type().expect(&read_registry_err).is_dir())
        .map(|x| x.path().to_string_lossy().to_string())
        .collect::<Vec<_>>();

    // read each registry directory
    for registry_dir in registry_directories {
        eprintln!("auditing registry directory: {}", registry_dir);
        for dependency in &dependencies {
            let dependency_dir: String = format!("{}/{}", registry_dir, dependency);
            match metadata(&dependency_dir) {
                Ok(meta) => {
                    if meta.is_file() {
                        continue;
                    }

                    let build_rs: String = format!("{}/build.rs", dependency_dir);
                    let build_rs_exists: bool = metadata(&build_rs).is_ok();
                    if !build_rs_exists {
                        eprintln!(">> crate `{}` appear not to have a `build.rs`", dependency);
                        continue;
                    }

                    eprintln!(">> auditing {}/build.rs", dependency);

                    // open with the default editor
                    let _ = Command::new(&editor)
                        .arg(&build_rs)
                        .output()
                        .expect(&editor_error);
                },
                Err(_) => {}
            }
        }
    }
}
