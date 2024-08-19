<?php

use Psr\Http\Message\ResponseInterface;
use Psr\Http\Message\ServerRequestInterface;
use Slim\Views\Twig;
use parallel\Runtime;

require_once __DIR__ . '/database.php';

class ParallelController
{
    public function test1(ServerRequestInterface $request, ResponseInterface $response, array $args): ResponseInterface {
        $dbConfig = Database::getInstance('bank')->getConfig();
        $db = Database::getInstance('bank')->getPDO();

        $stmt = $db->prepare("SELECT name, balance FROM users");
        $stmt->execute();
        $usersOld = $stmt->fetchAll(PDO::FETCH_ASSOC);

        $runtime1 = new Runtime();
        $runtime2 = new Runtime();

        // Konto1 überweist Konto2 500€
        $future1 = $runtime1->run(function ($dbConfig) {
            $db = new PDO($dbConfig['dsn'], $dbConfig['user'], $dbConfig['pass'], $dbConfig['opt']);
            
            $stmt = $db->prepare('SELECT balance FROM users WHERE name = "Konto1"');
            $stmt->execute();
            $oldBalance = $stmt->fetchColumn();

            $stmt = $db->prepare('SELECT balance FROM users WHERE name = "Konto2"');
            $stmt->execute();
            $oldBalance2 = $stmt->fetchColumn();
            
            $stmt = $db->prepare('UPDATE users SET balance = ' . $oldBalance - 500 . ' WHERE name = "Konto1"');
            $stmt->execute();
            $stmt = $db->prepare('UPDATE users SET balance = ' . $oldBalance2 + 500 . ' WHERE name = "Konto2"');
            $stmt->execute();
        }, [$dbConfig]);

        // Konto3 überweist Konto1 1000€
        $future2 = $runtime2->run(function ($dbConfig) {
            $db = new PDO($dbConfig['dsn'], $dbConfig['user'], $dbConfig['pass'], $dbConfig['opt']);
            
            $stmt = $db->prepare('SELECT balance FROM users WHERE name = "Konto3"');
            $stmt->execute();
            $oldBalance = $stmt->fetchColumn();

            $stmt = $db->prepare('SELECT balance FROM users WHERE name = "Konto1"');
            $stmt->execute();
            $oldBalance2 = $stmt->fetchColumn();
            
            $stmt = $db->prepare('UPDATE users SET balance = ' . $oldBalance - 1000 . ' WHERE name = "Konto3"');
            $stmt->execute();
            $stmt = $db->prepare('UPDATE users SET balance = ' . $oldBalance2 + 1000 . ' WHERE name = "Konto1"');
            $stmt->execute();
        }, [$dbConfig]);

        // wait for both futures to finish
        while (!$future1->done() && !$future2->done()) {
            usleep(50);
        }

        $stmt = $db->prepare("SELECT name, balance FROM users");
        $stmt->execute();
        $users = $stmt->fetchAll(PDO::FETCH_ASSOC);

        $view = Twig::fromRequest($request);
        return $view->render($response, 't3.twig', ['users' => $users, 'usersOld' => $usersOld]);
    }

    public function test3(ServerRequestInterface $request, ResponseInterface $response, array $args): ResponseInterface {
        $files = $request->getUploadedFiles();
        $uploadDir = __DIR__ . '/public/assets/';
        $savedFiles = [];
        $runtimes = [];

        foreach ($files['images'] as $file) {
            if ($file->getError() === UPLOAD_ERR_OK) {
                try {
                    $runtime = new Runtime(__DIR__ . '/bootstrap.php');
                    $imageData = file_get_contents($file->getStream()->getMetadata('uri'));
                    $runtime->run(function ($imageData, $uploadDir, $fileName) {
                        $image = imagecreatefromstring($imageData);
                        if (!@imagefilter($image, IMG_FILTER_GRAYSCALE)) {
                            // Handle the error, e.g., log it or throw an exception
                            die('Failed to apply grayscale filter to the image.');
                        }
                        if (!imagepng($image, $uploadDir . $fileName)) {
                            imagedestroy($image);
                            die('Failed to output image');
                        }
                        imagedestroy($image);
                    }, [$imageData, $uploadDir, $file->getClientFilename()]);

                    $runtimes[] = $runtime;
                    $savedFiles[] = $file->getClientFilename();
                } catch (Exception $e) {
                    // Handle the exception, e.g., log it or return an error response
                    return $response->withStatus(500)->write('Failed to process image: ' . $e->getMessage());
                }
            }
        }

        $view = Twig::fromRequest($request);
        return $view->render($response, 't3.twig', ['images' => $savedFiles]);
    }
}
