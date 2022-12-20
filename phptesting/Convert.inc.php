<?php   //  -*- tab-width:4; -*-
error_reporting(E_ERROR | E_PARSE);

/**
 * Convert.inc.php
 *
 * Reimplementation by Martin J. Osborne of class written by Fabian Qifei Bai
 * Copyright (c) 2007 Martin J. Osborne
 * Distributed under the GNU GPL v2. For full terms see the file COPYING.
 *
 * For version, see first line of constructor of Convert class.
 */

//import("convert.Bibtex");

class bibtex {
	var $OriginalFormat; //Original format of the file if known
	var $label;
	var $kind;
	var $type;
	var $author;
	var $editor;
	var $title;
	var $edition;
	var $number;
	var $volume;
	var $pages;
	var $year;
	var $journal;
	var $publisher;
	var $note;
	var $address;
	var $institution;
	var $booktitle;
	var $month;
	var $school;
	var $unidentified;
}

class Convert {

	var $version;
	var $labelStyle;
	var $overrideLabels;
	var $lineEndings;
	var $itemSeparator;
	var $percentComment;
	var $verbose;
	var $debug;
	var $displayLines;
	var $cities;
	var $publishers;
	var $workingPaperRegExp;
	var $italicCodes;
	var $boldCodes;
	var $italicTitle;

	/*
	 * $labelStyle: 'short' or 'long' [any other string is equivalent to 'long']
	 * $overrideLabels: true or false
	 * $lineEndings: 'w' [for Windows] or 'l' [for Linux]
	 * $verbose: 1 [display info while converting] or 0 [don't]
	 * $debug: 1 [display additional messages, for debugging purposes] or 0 [don't]
	 * $itemSeparator: 'line' (blank line separates items), 'cr' (each line is an item)
	 */
	function Convert($labelStyle, $overrideLabels, $lineEndings, $verbose, $debug, $itemSeparator = 'line', $percentComment = 1) {
		$id = '$Id: Convert.inc.php,v 1.16 2008/01/05 05:00:34 osborne Exp $';
		$id = explode(' ', $id);
		$this->version = $id[2] . ' ' . $id[3] . ' ' . $id[4];
		$this->labelStyle = $labelStyle;
		$this->overrideLabels = $overrideLabels;
		$this->lineEndings = $lineEndings;
		$this->itemSeparator = $itemSeparator;
		$this->percentComment = $percentComment;
		$this->verbose = $verbose;
		$this->debug = $debug;
		$this->displayLines = array();
		// The script will identify strings as cities and publishers even if they are not in these arrays---but the
		// presence of a string in one of the arrays helps when the elements of the reference are not styled in any way.
		$this->cities = array('Berlin', 'Boston', 'Cambridge', 'Chicago', 'Greenwich', 'London', 'New York', 'Northampton',
				'Oxford',
				'Princeton', 'San Diego', 'Upper Saddle River', 'Washington');
		$this->publishers = array('Academic Press', 'Cambridge University Press', 'Chapman & Hall', 'Edward Elgar', 'Elsevier',
				'Harvard University Press', 'McGraw-Hill', 'MIT Press', 'Norton', 'Oxford University Press',
				'Prentice Hall', 'Princeton University Press', 'Routledge', 'Springer',
				'Springer-Verlag', 'University of Pittsburgh Press',
				'Van Nostrand Reinhold', 'Wiley', 'Yale University Press');
		$this->workingPaperRegExp = '([Pp]reprint|[Ww]orking [Pp]aper|[Dd]iscussion [Pp]aper|[Tt]echnical [Rr]eport|[Rr]esearch [Pp]aper|[Mi]meo|[Uu]npublished [Pp]aper|[Uu]npublished [Mm]anuscript)';
		$this->italicCodes = array("\\textit{", "\\textsl{", "\\emph{", "{\\em ", "\\em ", "{\\it ", "\\it ", "{\\sl ", "\\sl ");
		$this->boldCodes = array("\\textbf{", "{\\bf ", "{\\bfseries ");
		$this->debug("itemSeparator is " . $itemSeparator);
	}

	function verbose($string) {
		if($this->verbose) $this->displayLines[] = $string;
	}

	function debug($string) {
		if($this->debug) $this->displayLines[] = "<br>$string\n";
	}

	/**
	 * formatDetect
	 * @param $uploadfile
     * @param $string
	 * If $string is not supplied, detect format of string in the file $uploadfile; else detect format of $string.
	 * (Format is used as an entry-separator.)
	 */
	function formatDetect($uploadfile, $string = null){
		if($string) $filestring = $string;
		else $filestring=file_get_contents($uploadfile);
		if (substr_count($filestring , "\\bibitem"))
			return "\bibitem";
		else if (substr_count($filestring, "\\noindent"))
			return "\noindent";
		else if (substr_count($filestring, "\\smallskip"))
			return "\smallskip";
		else if (substr_count ($filestring, "\\item"))
			return "\item";
		else if (substr_count ($filestring, "\\bigskip"))
			return "\bigskip";
		else
			return "generic";	
		return false;
	}

	function killhtml($string){
		$newString = array();
		for ($i=0; $i<strlen($string); $i++){
			if ($string[$i]=="<") for(; $string[$i] != '>' && $i<strlen($string); $i++);
			else $newString[] = $string[$i];
		}
		return implode($newString);
	}

	// Truncate $string at first '%' that is not preceded by '\'.  Return 1 if truncated, 0 if not.
	function uncomment(&$string) {
		for(
			$i=0;
			$i<strlen($string) and 
				($string[$i] != '%' or ($i and $string[$i] == '%' and $string[$i-1] == "\\"));
			$i++
		   ) {}
		$truncated = $i < strlen($string) ? 1 : 0;
		$string = substr($string, 0, $i);
		return $truncated;
	}

	/**
	 * containsFontStyle: report if string contains opening string for font style, at start
	 * if $start is true
	 * @param $string string The string to be searched
	 * @param $start boolean: true if want to restrict to italics starting the string
	 * @param $style: 'italics' [italics or slanted] or 'bold'
	 * @param $startPos: position in $string where italics starts
	 * @param $length: length of string starting italics
	 */
	function containsFontStyle($string, $start, $style, &$startPos, &$length) {
		if($style == 'italics') $codes = $this->italicCodes;
		elseif($style == 'bold') $codes = $this->boldCodes;
		foreach($codes as $code) {
			$length = strlen($code);
			$startPos = strpos($string, $code);
			if($startPos !== false and (($start and $startPos == 0) or !$start)) return true;
		}
		return false;
	}

