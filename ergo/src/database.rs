use rusqlite::{Connection, Result, params};
use std::path::PathBuf;
use chrono::{Local, DateTime};

pub struct Database {
    conn: Connection,
}

impl Database {
    // Create or open database
    pub fn new(db_path: &PathBuf) -> Result<self> {

    }
}
