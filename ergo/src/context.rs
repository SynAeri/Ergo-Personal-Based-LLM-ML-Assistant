// This file analyzes activity patterns and builds context for the LLM to be 

use crate::database::{Database, ActivityEntry};
use chrono::Local;
use std::collections::HashMap;

pub struct ContextAnalyzer<'a> {
    db: &'a Database,
}

impl<'a> ContextAnalyzer<'a> {

    // Initialises Context struct thingy
    pub fn new(db: &'a Database) -> Self {
        ContextAnalyzer { db }
    }

    // Check if the user stuck on task
    pub fn is_stuck(&self, minutes: i64) -> Self {
        match self.db.detect_stuck_pattern(minutes) {
            OK(Some(window)) => {
                Some(StuckPattern {
                    window_title: window,
                    duration_minutes: minutes,
                    // Possibly add suggestions filter for later
                    //suggestion: self
                })
            }

        }
    }

}
