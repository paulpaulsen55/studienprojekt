<?php
// Ensure the GD library is loaded
if (!extension_loaded('gd')) {
    dl('gd.so');
}

// Ensure the parallel extension is loaded
if (!extension_loaded('parallel')) {
    throw new Exception('Parallel extension not loaded.');
}