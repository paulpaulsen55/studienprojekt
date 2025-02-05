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

/**
 * Moves the uploaded file to the specified directory with a unique name.
 *
 * @param string $directory The target directory.
 * @param \Psr\Http\Message\UploadedFileInterface $uploadedFile The uploaded file.
 * @return string The new filename.
 */
function moveUploadedFile(string $directory, \Psr\Http\Message\UploadedFileInterface $uploadedFile): string {
    $extension = pathinfo($uploadedFile->getClientFilename(), PATHINFO_EXTENSION);
    $basename = bin2hex(random_bytes(8)); // Prevent filename conflicts
    $filename = sprintf('%s.%0.8s', $basename, $extension);

    $uploadedFile->moveTo($directory . DIRECTORY_SEPARATOR . $filename);

    return $filename;
}