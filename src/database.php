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
        try {
            $this->pdo = new PDO($dsn, $user, $pass, $opt);
        } catch (PDOException $e) {
            if ($e->getCode() == 1049) {
                $this->pdo = new PDO("mysql:host=$host;", $user, $pass, $opt);
                $this->pdo->exec("CREATE DATABASE `$dbName`;USE `$dbName`;");
            } else {
                throw $e;
            }
        }
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

    private function createDatabase($dbName) {
        $stmt = $this->pdo->prepare("SHOW DATABASES LIKE :dbName");
        $stmt->execute(['dbName' => $dbName]);
        if ($stmt->fetch(PDO::FETCH_ASSOC) === false) {
            $this->pdo->exec("CREATE DATABASE {$dbName}");
        }
    }

    public function createTable($tableName, $columns) {
        $columnsSql = implode(', ', array_map(function($column, $type) {
            return "$column $type";
        }, array_keys($columns), $columns));
        $stmt = $this->pdo->prepare("SHOW TABLES LIKE '$tableName'");
        $stmt->execute();
        if ($stmt->fetch(PDO::FETCH_ASSOC)) {
            $this->pdo->exec("DELETE FROM $tableName");
        } else {
            $sql = "CREATE TABLE IF NOT EXISTS $tableName ($columnsSql)";
            $this->pdo->exec($sql);
        }
    }

    public function insertData($tableName, $data) {
        $columns = implode(', ', array_keys($data));
        $placeholders = implode(', ', array_fill(0, count($data), '?'));
        $sql = "INSERT INTO $tableName ($columns) VALUES ($placeholders)";
        $stmt = $this->pdo->prepare($sql);
        $stmt->execute(array_values($data));
    }
}