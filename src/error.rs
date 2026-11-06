use std::fmt::{self, Display, Formatter};

pub struct Error {
    pub code: u8,
    message: String,
}

impl Error {
    pub fn new(code: u8, message: impl Display) -> Self {
        Self {
            code,
            message: message.to_string(),
        }
    }
}

impl Display for Error {
    fn fmt(&self, f: &mut Formatter<'_>) -> fmt::Result {
        f.write_str(&self.message)
    }
}
