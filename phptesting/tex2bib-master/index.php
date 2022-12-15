<?php
include("Convert.inc.php");

// Following lines are examples.  See Convert.inc.php for all possibilities.
$labelStyle = 'short';
$overrideLabels = true;
$lineEndings = 'w';
$verbose = 1;
$debug = 0;
$itemSeparator = 'cr';
$percentComment = 1;
$filename = 'example-cites.tex';

$convert = new Convert($labelStyle, $overrideLabels, $lineEndings, $verbose, $debug, $itemSeparator, $percentComment);
$items = $convert->convertToBibtex($filename);
$outputstring = $convert->formBibtex($items);
var_dump($outputstring);
