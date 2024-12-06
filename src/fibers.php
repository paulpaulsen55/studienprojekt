<?php

use Psr\Http\Message\ResponseInterface;
use Psr\Http\Message\ServerRequestInterface;
use Psr\Container\ContainerInterface;
use Slim\Views\Twig;
use GuzzleHttp\Client;

require_once __DIR__ . '/database.php';

class FibersController
{
    public function test1(ServerRequestInterface $request, ResponseInterface $response, array $args): ResponseInterface {
        $db = Database::getInstance('bank')->getPdo();

        $stmt = $db->prepare("SELECT name, balance FROM users");
        $stmt->execute();
        $usersOld = $stmt->fetchAll(PDO::FETCH_ASSOC);

        $update1 = new Fiber(function () use ($db) {
            $transfertAmount = 500;

            $stmt = $db->prepare("SELECT balance FROM users WHERE name = 'Konto1'");
            $stmt->execute();
            $oldBalance = $stmt->fetchColumn();

            $newValue = $oldBalance + $transfertAmount;
            $stmt = $db->prepare("UPDATE users SET balance = " . $oldBalance - $transfertAmount . " WHERE name = 'Konto1'");
            $stmt->execute();

            $stmt = $db->prepare("SELECT balance FROM users WHERE name = 'Konto2'");
            $stmt->execute();
            $oldBalance = $stmt->fetchColumn();

            $stmt = $db->prepare("UPDATE users SET balance = " . $oldBalance + $transfertAmount ." WHERE name = 'Konto2'");
            $stmt->execute();
        });
    
        $update2 = new Fiber(function () use ($db) {
            $transfertAmount = 500;

            $stmt = $db->prepare("SELECT balance FROM users WHERE name = 'Konto3'");
            $stmt->execute();
            $oldBalance = $stmt->fetchColumn();

            $newValue = $oldBalance - $transfertAmount;
            $stmt = $db->prepare("UPDATE users SET balance = " . $newValue . " WHERE name = 'Konto3'");
            $stmt->execute();

            $stmt = $db->prepare("SELECT balance FROM users WHERE name = 'Konto1'");
            $stmt->execute();
            $oldBalance = $stmt->fetchColumn();

            $newValue = $oldBalance + $transfertAmount;
            $stmt = $db->prepare("UPDATE users SET balance = " . $newValue . " WHERE name = 'Konto1'");
            $stmt->execute();
        });
    
        $update1->start();
        $update2->start();
    
        if ($update1->isRunning()) {
            $update1->resume();
        }
        if ($update2->isRunning()) {
            $update2->resume();
        }

        $stmt = $db->prepare("SELECT name, balance FROM users");
        $stmt->execute();
        $users = $stmt->fetchAll(PDO::FETCH_ASSOC);

        $view = Twig::fromRequest($request);
        return $view->render($response, 't1.twig', ['users' => $users, 'usersOld' => $usersOld]);
    }

    public function test2(ServerRequestInterface $request, ResponseInterface $response, array $args): ResponseInterface {
        $client = new Client();
        $fetch1 = new Fiber(function () use ($client) {
            $response = $client->get('https://api.open-meteo.com/v1/forecast?latitude=59.9127&longitude=10.7461&timezone=Europe%2FBerlin&forecast_days=1');
            $data = json_decode($response->getBody(), true);
            Fiber::suspend($data);
        });

        $weatherData = $fetch1->start();

        $fetch2 = new Fiber(function () use ($client) {
            $response = $client->get('https://api.open-meteo.com/v1/forecast?latitude=59.9127&longitude=10.7461&current=temperature_2m&timezone=Europe%2FBerlin&forecast_days=1&models=metno_seamless');
            $data = json_decode($response->getBody(), true);
            Fiber::suspend($data);
        });

        $weatherData = $fetch2->start();

        $view = Twig::fromRequest($request);
        return $view->render($response, 't2.twig', ['weather' => $weatherData]);
    }

    public function test3(ServerRequestInterface $request, ResponseInterface $response, array $args) {
        $files = $request->getUploadedFiles();
        $uploadDir = __DIR__ . '/public/assets/';
        $savedFiles = [];
        
        $before = microtime(true);

        foreach ($files['images'] as $file) {
            if ($file->getError() === UPLOAD_ERR_OK) {
                $fiber = new Fiber(function () use ($file, $uploadDir) {
                    $image = imagecreatefromstring(file_get_contents($file->getStream()->getMetadata('uri')));
                    imagefilter($image, IMG_FILTER_GRAYSCALE);
                    imagepng($image, $uploadDir . $file->getClientFilename());
                    imagedestroy($image);
                    return $file->getClientFilename();
                });

                $fiber->start();

                $savedFiles[] = $file->getClientFilename();
            }
        }

        $after = microtime(true);

        $view = Twig::fromRequest($request);
        return $view->render($response, 't3.twig', [
            'images' => $savedFiles,
            'processingTime' => $after - $before
        ]);
    }
}
