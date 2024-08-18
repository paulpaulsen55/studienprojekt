<?php
// Ensure the GD library is loaded
if (!extension_loaded('gd')) {
    dl('gd.so');
}
