<?php
use Psr\Http\Message\ResponseInterface as Response;
use Psr\Http\Message\ServerRequestInterface as Request;
use Slim\Factory\AppFactory;
use Slim\Views\Twig;
use Slim\Views\TwigMiddleware;


require_once __DIR__ . '/../database.php';
require_once __DIR__ . '/../helper.php';
require __DIR__ . '/../parallel.php';
require __DIR__ . '/../fibers.php';

require __DIR__ . '/../../vendor/autoload.php';

$app = AppFactory::create();

$twig = Twig::create('../templates', ['cache' => false]);
$app->add(TwigMiddleware::create($app, $twig));


$app->get('/', function (Request $request, Response $response, $args) {
    $view = Twig::fromRequest($request);
    return $view->render($response, 'index.twig');
});

$app->get('/about', function (Request $request, Response $response, $args) {
    $view = Twig::fromRequest($request);
    ob_start();
    phpinfo();
    $phpinfo = ob_get_clean();

    return $view->render($response, 'about.twig', ['phpinfo' => $phpinfo]);
});

$app->get('/t1', function (Request $request, Response $response, $args) {
    $db = Database::getInstance('bank');

    $db->createTable('users', [
        'id' => 'INT AUTO_INCREMENT PRIMARY KEY',
        'name' => 'VARCHAR(100)',
        'balance' => 'DECIMAL(10, 2) DEFAULT 0'	
    ]);

    $db->insertData('users', ['name' => 'Konto1', 'balance' => 1000]);
    $db->insertData('users', ['name' => 'Konto2', 'balance' => 1000]);
    $db->insertData('users', ['name' => 'Konto3', 'balance' => 1000]);

    $db = $db->getPdo();

    $stmt = $db->prepare("SELECT name, balance FROM users");
    $stmt->execute();
    $users = $stmt->fetchAll(PDO::FETCH_ASSOC);

    $view = Twig::fromRequest($request);
    return $view->render($response, 't1.twig', ['users' => $users]);
});

$app->get('/t1/parallel', \ParallelController::class . ':test1');
$app->get('/t1/fibers', \FibersController::class . ':test1');


$app->get('/t2', function (Request $request, Response $response, $args) {
    $view = Twig::fromRequest($request);
    return $view->render($response, 't2.twig');
});

$app->get('/t2/fibers', \FibersController::class . ':test2');
$app->get('/t2/parallel', \ParallelController::class . ':test2');

$app->get('/t3', function (Request $request, Response $response, $args) {
    $view = Twig::fromRequest($request);
    return $view->render($response, 't3.twig');
});

$app->post('/t3/upload', function (Request $request, Response $response, array $args): Response {
    clearAssets();
    $params = $request->getParsedBody();
    $library = $params['library'] ?? 'parallel';

    if ($library === 'parallel') {
        $parallelController = new \ParallelController();
        return $parallelController->test3Post($request, $response, $args);
    } else {
        $fibersController = new \FibersController();
        return $fibersController->test3($request, $response, $args);
    }
});

$app->get('/t3/upload', \ParallelController::class . ':test3Get');

$app->run();