	/**
	 * WARNING: TAKE CARE WHEN MODIFYING THIS FUNCTION!  Modifications that improve the parsing of
	 *          some strings may well make worse the parsing of other strings.
	 * convertToAuthors: determine the authors in the initial elements of an array of words
	 * @param $words array of words
	 * @param $remainder string remaining string after authors removed
	 * @param $determineEnd boolean if true, figure out where authors end; otherwise take whole string
	 *        to be authors
	 * return author string
	 */
	function convertToAuthors($words, &$remainder, &$year, &$isEditor, $determineEnd = true) {
		$hasAnd = $namePart = $prevWordAnd = $done = $authorIndex = 0;
		$isEditor = false;
		$authorstring = '';
		$remainingWords = $words;
		foreach($words as $i => $word) {
			$this->debug("[0] Word: " . $word);
			// remove first word from $remainingWords
			array_shift($remainingWords);
			if($this->isEd($word, $hasAnd)) {
				$isEditor = true;
				$remainder = implode(" ", $remainingWords);
				break;
			} elseif($word == 'and' or $word == '\\&' or $word == '&') {
				$hasAnd = 1;
				$authorstring .= ' and ';
				$prevWordAnd = 1;
				$namePart = 0;
				$authorIndex++;
				$this->debug("[1] Authorstring: " . $authorstring . ".  Name part: " . $namePart);
			} elseif($word == "{\\sc") {
			} else {
				if($determineEnd and $done) break;
				if($namePart == 0) {
					if(!$prevWordAnd and $authorIndex) {
						$authorstring .= ' and ';
						$prevWordAnd = 0;
					}
					$authorstring .= $this->spaceOutInitials($word);
					$namePart = 1;
					$this->debug("[2] Authorstring: " . $authorstring . ".  Name part: " . $namePart);
				} else {
					$prevWordAnd = 0;
					$authorstring .= " " . $this->trimRightBrace($this->spaceOutInitials(rtrim($word, ',')));
					$bareWords = $this->bareWords($remainingWords, !$hasAnd, $hasAnd);
					if($determineEnd and $this->getQuotedOrItalic(implode(" ", $remainingWords), true, false, $remains)) {
							$done = 1;
							$remainder = implode(" ", $remainingWords);
							$this->debug("[3] Authorstring: " . $authorstring . ".  Name part: " . $namePart);
					} elseif($determineEnd and $year = $this->getYear(implode(" ", $remainingWords), true, $remainder)) {
						$done = 1;
						$this->debug("[4] Authorstring: " . $authorstring . ".  Name part: " . $namePart);
					} elseif($determineEnd and 
								substr($word, -1) == '.' and strtolower(substr($word, -2, 1)) == substr($word, -2, 1)) {
						$done = 1;
						$this->debug("[5] Authorstring: " . $authorstring . ".  Name part: " . $namePart);
					} elseif($determineEnd and $bareWords > 2) {
						// Note that this check occurs only when $namePart >= 1---so it rules out double-barelled
						// family names that are not followed by commas.  ('Paulo Klinger Monteiro, ...' is OK.)
						// Cannot set limit to be > 1 bareWord, because then '... Smith, Nancy Lutz and' gets truncated
						// at comma.
						$done = 1;
						$this->debug("[6] Authorstring: " . $authorstring . ".  Name part: " . $namePart);
					} else {
						if(substr($word, -1) == ',' and !$this->isEd($words[$i+1], $hasAnd)) {
							if($hasAnd) {
								// Word is followed by comma and 'and' has already occurred
								// To cover the case of a last name containing a space, look ahead to see if next words
								// are initials or year.  If so, add back comma taken off above and continue.  Else done.
								if($i+3 < count($words) 
									and (
										$this->isInitials($words[$i+1])
										or $this->getYear($words[$i+2], true, $trash)
										or ($this->isInitials($words[$i+2]) and $this->getYear($words[$i+3], true, $trash))
										)
									) $authorstring .= ',';
								else $done = 1;
							} else {
								$namePart = 0;
								$authorIndex++;
							}
						} else $namePart++;
						$this->debug("[7] Authorstring: " . $authorstring . ".  Name part: " . $namePart);
					}
				}
			}
		}
		return $authorstring;
	}

	function isInitials($string) {
		for($i = 0; $i < strlen($string); $i = $i+2) {
			if($string[$i] != strtoupper($string[$i]) or ($i+1 < strlen($string) and $string[$i+1] != '.')) return false;
		}
		return true;
	}

	/*
	 * isEd: determine if string is 'Eds.' or '(Eds.)' or '(Eds)' or 'eds.' or '(eds.)' or '(eds)' and multiple == true or
	 * singular version if multiple == false.
	 * @param $string string
	 * @param $multiple boolean
	 */
	function isEd($string, $multiple = false) {
		if($multiple and preg_match('/^\(?[Ee]ds\.?\)?,?$/', $string)) return true;
		elseif(!$multiple and preg_match('/^\(?[Ee]d\.\)?,?$/', $string)) return true;
		else return false;		
	}

	/**
	 * getQuotedOrItalic: get first quoted or italicized substring in $string, restricting to start if $start
	 * is true and getting only italics if $italicsOnly is true.
	 * Quoted means starts with `` or unescaped " [though latter is wrong] and ends with '' or unescaped ".
	 * @param $string string
	 * @param $start boolean (if true, check only for substring at start of string)
	 * @param $italicsOnly boolean (if true, get only italic string, not quoted string)
	 * @param $remains what is left of the string after the substring is removed
	 * return quoted or italic substring
	 */
	function getQuotedOrItalic($string, $start, $italicsOnly, &$remains) {
		$quoted = '';
		$remains = $string;
		$quoteExists = 0;

		if($italicsOnly) $containsQuote = 0;
		else {
			$posQuote1 = strpos($string, "``");
			$lenQuote1 = 2;

			for($j=0; $j<strlen($string) and !($string[$j] == '"' and ($j == 0 or $string[$j-1] != '\\')); $j++) {}
			$posQuote2 = $j < strlen($string) ? $j : false;
			$lenQuote2 = 1;

			$containsQuote = 1;
			if($posQuote1 !== false and $posQuote2 !== false) {
				if($posQuote1 < $posQuote2) {
					$posQuote = $posQuote1;
					$lenQuote = $lenQuote1;
				} else {
					$posQuote = $posQuote2;
					$lenQuote = $lenQuote2;
				}
			} elseif($posQuote1 !== false) {
				$posQuote = $posQuote1;
				$lenQuote = $lenQuote1;
			} elseif($posQuote2 !== false) {
				$posQuote = $posQuote2;
				$lenQuote = $lenQuote2;
			} else $containsQuote = 0;
		}

		$containsItalics = $this->containsFontStyle($string, $start, 'italics', $posItalics, $lenItalics);

		if(
			($containsQuote and $containsItalics
				and (($start and $posQuote == 0) or (!$start and $posQuote < $posItalics)))
			or
			($containsQuote and !$containsItalics
				and (($start and $posQuote == 0) or !$start))) {
			// look for '' or " that isn't escaped
			for($j=$posQuote + $lenQuote; $j<strlen($string); $j++) {
				if($string[$j] == "'" and $string[$j+1] == "'") break;
				elseif($string[$j] == "\"" and $string[$j-1] != "\\") break;
			} 
			$pos = $posQuote;
			$len = $lenQuote;
			$quoteExists = 1;
		} elseif(
			($containsQuote and $containsItalics
				and (($start and $posItalics == 0) or (!$start and $posItalics < $posQuote)))
			or
			(!$containsQuote and $containsItalics
				and (($start and $posItalics == 0) or !$start))) {
			$this->italicTitle = true;
			// look for matching }
			$bracketLevel = 0;
			for($j=$posItalics+$lenItalics; $j<strlen($string); $j++) {
				if($string[$j] == '{') $bracketLevel++;
				elseif($string[$j] == '}') {
					if($bracketLevel) $bracketLevel--;
					else break;
				}
			}
			$pos = $posItalics;
			$len = $lenItalics;
			$quoteExists = 1;
		}

		if($quoteExists) {
			$quoted = rtrim(substr($string, $pos+$len, $j-$len-$pos), ',.');
			$quoted = $this->trimRightPeriod($quoted);
			$remains = substr($string, 0, $pos) . ltrim(substr($string, $j+1), "'" );
		}

		return $quoted;
	}

	/**
	 * getBold: get first boldface substring in $string, restricting to start if $start is true
	 * @param $string string
	 * @param $start boolean (if true, check only for substring at start of string)
	 * @param $remains what is left of the string after the substring is removed
	 * return bold substring
	 */
	function getBold($string, $start, &$remains) {
		$boldText = '';
		$remains = $string;

		$bracketLevel = 0;
		if($this->containsFontStyle($string, $start, 'bold', $posBold, $lenBold)) {
			for($j=$posBold+$lenBold; $j<strlen($string); $j++) {
				if($string[$j] == '{') $bracketLevel++;
				elseif($string[$j] == '}') {
					if($bracketLevel) $bracketLevel--;
					else break;
				}
			}
			$boldText = rtrim(substr($string, $posBold+$lenBold, $j-$posBold-$lenBold), ',');
			$boldText = $this->trimRightPeriod($boldText);
			$remains = rtrim(substr($string, 0, $posBold), ' .,') . ltrim(substr($string, $j+1), ' ,.');
		}

		return $boldText;
	}

