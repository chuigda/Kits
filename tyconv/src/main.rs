use std::fs::{read_to_string, write};
use xjbutil::std_ext::ExpectSilentExt;

fn yaml2toml(yaml_value: serde_yaml::Value) -> toml::Value {
    use serde_yaml::Value;
    match yaml_value {
        Value::Null => toml::Value::String("\x00".into()),
        Value::Bool(b) => toml::Value::Boolean(b),
        Value::Number(n) => if n.is_f64() {
            toml::Value::Float(n.as_f64().unwrap())
        } else {
            toml::Value::Integer(n.as_i64().unwrap())
        },
        Value::String(s) => toml::Value::String(s),
        Value::Sequence(seq) => toml::Value::Array(
            seq.into_iter()
                .map(yaml2toml)
                .collect(),
        ),
        Value::Mapping(mapping) => toml::Value::Table(mapping.into_iter().map(|(k, v)| {
            if let Value::String(k) = k {
                let v = yaml2toml(v);
                (k, v)
            } else {
                panic!("unable to process non-string yaml key: {:?}", k);
            }
        }).collect())
    }
}

fn toml2yaml(toml_value: toml::Value) -> serde_yaml::Value {
    use toml::Value;
    match toml_value {
        Value::String(s) => if s == "\x00" {
            serde_yaml::Value::Null
        } else {
            serde_yaml::Value::String(s)
        },
        Value::Integer(i) => serde_yaml::Value::from(i),
        Value::Float(f) => serde_yaml::Value::from(f),
        Value::Boolean(b) => serde_yaml::Value::Bool(b),
        Value::Datetime(d) => serde_yaml::Value::String(d.to_string()),
        Value::Array(arr) => serde_yaml::Value::Sequence(arr.into_iter().map(toml2yaml).collect()),
        Value::Table(table) => serde_yaml::Value::Mapping(
            table.into_iter()
                .map(|(k, v)| (serde_yaml::Value::String(k), toml2yaml(v)))
                .collect()
        )
    }
}

fn main() {
    let args = std::env::args().collect::<Vec<_>>();
    if args.len() != 4 || (args[1] != "y2t" && args[1] != "t2y") {
        eprintln!("usage: tyconv [y2r|r2y] source dest");
        return;
    }

    let source = read_to_string(&args[2])
        .expect_silent(&format!("cannot read file \"{}\"", &args[2]));

    match args[1].as_str() {
        "y2t" => {
            let yaml_value: serde_yaml::Value
                = serde_yaml::from_str(&source).expect("cannot parse source file");
            let toml_value: toml::Value = yaml2toml(yaml_value);
            let toml = toml::to_string_pretty(&toml_value).expect("failed serializing toml value");
            write(&args[3], toml).expect_silent(&format!("cannot write file \"{}\"", &args[3]));
        },
        "t2y" => {
            let toml_value: toml::Value
                = toml::from_str(&source).expect("cannot parse source file");
            let yaml_value: serde_yaml::Value = toml2yaml(toml_value);
            let yaml = serde_yaml::to_string(&yaml_value).expect("cannot convert to yaml");
            write(&args[3], yaml).expect_silent(&format!("cannot write file \"{}\"", &args[3]));
        },
        _ => unreachable!()
    }
}
