const sqlite3 = require('sqlite3').verbose();

class SqliteDatabase {
    constructor(filename) {
        this.connection = new sqlite3.Database(filename);
    }

    run(sql, params = []) {
        return new Promise((resolve, reject) => {
            this.connection.run(sql, params, function onRun(error) {
                if (error) return reject(error);
                resolve({ lastID: this.lastID, changes: this.changes });
            });
        });
    }

    get(sql, params = []) {
        return new Promise((resolve, reject) => {
            this.connection.get(sql, params, (error, row) => {
                if (error) return reject(error);
                resolve(row);
            });
        });
    }

    all(sql, params = []) {
        return new Promise((resolve, reject) => {
            this.connection.all(sql, params, (error, rows) => {
                if (error) return reject(error);
                resolve(rows);
            });
        });
    }

    close() {
        return new Promise((resolve, reject) => {
            this.connection.close(error => (error ? reject(error) : resolve()));
        });
    }
}

module.exports = SqliteDatabase;