	/**
	 * getYear: get first substring in $string that is a year, restricting to start if $start is true
	 * @param $string string
	 * @param $start boolean (if true, check only for substring at start of string)
	 * @param $remains what is left of the string after the substring is removed
	 * return bold substring
	 */
	function getYear($string, $start, &$remains) {
		$year = '';
		$remains = $string;

		// year can be in (1980), [1980], ' 1980 ', ' 1980,', ' 1980.', ' 1980)', or end with '1980' if not at start and
		// (1980), [1980], ' 1980 ', '1980,', '1980.', or '1980)' if at start; instead of 1980, can be of form
		// 1980/1 or 1980/81 or 1980-1 or 1980-81
		$yearRegExp = '((18|19|20)([0-9]{2})(-[0-9]{1,2}|\/[0-9]{1,2})?)[a-z]?';
		$regExp1 = '\(' . $yearRegExp . '\)';
		$regExp2 = '\[' . $yearRegExp . '\]';
		$regExp3 = $yearRegExp . '[ .,)]';
		$regExp4 = $yearRegExp . '$';
		if($start) $regExp = '^' . $regExp1 . '|^' . $regExp2 . '|^' . $regExp3;
		else $regExp = $regExp1 . '|' . $regExp2 . '| ' . $regExp3 . '|' . $regExp4;
		$regExp = '/' . $regExp . '/';

		preg_match($regExp, $string, $matches, PREG_OFFSET_CAPTURE);

		$matchIndexes = array(1, 5, 9, 13);
		foreach($matchIndexes as $i) {
			if(isset($matches[$i][0])) {
				$year = $matches[$i][0];
				$remains = rtrim(substr($string, 0, $matches[0][1]), '.,') . 
						ltrim(substr($string, $matches[0][1]+strlen($matches[0][0])), '.,');
			}
		}

		return $year;
	}

	/**
	 * trimRightPeriod: remove trailing period if preceding character is not uppercase letter
	 * @param $string string
	 * return trimmed string
	 */
	function trimRightPeriod($string) {
		if($string == '' or $string == '.') $trimmedString = '';
		elseif(strlen($string) == 1) $trimmedString = $string;
		elseif(substr($string, -1) == '.' and strtoupper(substr($string, -2, 1)) != substr($string, -2, 1))
			$trimmedString = substr($string, 0, -1);
		else $trimmedString = $string;

		return $trimmedString;
	}

	/**
	 * trimRightBrace: remove trailing brace if and only if string contains one more right brace than left brace
	 * (e.g. deals with author's name Andr\'{e})
	 * @param $string string
	 * return trimmed string
	 */
	function trimRightBrace($string) {
		if(substr($string, -1) == '}' and 
			substr_count($string, '}') - substr_count($string, '{') == 1) $trimmedString = substr($string, 0, -1);
		else $trimmedString = $string;

		return $trimmedString;
	}

	/**
	 * extractPublisherAndAddress
	 * @param $string string
	 * @param $address string
	 * @param $publisher string
	 * Assuming $string contains exactly the publisher and address, break it into those two components;
	 * return remaining string (if any)
	 */
	function extractPublisherAndAddress($string, &$address, &$publisher) {
		$containsPublisher = $containsCity = false;
		$string = trim($string, ' ().,');
		// If $string contains a single ':', take city to be preceding string and publisher to be
		// following string
		if(substr_count($string, ':') == 1) {
			// Work back from ':' looking for '(' not followed by ')'.  If found, take the following char to
			// be the start of the address (covers case like "extra stuff (New York: Addison-Wesley).
			$colonPos = strpos($string, ':');
			for($j = $colonPos; $j > 0 and $string[$j] != ')' and $string[$j] != '('; $j--) {}
			if($string[$j] == '(') {
				$remainder = substr($string, 0, $j);
				$string = substr($string, $j+1);
			} else $remainder = '';
			$address = rtrim(ltrim(substr($string, 0, strpos($string, ':')), ',. '), ': ');
			$publisher = trim(substr($string, strpos($string, ':')+1), ',.: ');
		// else if string contains no colon and at least one ',', take publisher to be string 
		// preceding first colon and and city to be rest
		} elseif(!substr_count($string, ':') and substr_count($string, ',')) {
			$publisher = trim(substr($string, 0, strpos($string, ',')), ',. ');
			$address = trim(substr($string, strpos($string, ',')+1), ',.: ');
			$remainder = '';
		// else take publisher/city to be strings that match list above and report rest to be
		// city/publisher
		} else {
			$stringMinusPubInfo = $string;
			foreach($this->publishers as $publisherFromList) {
				$publisherPos = strpos($string, $publisherFromList);
				if($publisherPos !== false) {
					$containsPublisher = true;
					$publisher = $publisherFromList;
					$stringMinusPubInfo = 
							substr($string, 0, $publisherPos) . substr($string, $publisherPos+strlen($publisherFromList));
					break;
				}
			}
			foreach($this->cities as $cityFromList) {
				$cityPos = strpos($stringMinusPubInfo, $cityFromList);
				if($cityPos !== false) {
					$containsCity = true;
					$address = $cityFromList;
					$stringMinusPubInfo = 
						substr($stringMinusPubInfo, 0, $cityPos) . substr($stringMinusPubInfo, $cityPos+strlen($cityFromList));
					break;
				}
			}

			// These two lines seem necessary---why??
			if(!$containsPublisher) $publisher = '';
			if(!$containsCity) $address = '';

			$remainder = $stringMinusPubInfo;
			// If only publisher has been identified, take rest to be city
			if($containsPublisher and !$containsCity) {
				$address = trim($remainder, ',.: }{ ');
				$remainder = '';
			// elseif publisher has not been identified, take rest to be publisher (whether or not city has been identified)
			} elseif(!$containsPublisher) {
				$publisher = trim($remainder, ',.: }{ ');
				$remainder = '';
			}
		}
		$address = ltrim($address, '} ');

		return $remainder;
	}

	// Report whether $string is a year between 1700 and 2100
	function isYear($string) {
		$number = (int) $string;
		if($number > 1700 and $number < 2100) return true;
		else return false;
	}

	/**
	 * bareWords: count number of words that do not end in ',' or '.' or ')' at the start of an array of words
	 * If $countAndAsPunct is true, count 'and' as punctuation
	 * @param $words array
	 * @param $countAndAsPunct boolean
	 */
	function bareWords($words, $countAndAsPunct, $hasAnd) {
		// an empty element is added to the end of $words to cover case in which no element has ending punctuation
		$words[] = "";
		foreach($words as $j=>$word) {
			if(in_array(substr($word, -1), array('.', ',', ')'))) break;
			if($countAndAsPunct and $word == 'and') {
				$hasAnd = 1;
				break;
			}
		}
		return $j;
	}

	/**
	 * spaceOutInitials: change A.B. to A. B.
	 * @param $string string
	 */
	function spaceOutInitials($string) {
		return preg_replace('/([A-Z])\.([A-Z])/', '$1. $2', $string);
	}

