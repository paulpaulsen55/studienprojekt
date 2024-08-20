<?php

function clearAssets() {
    $dir = __DIR__ . '/public/assets';
    $files = glob($dir . '/*');
    foreach ($files as $file) {
        if (is_file($file)) {
            unlink($file);
        }
    }
}