<?php

class Database {
    private static $instances = [];
    private $pdo;

    private function __construct($dbName) {
        $host = '127.0.0.1';
        $user = 'root';
        $pass = '';
        $charset = 'utf8mb4';

        $dsn = "mysql:host=$host;dbname=$dbName;charset=$charset";
        $opt = [
            PDO::ATTR_ERRMODE            => PDO::ERRMODE_EXCEPTION,
            PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
            PDO::ATTR_EMULATE_PREPARES   => false,
        ];
        $this->pdo = new PDO($dsn, $user, $pass, $opt);
    }

    public static function getInstance($dbName) {
        if (!isset(self::$instances[$dbName])) {
            self::$instances[$dbName] = new Database($dbName);
        }
        return self::$instances[$dbName];
    }

    public function getPdo() {
        return $this->pdo;
    }
}