	/**
	 * convertToBibtex
	 * Main function to convert content of uploaded file or string
	 * @param $uploadfile
	 * @param $string
	 * If $string is supplied, it is used; else the content of $uploadfile is used
	 */
	function convertToBibtex($uploadfile, $string = null){

		$format = $this->formatDetect($uploadfile, $string);
		$this->debug("Format is $format");

		$item = new bibtex;
		$item->OriginalFormat = $format;

		$newEntryarray = array();
		$items = array();

		// $uploadfile is an array of lines in the uploaded file	
		if($format == false){
			echo "<br> Wrong format!!! <br>";
			return false;
		} elseif ($format == "generic"){
			// filearray is an array, with one line in each component
			// Each component has \n at the end
			if($string) $filearray = explode("\r\n", $string);
			else $filearray = file($uploadfile);

			$u = $truncated = 0;
			$entryarray = [];
			$entryarray[0] = '';
			// at blank lines, split file into strings, with comments removed
			foreach($filearray as $fileline){
				$fileline = rtrim($fileline); // trim \r and \n from end
				if($this->percentComment) $truncated = $this->uncomment($fileline);
				if(trim($fileline)) {
					$entryarray[$u] .= $fileline;
					if(!$truncated) $entryarray[$u] .= " ";
					if($this->itemSeparator == 'cr') {
						$u++;
						$entryarray[$u] = '';
					}
				} else {
					if($this->itemSeparator == 'line') {
						$u++;	
						$entryarray[$u] = '';
					}
				}
			}
		} else {
			if($string) $filestring = $string;
			else $filestring = file_get_contents($uploadfile);
			// array_slice: ignore component 0 (before first format string)
			$entryarray = array_slice(explode($format, $filestring), 1);

			foreach($entryarray as $u => $entry) {
				$entry = str_replace(array("\r\n", "\r"), "\n", $entry);
				$entryAsArray = explode("\n", $entry);
				$newEntryarray[$u] = '';
				for ($t=0; $t<count($entryAsArray); $t++){
					if($this->percentComment) $truncated = $this->uncomment($entryAsArray[$t]);
					if($truncated) $newEntryarray[$u] .= $entryAsArray[$t];
					else $newEntryarray[$u] .= $entryAsArray[$t] . " ";
				}
				$entryarray[$u] = $newEntryarray[$u];
			}
		}

		$this->displayLines[] = "<p><i>Current version of conversion algorithm: " . $this->version . "</i>";
		$num = count($entryarray);
		$message = '<p>' . $num . ' reference';
		if($num > 1) $message .= 's';
		$message .= ' found in your file.';
		if($num == 1) $message .= "  If you expected more to be found, perhaps your file has one reference per line but you didn't select the 'item separator' to be a carriage return?";
		$this->displayLines[] = $message;

		// Process each entry in turn			
		foreach($entryarray as $entry) {
			unset($item, $temp, $temparray, $label, $num, $numSpaces, $year, $authorfound, $authorstring);
			unset($done, $foundtitle, $authorarray, $titlearray, $thearray);

			$isArticle = $containsPageRange = false;
			$label = '';

			$warnings = array();

			// Clean up entry
			$entry = str_replace("\\textquotedblleft ", "``", $entry);
			$entry = str_replace("\\textquotedblright ", "''", $entry);
			$entry = str_replace("\\textquotedblright", "''", $entry);
			$entry = str_replace("\\ ", " ", $entry);
			$entry = str_replace("\\textbf{\\ }", " ", $entry);
			$entry = str_replace("~", " ", $entry);
			$entry = str_replace("\\/", "", $entry);
			$entry = str_replace("\x96", "-", $entry);
			// Delete ^Z and any trailing space (^Z will be at end of last entry of DOS file)
			$entry = rtrim($entry, " \032");
			$entry = ltrim($entry, ' ');

			// get the label
			if ($format == "\bibitem" and $entry[0] == "{"){
				for($j=1; $j<strlen($entry) and $entry[$j] != "}"; $j++) $label .= $entry[$j];
				$entry = substr($entry, $j+1);
				$item->label = trim($label, ' ');
			} else $item->label = ""; // label will be constructed later

			// Don't put the following earlier---{} may legitimately follow \bibitem
			$entry = str_replace("{}", "", $entry);

			// if entry starts with [n] or (n) (after removing $format string) for some number n, eliminate it
			$entry = preg_replace("/^\s*\[\d*\]|^\s*\(\d*\)/", "", $entry);

			$this->verbose("<hr size=1 noshade><font color=\"green\">Item:</font> ". $this->killhtml($entry));
			if($label) $this->verbose("<br>Label in your file: " . $this->killhtml($label));

			$entry = ltrim($entry, ' ');

			//////////////////////
			// Look for authors //
			//////////////////////

			unset($remainder);

			$words = explode(" ", $entry);
			$isEditor = false;
			$authorstring = $this->convertToAuthors($words, $remainder, $year, $isEditor);

			$authorstring = trim($authorstring, ', ');
			$authorstring = $this->trimRightBrace($authorstring);
			if($authorstring and $authorstring[0] == '{') $authorstring = strstr($authorstring, ' ');

			//////////////////////////
			// Fix up $authorstring //
			//////////////////////////

			if($isEditor === false
				and strpos($authorstring, '(editor)') === false 
				and strpos($authorstring, '(editors)') === false
				and strpos($authorstring, '(ed.)') === false
				and strpos($authorstring, '(eds.)') === false) 
					$item->author = $authorstring;
			else $item->editor = 
					trim(str_replace(array('(editor)', '(editors)', '(ed.)', '(eds.)'), "", $authorstring), ' ');

			if(isset($item->author)) $message = "Authors: " . $item->author;
			if(isset($item->editor)) $message = "Editors: " . $item->editor;
			if($year) $item->year = $year;

      		$this->verbose("<br>" . $this->killhtml($message));
			$this->debug("Remainder: " . $this->killhtml($remainder));

			////////////////////
			// Look for title //
			////////////////////

			unset($title, $this->italicTitle, $firstCommaPos);

			$remainder = ltrim($remainder, ': ');
			$title = $this->getQuotedOrItalic($remainder, true, false, $newRemainder);

			if(!$title) {
				// Look for comma or period (or ? or !).  If period found first and is not followed by lowercase letter,
				// take that to be end of title.  If
				// comma found first, look to see if following string starts italics, starts with working paper
				// string, starts with 'in ', or starts with a year since 1900 followed by a period (case of a
				// working paper without any institution); if so, take that to be end of title.  (Assumption: 
				// 'in ' can occur in a title, but is very unlikely after a comma.)  If comma found first and
				// is at least second comma in remainder and string from the comma to the next comma or period contains no
				// letters, then take item to be article (assume string with no letters is volume/number, with
				// the title the string up to the previous comma).
				// Else continue searching.  If reach end of string, take title to be string
				// up to first comma. 
				$numberOfCommas = 0;
				for($j=0; $j<strlen($remainder) and !$title; $j++) {
					// find index of first nonspace after $remainder[$j]
					for($k = $j+1; $remainder[$k] == ' '; $k++) {}
					switch($remainder[$j]) {
						case '!':
						case '?':
						case '.':
							// period doesn't terminate if followed by lowercase letter (covers case of abbreviation in
							// title).
							if(strtolower($remainder[$k]) == $remainder[$k]) {
							} elseif($j < strlen($remainder)-1) {
								$title = rtrim(substr($remainder, 0, $j+1), '.');
								$newRemainder = ltrim(substr($remainder, $j+2), ' ');
							} elseif($firstCommaPos) {
								$title = rtrim(substr($remainder, 0, $firstCommaPos), ',');
								$newRemainder = ltrim(substr($remainder, $firstCommaPos+1), ' ');
							} else {
								$title = rtrim(substr($remainder, 0, $j), '.');
								$newRemainder = ltrim(substr($remainder, $j+1), ' ');
							}
							break;
						case ',':
							if(!isset($firstCommaPos)) $firstCommaPos = $j;
							$numberOfCommas++;
						case ' ':
							$rest = ltrim(substr($remainder, $j+1), ' ');
							$this->debug("Rest: " . $rest);
							$regExp = '/^' . $this->workingPaperRegExp . '/';
							if($remainder[$j] == ',') {
								$commaPos = strpos($rest, ',');
								$periodPos = strpos($rest, '.');
								if($commaPos !== false) {
									if($periodPos !== false) $stringBeforeNextComma = substr($rest,0,min($commaPos, $periodPos));
									else $stringBeforeNextComma = substr($rest, 0, $commaPos);
								} elseif($periodPos !== false) $stringBeforeNextComma = substr($rest, 0, $periodPos);
								else $stringBeforeNextComma = '';
								$this->debug("String before next comma or period: " . $stringBeforeNextComma);
							}
							if($this->containsFontStyle($rest, true, 'italics', $startPos, $length) 
								  or preg_match($regExp, $rest, $matches)
								  or preg_match('/^(pages|pp.) [1-9]/', $rest, $matches)
								  or ($remainder[$j] == ',' and substr($rest, 0, 3) == 'in ')
								  or ($remainder[$j] == ',' and preg_match('/^(19|20)[0-9][0-9]\./', $rest))) {
								$this->debug("Case A");
								$title = rtrim(substr($remainder, 0, $j), ',');
								$newRemainder = ltrim(substr($remainder, $j+1), ' ');
							} elseif($remainder[$j] == ',' 
										and $numberOfCommas > 1 
										and preg_match('/^[^A-Za-z]+$/', $stringBeforeNextComma)){
								$this->debug("Case B");
								$isArticle = true;
								$remainderArray = explode(",", substr($remainder, 0, $j));
								array_pop($remainderArray);
								$title = implode(",", $remainderArray);
								$newRemainder = ltrim(substr($remainder, strlen($title)), ' ');
							}
							break;
					}
				}
			}

			$remainder = $newRemainder;
			$item->title = $title;

			$this->verbose("<br>Title: " . $this->killhtml($title));
			$this->debug("Remainder: " . $this->killhtml($remainder));

			////////////////////////////////////////
			// Look for year if not already found //
			////////////////////////////////////////

			if(!$year) $year = $this->getYear($remainder, false, $newRemainder);

			if($year) $item->year = $year;
			else {
				$item->year = '';
				$warnings[] = "No year found.";
			}

			$remainder = ltrim($newRemainder, ' ');

			$this->verbose("<br>Year: " . $this->killhtml($item->year));

			////////////////////////////
			// Determine type of item //
			////////////////////////////

			// $remainder is item minus authors, year, and title
			$remainder = ltrim($remainder, '., ');
			$this->debug("[type] Remainder: " . $this->killhtml($remainder));
			unset($city, $publisher, $type, $number, $institution, $booktitle, $workingPaperMatches);
			$inStart = $italicStart = $containsBoldface = $containsEditors = $containsThesis = false;
			$containsWorkingPaper = $containsNumber = $containsCity = $containsPublisher = false;
			$containsNumberedWorkingPaper = $containsNumber = $containsForthcoming = false;
			$cityLength = $publisherLength = 0;

			if(substr($remainder, 0, 3) == "in " or substr($remainder, 0, 3) == "In ") {
				$inStart = true;
				$this->debug("Starts with \"in\".");
			}

			if($this->containsFontStyle($remainder, true, 'italics', $startPos, $length)) {
				$italicStart = true;
				$this->debug("Starts with italics.");
			}

			if(preg_match('/\d/', $remainder)) {
				$containsNumber = true;
				$this->debug("Contains a number.");
			}

			// 1st|2nd ... stuff in second preg_match is to exclude a string like '1st ed.'
			if(preg_match('/\([Ee]ds?\.?\)|\([Ee]ditors?\)/', $remainder) or preg_match('/[^1st|2nd|3rd|4th] [Ee]ds?\.|^[Ee]ds?\.| [Ee]ditors?/', $remainder)) {
				$containsEditors = true;
				$this->debug("Contains editors.");
			}

			if(preg_match('/[ :][1-9][0-9]{0,3} ?-{1,2} ?[1-9][0-9]{0,3}([\.,\} ]|$)/', $remainder)) {
				$containsPageRange = true;
				$this->debug("Contains page range.");
			}

			$regExp = '/' . $this->workingPaperRegExp . ' (\\\\#|[Nn]umber)? ?(\d{0,5})/';
			if(preg_match($regExp, $remainder, $workingPaperMatches, PREG_OFFSET_CAPTURE)) {
				$containsNumberedWorkingPaper = true;
				$this->debug("Contains string for numbered working paper.");
			}

			$regExp = '/' . $this->workingPaperRegExp . '/';
			if(preg_match($regExp, $remainder)) {
				$containsWorkingPaper = true;
				$this->debug("Contains string for working paper.");
			}

			if(substr_count($remainder, '\\#')) {
				$containsNumber = true;
				$this->debug("Contains number sign (\\#).");
			}

			if(preg_match('/ [Tt]hesis/', $remainder)) {
				$containsThesis = true;
				$this->debug("Contains thesis.");
			}

			if($this->containsFontStyle($remainder, false, 'bold', $startPos, $length)) {
				$containsBoldface = true;
				$this->debug("Contains string in boldface.");
			}

			if(substr_count($remainder, 'forthcoming')) {
				$containsForthcoming = true;
				$this->debug("Contains string 'forthcoming'.");
			}

			$remainderMinusPubInfo = $remainder;
			foreach($this->publishers as $publisher) {
				$publisherPos = strpos($remainder, $publisher);
				if($publisherPos !== false) {
					$containsPublisher = true;
					$publisherLength = strlen($publisher);
					$remainderMinusPubInfo = 
							substr($remainder, 0, $publisherPos) . substr($remainder, $publisherPos+$publisherLength);
					$this->debug("Contains publisher \"" . $publisher . "\"");
					break;
				}
			}

			// Check for cities only in $remainder minus publisher, if any.
			foreach($this->cities as $city) {
				$cityPos = strpos($remainderMinusPubInfo, $city);
				if($cityPos !== false) {
					$containsCity = true;
					$cityLength = strlen($city);
					$remainderMinusPubInfo = 
						substr($remainderMinusPubInfo, 0, $cityPos) . substr($remainderMinusPubInfo, $cityPos+$cityLength);
					$this->debug("Contains city \"" . $city . "\"");
					break;
				}
			}

			$commaCount = substr_count($remainder, ',');
			$this->debug("Number of commas: " . $commaCount);

			if(isset($this->italicTitle)) $this->debug("Italic title");

			if($isArticle or ($italicStart and $containsPageRange and !$containsEditors)) $item->kind = 'article';
			elseif($containsNumberedWorkingPaper or ($containsWorkingPaper and $containsNumber)) $item->kind = 'techreport';
			elseif($containsWorkingPaper or !$remainder) $item->kind = 'unpublished';
			elseif($containsEditors and ($inStart or $containsPageRange)) $item->kind = 'incollection';
			elseif($containsEditors) {
				$item->kind = 'incollection';
				$warnings[] = "Not sure of type; guessed to be " . $item->kind;
			}
			elseif($containsPageRange) {
				/** $commaCount criterion doesn't seem to be useful
				if($commaCount < 6) $item->kind = 'article';
				else $item->kind = 'incollection';
				**/
				$item->kind = 'article';
				$warnings[] = "Not sure of type; guessed to be " . $item->kind;
			}
			elseif(isset($this->italicTitle) and ($containsCity or $containsPublisher) or isset($item->editor)) $item->kind = 'book';
			elseif($containsForthcoming) $item->kind = 'article';
			elseif($containsPublisher or $inStart) {
				if(strlen($remainder) - $cityLength - $publisherLength < 30) $item->kind = 'book';
				else $item->kind = 'incollection';
				$warnings[] = "Not sure of type; guessed to be " . $item->kind;
			} elseif(!$containsNumber or !$containsPageRange) {
				if($containsThesis) $item->kind = 'thesis';
				else $item->kind = 'book';
				$warnings[] = "Note sure of type; guessed to be " . $item->kind;
			} else {
				$item->kind = 'article';
				$warnings[] = "Really not sure of type; has to be something, so set to " . $item->kind;
			}

			// Whether thesis is ma or phd is determined later
			if($item->kind != 'thesis') $this->verbose("<br>Item type: <font color=\"black\">" . $item->kind . "</font>");

			unset($journal, $volume, $pages);

			// Remove ISBN if any and put in note field.
			if($item->kind == 'book' or $item->kind == 'incollection') {
				$numberOfMatches = preg_match('/(ISBN [0-9X]+)/', $remainder, $matches, PREG_OFFSET_CAPTURE);
				if($numberOfMatches) {
					$item->note = $matches[1][0];
					$take = $matches[1][1];
					$drop = $matches[1][1] + strlen($matches[1][0]);
					$remainder = substr($remainder, 0, $take) . substr($remainder, $drop);
					$this->verbose("<br>Note: " . $item->note);
				}
			}

			switch($item->kind) {

			/////////////////////////////////////////////
			// Get publication information for article //
			/////////////////////////////////////////////

				case 'article':
					// Get journal
					// If remainder starts with italics, italicized text is journal
					$remainder = ltrim($remainder, '., ');

					if($italicStart) $journal = $this->getQuotedOrItalic($remainder, true, false, $remainder);
					// else journal is string up to first comma, period, or number
					else {
						for($j=0; $j<strlen($remainder); $j++) {
							// if($remainder[$j] == ',' or $remainder[$j] == '.' or $j == strlen($remainder)-1
							// Case of comma removed to allow commas in journal titles
							if($remainder[$j] == '.' or $j == strlen($remainder)-1
								or in_array($remainder[$j], range('1', '9'))) {
								$journal = rtrim(substr($remainder, 0, $j), ', ');
								$remainder = ltrim(substr($remainder, $j), ',.');
								break;
							}
						}
					}

					$item->journal = $journal;
					if($item->journal) $this->verbose("<br>Journal: " . $this->killhtml($item->journal));
					else $warnings[] = "'Journal' field not found.";
					$this->debug("Remainder: " . $remainder);

					// Get pages
					$numberOfMatches = preg_match_all('/(pp.)?( )?([1-9][0-9]{0,4} ?-{1,2} ?[0-9]{1,5})/', $remainder, 
							$matches, PREG_OFFSET_CAPTURE);
					if($numberOfMatches) $matchIndex = $numberOfMatches - 1;
					$this->debug("Number of matches for a potential page range: " . $numberOfMatches);
					$this->debug("Match index: " . $matchIndex);
					if($numberOfMatches) {
						$item->pages = str_replace('--', '-', $matches[3][$matchIndex][0]);
						$item->pages = str_replace(' ', '', $item->pages);
						$take = $matches[0][$matchIndex][1];
						$drop = $matches[3][$matchIndex][1] + strlen($matches[3][$matchIndex][0]);
					} else {
						$item->pages = '';
						$take = 0;
						$drop = 0;
					}

					$remainder = rtrim(substr($remainder, 0, $take) . substr($remainder, $drop), ',.: ');
					$remainder = trim($remainder, ',. ');

					if($item->pages) $this->verbose("<br>Pages: " . $this->killhtml($item->pages));
					else $warnings[] = "'Pages' field not found.";
					$this->debug("Remainder: " . $remainder);

					// Get volume and number
					if(is_numeric($remainder)) {
						$item->volume = $remainder;
						$remainder = '';
					} elseif($this->containsFontStyle($remainder, false, 'bold', $startPos, $length)) {
						$item->volume = $this->getBold($remainder, false, $remainder);
					} else {
						// $item->number can be a range (e.g. '6-7')
						$numberOfMatches = 
								preg_match('/([1-9][0-9]{0,3})(, |\(| | \(|\.|:)([Nn]o.)?( )?([1-9][0-9]{0,3})(-[1-9][0-9]{0,3})?\)?/',
									$remainder, $matches, PREG_OFFSET_CAPTURE);
						if($numberOfMatches) {
							$item->volume = $matches[1][0];
							$item->number = $matches[5][0];
							if(isset($matches[6][0])) $item->number .= $matches[6][0];
							$match6 = isset($matches[6][0]) ? $matches[6][0] : '';	
							$take = $matches[1][1];
							$drop = $matches[1][1] + strlen($matches[1][0]) + strlen($matches[2][0]) + strlen($matches[3][0])
									+ strlen($matches[4][0]) + strlen($matches[5][0]) + strlen($match6);
						} else {
							$item->volume = $item->number = '';
							$take = $drop = 0;
						}
						$remainder = substr($remainder, 0, $take) . substr($remainder, $drop);
						$remainder = rtrim($remainder, ',. )');
					}

					if(isset($item->volume) and $item->volume) $this->verbose("<br>Volume: " . $this->killhtml($item->volume));
					else $warnings[] = "'Volume' field not found.";
					if(isset($item->number) and $item->number) $this->verbose("<br>Number: " . $this->killhtml($item->number));

					break;

			/////////////////////////////////////////////////
			// Get publication information for unpublished //
			/////////////////////////////////////////////////

				case 'unpublished':
					$item->note = trim($remainder, '., }');
					$remainder = '';
					if($item->note) $this->verbose("<br>Note: " . $this->killhtml($item->note));
					else $warnings[] = "Mandatory 'note' field missing.";
					break;

			////////////////////////////////////////////////
			// Get publication information for techreport //
			////////////////////////////////////////////////

				case 'techreport':
					// If string before type, take that to be institution, else take string after number
					// to be institution---handles both 'CORE Discussion Paper 34' and 'Discussion paper 34, CORE'
					$item->type = isset($workingPaperMatches[1][0]) ? $workingPaperMatches[1][0] : '';
					$item->number = isset($workingPaperMatches[3][0]) ? $workingPaperMatches[3][0] : '';
					if(isset($workingPaperMatches[0][1]) and $workingPaperMatches[0][1] > 0) {
						// Chars before 'Working Paper'
						$item->institution = trim(substr($remainder, 0, $workingPaperMatches[0][1]-1), ' .,');
						$remainder = trim(substr($remainder, $workingPaperMatches[3][1]+strlen($item->number)), ' .,');
					} else {
						// No chars before 'Working paper'---so take string after number to to institution
						$n = isset($workingPaperMatches[3][1]) ? $workingPaperMatches[3][1] : 0;
						$item->institution = trim(substr($remainder, $n+strlen($item->number)), ' .,');
						$remainder = '';
					}

					if($item->type) $this->verbose("<br>Type: " . $this->killhtml($item->type));
					if($item->number) $this->verbose("<br>Number: " . $this->killhtml($item->number));
					if($item->institution) $this->verbose("<br>Institution: " . $this->killhtml($item->institution));
					else $warnings[] = "Mandatory 'institition' field missing";
					$warnings[] = "Check institution.";
					break;

			//////////////////////////////////////////////////
			// Get publication information for incollection //
			//////////////////////////////////////////////////

				case 'incollection':
					$leftover = '';
					$pubInfoInParens = false;
					$this->debug("[in1] Remainder: " . $remainder);
					if($inStart) $remainder = ltrim(substr($remainder, 2), ' ');

					// Get pages and remove them from $remainder
					preg_match('/(\()?(pp.|pages)?( )?([1-9][0-9]{0,4} ?-{1,2} ?[0-9]{1,5})(\))?/', $remainder, 
							$matches, PREG_OFFSET_CAPTURE);
					if(isset($matches[4][0])) {
						$item->pages = str_replace('--', '-', $matches[4][0]);
						$item->pages = str_replace(' ', '', $item->pages);
					} else {
						$item->pages = '';
					}
					if($item->pages) $this->verbose("<br>Pages: " . $this->killhtml($item->pages));
					else $warnings[] = "Pages not found.";

					$take = isset($matches[0][1]) ? $matches[0][1] : 0;
					$drop = isset($matches[0]) ? $matches[0][1]+strlen($matches[0][0]) : 0;
					$remainder = substr($remainder, 0, $take) . substr($remainder, $drop);
					$remainder = ltrim($remainder, ' ');
					// Next case occurs if remainder previously was like "pages 2-33 in ..."
					if(substr($remainder, 0, 3) == 'in ') $remainder = substr($remainder, 3);
					$this->debug("[in2] Remainder: " . $remainder);

					// Try to find book title
					$editorStart = false;
					$newRemainder = $remainder;
					$editorStartRegExp = '/^\(?[Ee]ds?\.?|^\([Ee]ditors?/';
					// If a string is quoted or italicized, take that to be book title
					$booktitle = $this->getQuotedOrItalic($remainder, false, false, $newRemainder);

					if(!$booktitle) {
						// If no string is quoted or italic, try to determine whether $remainder starts with
						// title or editors.
						if(preg_match($editorStartRegExp, $remainder)) {
							$editorStart = true;
							$remainder = ltrim(strstr($remainder, ' '), ' ');
							$this->debug("[in3] Remainder: " . $remainder);
							if(substr($remainder, 0, 4) == 'and ') {
								// In this case, the string starts something like 'ed. and '.  Assume the next
								// word is something like 'translated', and drop it
								$words = explode(" ", $remainder);
								$leftover = array_shift($words);
								$leftover .= " " . array_shift($words);
								$warnings[] = "Don't know what to do with: " . $leftover;
								$remainder = implode(" ", $words);
							}
						} else {
							$numberSpaces = 0;
							for($j=0; $j<strlen($remainder) and $numberSpaces < 3; $j++) {
								// If period after first or second word and previous char is uppercase,
								// assume $remainder starts with editors.  How else to detect start with editors???
								if($remainder[$j] == ' ') {
									$numberSpaces++;
									if($j > 1 and $remainder[$j-1] == '.' and strtoupper($remainder[$j-2])==$remainder[$j-2]) {
										$editorStart = true;
										break;
									}
								}
							}
						}
						if($editorStart) {
							$this->debug("Remainder starts with editor string");
							$words = explode(' ', $remainder);
							// $isEditor is used only for a book (with an editor, not an author)
							$isEditor = false;
							$item->editor = trim($this->convertToAuthors($words, $remainder, $trash2, $isEditor, true), '() ');
							$newRemainder = $remainder;
						} else {
							$this->debug("Remainder starts with book title");
							// Take title to be string up to first comma or period
							for($j=0; $j<strlen($remainder) and !$booktitle; $j++) {
								if($remainder[$j] == '.' or $remainder[$j] == ',') {
									$booktitle = substr($remainder, 0, $j);
									$newRemainder = rtrim(substr($remainder, $j+1), ',. ');
								}
							}
						}
					}
					// At this point, either $booktitle is defined and $remainder starts with editors OR $item->editor is
					// defined and remainder starts with booktitle.

					$remainder = ltrim($newRemainder, ", ");
					$this->debug("[in4] remainder: " . $remainder); 

					// Get editors
					if($booktitle) {
						if(preg_match($editorStartRegExp, $remainder)) {
							$this->debug("Remainder starts with string for editors.");
							// If $remainder starts with "ed." or "eds.", guess that potential editors end at period or '(' 
							// (to cover case of publication info in parens) preceding 
							// ':' (which could separate publisher and city), if such exists.
							$colonPos = strpos($remainder, ':');
							if($colonPos !== false) {
								// find previous period
								for($j=$colonPos; $j>0 and $remainder[$j]!='.' and $remainder[$j] != '('; $j--) {}
								$this->debug("j is " . $j);
								$editor = trim(substr($remainder, 3, $j-3), ' .,');
								$this->debug("Editor is: " . $editor);
								$newRemainder = substr($remainder, $j);
							} else {
								$warnings[] = "Unable to determine editors.";
							}
						} else {
							// Else editors are part of $remainder up to " ed." or "(ed.)" etc.
							$numberOfMatches = preg_match('/( [Ee]d[\. ]|\([Ee]d\.?\)| [Ee]ds[\. ]|\([Ee]ds\.?\)| [Ee]ditor| [Ee]ditors| \([Ee]ditor\)| \([Ee]ditors\))/',
										$remainder, $matches, PREG_OFFSET_CAPTURE);
							$take = $numberOfMatches ? $matches[0][1] : 0;
							$match = $numberOfMatches ? $matches[0][0] : '';
							$editor = rtrim(substr($remainder, 0, $take), '., ');
							$newRemainder = substr($remainder, $take+strlen($match));
						}

						$words = explode(' ', ltrim($editor, ','));
						// Let convertToAuthors figure out where editors end, in case some extra text appears after editors,
						// before publication info.  Not sure this is a good idea: if convertToAuthors works very well, could
						// be good, but if it doesn't, might be better to take whole string.  If revert to not letting
						// convertToAuthors determine end of string, need to redefine remainder below.
						$isEditor = false;
						$item->editor = trim($this->convertToAuthors($words, $remainder, $trash2, $isEditor, true), '() ');
						//$item->editor = trim($this->convertToAuthors($words, &$trash1, $trash2, false), '() ');
						$remainder = $remainder . ltrim($newRemainder, ' ,');
					} else {
						// Case in which $booktitle is not defined: remainder presumably starts with booktitle
						$this->debug("[in5] Remainder: " . $remainder);
						// $remainder contains book title and publication info.  Need to find boundary.  Temporarily drop last
						// word from remainder, then any initials (which are presumably part of the publisher's name), then 
						// the previous word.  In what is left, take the booktitle to end at the first period 
						$words = explode(" ", $remainder);
						$n = count($words);
						for($j = $n-2; $j > 0 && $this->isInitials($words[$j]); $j--) {}
						$potentialTitle = implode(" ", array_slice($words, 0, $j));
						$this->debug("Potential title: " . $potentialTitle);
						$periodPos = strpos(rtrim($potentialTitle, '.'), '.');
						if($periodPos !== false) {
							$booktitle = trim(substr($remainder, 0, $periodPos), ' .,');
							$remainder = substr($remainder, $periodPos);
						} else {
							// Does whole entry end in ')' or ').'?  If so, pubinfo is in parens, so booktitle ends 
							// at previous '('; else booktitle is all of $potentialTitle
							if($entry[strlen($entry)-1] == ')' or $entry[strlen($entry)-2] == ')')
										$booktitle = substr($remainder, 0, strrpos($remainder, '('));
							else $booktitle = $potentialTitle;
							$remainder = substr($remainder, strlen($booktitle));
							/*****
							//Old code, before $potentialTitle was constructed:
							//$booktitle is $remainder up to ', ' or '. ' or ': ' or ') ' string preceding first colon
							$colonPos = strpos($remainder, ':');
							if($colonPos !== false) {
								// find previous space
								for($j=$colonPos; $j>0 
										and substr($remainder, $j-2, 2) != ', ' 
										and substr($remainder, $j-2, 2) != '. '
										and substr($remainder, $j-2, 2) != ': '
										and substr($remainder, $j-2, 2) != ') '
										and substr($remainder, $j-2, 2) != '. '; $j--) {}
								$booktitle = trim(substr($remainder, 0, $j), ' .,');
								$remainder = substr($remainder, $j);
							} else {
								$warnings[] = "Unable to determine book title.";
							}
							*****/
						}
					}

					if($item->editor) $this->verbose("<br>Editors: " . $this->killhtml($item->editor));
					else $warnings[] = "Editor not found.";

					$this->debug("[in6] remainder: " . $remainder); 
					// Whatever is left is publisher and address
					$newRemainder = $this->extractPublisherAndAddress($remainder, $address, $publisher);

					$item->publisher = $publisher;
					if($item->publisher) $this->verbose("<br>Publisher: " . $this->killhtml($item->publisher));
					else $warnings[] = "Publisher not found.";

					$item->address = $address;
					if($item->address) $this->verbose("<br>Address: " . $this->killhtml($item->address));
					else $warnings[] = "Address not found.";

					$booktitle = rtrim($booktitle, '.');
					$item->booktitle = $booktitle;
					if($item->booktitle) $this->verbose("<br>Book title: " . $this->killhtml($item->booktitle));
					else $warnings[] = "Book title not found.";

					if($leftover) $leftover = $leftover . ';';
					$remainder = $leftover . " " . $newRemainder;
					$this->debug("Remainder: " . $remainder);
					break;


			//////////////////////////////////////////
			// Get publication information for book //
			//////////////////////////////////////////

				case 'book':
					// If remainder contains word 'edition', take previous word as the edition number
					$remainingWords = explode(" ", $remainder);
					foreach($remainingWords as $key => $word) {
						if($key and (strtolower(trim($word, ',. ')) == 'edition' or strtolower(trim($word, ',. ')) == 'ed')) {
							$item->edition = trim($remainingWords[$key-1], ',. ');
							$this->verbose("<br>Edition: " . $this->killhtml($item->edition));
							array_splice($remainingWords, $key-1, 2);
							break;
						}
					}

					// If remainder contains word 'volume', take next word to be volume number, and if
					// following word is "in", take string up to next comma to be series name
					foreach($remainingWords as $key => $word) {
						if(count($remainingWords) > $key+1 and strtolower(trim($word, ',. ')) == 'volume') {
							$item->volume = trim($remainingWords[$key+1], ',. ');
							$this->verbose("<br>Volume: " . $this->killhtml($item->volume));
							array_splice($remainingWords, $key, 2);
							$series = array();
							if(strtolower($remainingWords[$key]) == 'in') {
								for($k=$key+1; $k<count($remainingWords); $k++) {
									$series[] = $remainingWords[$k];
									if(substr($remainingWords[$k], -1) == ',') {
										if($series[0][0] == "\\" or substr($series[0], 0, 2) == "{\\") array_shift($series);
										$item->series = trim(implode(" ", $series), '.,}');
										$this->verbose("<br>Series: " . $this->killhtml($item->series));
										array_splice($remainingWords, $key, $k - $key + 1);
										break;
									}
								}
							}
							break;
						}
					}

					$remainder = implode(" ", $remainingWords);
					// If string is in italics, get rid of the italics
					if($this->containsFontStyle($remainder, true, 'italics', $startPos, $length))
								$remainder = rtrim(substr($remainder, $length), '}');

					$remainder = $this->extractPublisherAndAddress($remainder, $address, $publisher);

					$item->publisher = $publisher;
					if($item->publisher) $this->verbose("<br>Publisher: " . $this->killhtml($item->publisher));
					else $warnings[] = "No publisher identified.";

					$item->address = $address;
					if($item->address) $this->verbose("<br>Publication city: " . $this->killhtml($item->address));
					else $warnings[] = "No place of publication identified.";

					break;

			////////////////////////////////////////////
			// Get publication information for thesis //
			////////////////////////////////////////////

				case 'thesis':
					$thesisTypeFound = 0;
					// If remainder contains comma, previous word as the edition number
					$commaPos = strpos($remainder, ',');
					if($commaPos !== false) {
						$beforeComma = substr($remainder, 0, $commaPos);
						$afterComma = substr($remainder, $commaPos);
						if(strstr(strtolower($afterComma), 'thesis')) {
							$thesisString = $afterComma;
							$item->school = trim($beforeComma, ' .,');
						} else {
							$thesisString = $beforeComma;
							$item->school = trim($afterComma, ' .,');
						}
						if(preg_match('/[Mm]aster|MA|M.A./', $thesisString, $matches, PREG_OFFSET_CAPTURE)) {
								$item->kind = 'mastersthesis';
								$thesisTypeFound = 1;
						} elseif(preg_match('/PhD|Ph.D.|Ph. D.|Ph.D|[Dd]octoral/', $thesisString, $matches, PREG_OFFSET_CAPTURE)) {
								$item->kind = 'phdthesis';
								$thesisTypeFound = 1;
						} else {
							$item->kind = 'phdthesis';
							$warnings[] = "Can't determine whether MA or PhD thesis; set to be PhD thesis.";
						}
					} else {
						if(preg_match('/[Mm]aster|MA|M.A./', $remainder, $matches, PREG_OFFSET_CAPTURE)) {
							$item->kind = 'mastersthesis';
							$thesisTypeFound = 1;
						} elseif(preg_match('/PhD|Ph.D.|[Dd]octoral/', $remainder, $matches, PREG_OFFSET_CAPTURE)) {
							$item->kind = 'phdthesis';
							$thesisTypeFound = 1;
						} else {
							$item->kind = 'phdthesis';
							$warnings[] = "Can't determine whether MA or PhD thesis; set to be PhD thesis.";
						}
						
						$item->school = trim($remainder, ' .,');
					}


					if($thesisTypeFound) {
						$thesisString = substr($thesisString, 0, $matches[0][1]) . 
													substr($thesisString, $matches[0][1] + strlen($matches[0][0]));
					}

					$j = strpos(strtolower($thesisString), 'thesis');
					// $j shouldn't be false, else the item would not have been identified as a thesis
					if($j !== false) $thesisString = substr($thesisString, 0, $j) . substr($thesisString, $j+6);
					$thesisString = trim($thesisString, ' .,');

					$this->verbose("<br>Item type: <font color=\"black\">" . $item->kind . "</font>");

					if($item->school) $this->verbose("<br>School: " . $this->killhtml($item->school));
					else $warnings[] = "No school identified.";

					$remainder = $thesisString;

					break;
			}

			$remainder = trim($remainder, '.,:;}{ ');
			if($remainder) {
				$item->unidentified = $remainder;
				$warnings[] = "The string \"" . $remainder . "\" remains unidentified";
			}

			foreach($warnings as $warning) {
				$this->verbose("<br><font color=\"red\">Warning:</font> " . $this->killhtml($warning));
			}

			$items[] = $item;

		}

		return $items;
	}

