import { readJson } from './app/utils.js';
import { Server } from './app/server.js';



Server.run(readJson('./data/config.json'));



// console.log(db);

/*
db.exec(`
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        age INTEGER
    );
`);

CREATE TABLE enrollments (
    student_id INTEGER,
    course_id INTEGER,
    enrollment_date TEXT,
    PRIMARY KEY (student_id, course_id)
);

CREATE TABLE Albums (
    AlbumID INTEGER PRIMARY KEY,
    AlbumTitle TEXT NOT NULL,
    ArtistID INTEGER,
    FOREIGN KEY (ArtistID) REFERENCES Artists(ArtistID)
);

db.close();

// ---------------------------------------------------------

try {
  // Begin a transaction
  const createTables = db.transaction(() => {
    db.prepare(`
      CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL
      );
    `).run();

    db.prepare(`
      CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        price REAL NOT NULL
      );
    `).run();

    db.prepare(`
      CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (product_id) REFERENCES products(id)
      );
    `).run();
  });

  // Execute the transaction
  createTables();
  console.log('Tables created successfully in a single transaction.');

} catch (error) {
  console.error('Error creating tables:', error.message);
  // The transaction will be automatically rolled back in case of an error
} finally {
  db.close();
}

*/