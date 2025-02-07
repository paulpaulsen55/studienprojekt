<?php

use Psr\Http\Message\ResponseInterface;
use Psr\Http\Message\ServerRequestInterface;
use Slim\Views\Twig;
use parallel\Runtime;
use GuzzleHttp\Client;

require_once __DIR__ . '/database.php';

class ParallelController
{
    public function test1(ServerRequestInterface $request, ResponseInterface $response, array $args): ResponseInterface {
        $dbConfig = Database::getInstance('bank')->getConfig();
        $db = Database::getInstance('bank')->getPDO();

        $before = microtime(true);

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

        $after = microtime(true);
        $processingTime = $after - $before;

        $view = Twig::fromRequest($request);
        return $view->render($response, 't1.twig', [
            'users' => $users,
            'usersOld' => $usersOld,
            'processingTime' => $processingTime
        ]);
    }

    public function test2(ServerRequestInterface $request, ResponseInterface $response, array $args): ResponseInterface {
        $before = microtime(true);
        
        $runtime1 = new Runtime();
        $future1 = $runtime1->run(function () {
            require_once __DIR__ . '/../vendor/autoload.php';

            $client = new \GuzzleHttp\Client();
            $response = $client->get('https://api.open-meteo.com/v1/forecast?latitude=59.9127&longitude=10.7461&timezone=Europe%2FBerlin&forecast_days=1');
            return json_decode($response->getBody(), true);
        });

        $weatherData = $future1->value();

        $runtime2 = new Runtime();
        $future2 = $runtime2->run(function () {
            require_once __DIR__ . '/../vendor/autoload.php';

            $client = new \GuzzleHttp\Client();
            $response = $client->get('https://api.open-meteo.com/v1/forecast?latitude=59.9127&longitude=10.7461&current=temperature_2m&timezone=Europe%2FBerlin&forecast_days=1&models=metno_seamless');
            return json_decode($response->getBody(), true);
        });

        $weatherData = $future2->value();

        $after = microtime(true);
        $processingTime = $after - $before;

        $view = Twig::fromRequest($request);
        return $view->render($response, 't2.twig', [
            'weather' => $weatherData,
            'processingTime' => $processingTime
        ]);
    }

    public function test3Post(ServerRequestInterface $request, ResponseInterface $response, array $args): ResponseInterface {
        $files = $request->getUploadedFiles();
        
        if (!isset($files['images'])) {
            // Handle the case where 'images' key is missing
            $response->getBody()->write('No images uploaded.');
            return $response->withStatus(400);
        }
    
        $uploadDir = __DIR__ . '/public/assets/';
        $savedFiles = [];
        $before = microtime(true);

        foreach ($files['images'] as $file) {
            if ($file->getError() === UPLOAD_ERR_OK) {
                $fileName = moveUploadedFile($uploadDir, $file);
                $savedFiles[] = $fileName;
            }
        }
    
        session_start();

        // Store the saved file names in the session
        $_SESSION['savedFiles'] = $savedFiles;

        $after = microtime(true);
        $_SESSION['processingTime'] = $after - $before;

        // Redirect to the GET route for processing
        return $response
            ->withHeader('Location', '/t3/upload')
            ->withStatus(302);
    }

    public function test3Get(ServerRequestInterface $request, ResponseInterface $response, array $args): ResponseInterface {
        session_start();
        $savedFiles = $_SESSION['savedFiles'] ?? [];
        $uploadingTime = $_SESSION['processingTime'] ?? 0;

        if (empty($savedFiles)) {
            $response->getBody()->write('No files found.');
            return $response->withStatus(404);
        }

        $before = microtime(true);
        $processedFiles = $this->processImagesInParallel($savedFiles);
        $after = microtime(true);

        $processingTime = $after - $before + $uploadingTime;

        // Clear the session after processing
        $_SESSION['savedFiles'] = [];
        $_SESSION['processingTime'] = 0;
    
        $view = Twig::fromRequest($request);
        return $view->render($response, 't3.twig', [
            'images' => $processedFiles,
            'processingTime' => $processingTime
        ]);
    }

    /**
     * Processes images in parallel by applying a grayscale filter.
     *
     * @param array $files The list of filenames to process.
     * @return array The list of processed filenames.
     */
    private function processImagesInParallel(array $files): array {
        $uploadDir = __DIR__ . '/public/assets/';
        $processedFiles = [];

        $runtimes = [];
        $futures = [];

        // Initialize runtimes
        foreach ($files as $file) {
            $runtime = new Runtime(__DIR__ . '/bootstrap.php');
            $runtimes[] = $runtime;
            $futures[] = $runtime->run(function ($uploadDir, $file) {
                $imagePath = $uploadDir . $file;
                $image = imagecreatefromstring(file_get_contents($imagePath));
                if ($image === false) {
                    return false;
                }
                imagefilter($image, IMG_FILTER_GRAYSCALE);
                $processedFilename = 'processed_' . $file;
                imagepng($image, $uploadDir . $processedFilename);
                imagedestroy($image);
                return $processedFilename;
            }, [$uploadDir, $file]);
        }

        // Collect results
        foreach ($futures as $future) {
            $result = $future->value();
            if ($result !== false) {
                $processedFiles[] = $result;
            }
        }

        return $processedFiles;
    }
}
