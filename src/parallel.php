<?php

use Psr\Http\Message\ResponseInterface;
use Psr\Http\Message\ServerRequestInterface;
use Slim\Views\Twig;
use parallel\Runtime;
use parallel\Channel;

require_once __DIR__ . '/database.php';

class ParallelController
{
    public function test3(ServerRequestInterface $request, ResponseInterface $response, array $args): ResponseInterface {
        $db = Database::getInstance('bank')->getPdo();
                
        // this function will be the threads
        $thread_function = function (int $id, Channel $ch) {
            // delay the first thread to simulate better multithreading
            // second thread always finishes first
            $sleep = ($id == 2) ? 1 : 2;
            sleep($sleep);
        
            // print thread id
            // so it's clear second thread goes first
            // and also you can make sure multithreading is working
            var_dump("thread $id sleep $sleep");
        
            // try to capture globals, but it's not possible
            echo '$GLOBALS["db"] = ';
            @var_dump($GLOBALS["db"]);
        
            // the only way to share data is between channels
            $ch->send($sleep);
        };
        
        try {
            // each runtime represents a thread
            $r1 = new Runtime();
            $r2 = new Runtime();
        
            // channel where the date will be sharead
            $ch1 = new Channel();
        
            // args that will be sent to $thread_function
            $args = array();
            $args[0] = null;
            $args[1] = $ch1;
        
            // running thread 1
            $args[0] = 1;
            $r1->run($thread_function, $args);
        
            // running thread 2
            $args[0] = 2;
            $r2->run($thread_function, $args);
        
            // receive data from channel
            $x = $ch1->recv();
            $y = $ch1->recv();
        
            // close channel
            $ch1->close();
        
            echo "\nData received by the channel: $x and $y";
        } catch (Error $err) {
            echo "\nError:", $err->getMessage();
        } catch (Exception $e) {
            echo "\nException:", $e->getMessage();
        }

        $view = Twig::fromRequest($request);
        return $view->render($response, 't3.twig');
    }
}