	/**
	 * onlyLetters
	 * @param $string string
	 * Returns string consisting only of letters and spaces in $string
	 */
	function onlyLetters($string) {
		$str = '';
		for($j=0; $j<strlen($string); $j++) {
			if(($string[$j] >= 'a' and $string[$j] <= 'z') or ($string[$j] >= 'A' and $string[$j] <= 'Z') 
				or $string[$j] == ' ') $str .= $string[$j];
		}
		return $str;
	}

	/**
	 * addFields
	 * Adds to the string output each element $name in $names if $item->$name exists
	 * @param $names array of names of fields (e.g. array('author', 'title'))
	 * @param $item
	 * @param $output string
	 */
	function addFields($names, $item, &$output, $cr) {
		foreach($names as $name) if(isset($item->$name)) $output .= $name . " = {" . $item->$name . "}," . $cr;
	}

	/**
	 * formBibtex
	 * @param $items array of items
	 */
	function formBibtex($items){
		$labels = array();
		$output = '';
		foreach($items as $item) {
			// Create label if not present in original file or if overrideLabels is set
			if($item->label == "" or $this->overrideLabels){
				$label = '';
				if($item->author) $authors = explode(" and ", $item->author);
				elseif(isset($item->editor)) $authors = explode(" and ", $item->editor);
				foreach($authors as $author) {
					$authorLetters = $this->onlyLetters($author);
					if($pos = strpos($author, ',')) {
						if($this->labelStyle == 'short') $label .= $authorLetters[0];
						else $label .= substr($authorLetters, 0, $pos);
					} else {
						if($this->labelStyle == 'short') $label .= substr(trim(strrchr($authorLetters, ' '), ' '), 0, 1);
						else $label .= trim(strrchr($authorLetters, ' '), ' ');
					}
				}

				if($this->labelStyle == 'short') {
					$label = strtolower($label);
					$label .= substr($item->year, 2);
				} else $label .= $item->year;

				$item->label = $label;
			}

			if($this->lineEndings == 'w') $cr = "\r\n";
			elseif($this->lineEndings == 'l') $cr = "\n";

			// avoid duplicate labels: add "a", "b", ... to potential duplicates
			// ($baseLabels is an array of the labels before the suffixes are added)
			unset($values);
			$baseLabels = array();
			if(in_array($item->label, $baseLabels)) $values = array_count_values($baseLabels);
			$baseLabels[] = $item->label;
			if(isset($values)) $item->label .= chr(96 + $values[$item->label]);

			$output .= "@" . $item->kind . "{" . $item->label . "," . $cr;

			switch($item->kind) {
				case 'article':
					$fields = array('author', 'title', 'journal', 'year', 'volume', 'number', 'pages');
					break;
				case 'book':
					$fields = array('author','editor','title','edition','volume','series', 'year', 'address', 'publisher','note');
					break;
				case 'techreport':
					$fields = array('author', 'title', 'year', 'number', 'institution', 'note', 'type');
					break;
				case 'incollection':
					$fields = array('author', 'title', 'booktitle', 'year', 'publisher', 'address', 'editor', 'pages', 'note');
					break;
				case 'unpublished':
					$fields = array('author', 'title', 'year', 'note');
					break;
				case 'mastersthesis':
					$fields = array('author', 'title', 'school', 'year', 'note');
					break;
				case 'phdthesis':
					$fields = array('author', 'title', 'school', 'year', 'note');
					break;
			}

			$fields[] = 'unidentified';

			$this->addFields($fields, $item, $output, $cr);

			$output .= "}" . $cr . $cr;
		}
		return $output;
	}
}
