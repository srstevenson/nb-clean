use std::fmt;

pub struct Error {
    pub code: u8,
    message: String,
}

impl Error {
    pub fn new(code: u8, message: impl fmt::Display) -> Self {
        Self {
            code,
            message: message.to_string(),
        }
    }
}

impl fmt::Display for Error {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        f.write_str(&self.message)
    }
}
