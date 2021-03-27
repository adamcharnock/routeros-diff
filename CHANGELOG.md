# RouterOS Diff Changelog

## 0.5.2

* Improvement: Escaping is now more robust

## 0.5.1

* Bug: Further improved implementation and testing of order-preserving logic

## 0.5.0

* Bug: Improved implementation and testing of order-preserving logic

## 0.4.0

* Bug: Fixing omitted settings parameter. Also making settings parameters required, to catch this issue sooner

## 0.3.0

* Feature: Verbose /export output can now (optionally) be used for more concise diff output
* Feature: Adding pretty HTML generation of configs. Fixing escaping/new-line issue
* Enhancement: Diffing of single object entities is now more robust
* Bug: Correcting incorrect instantiation of Expression objects
* Bug: Correcting expression_order_important setting default value to be more specific
* Bug: Fixing error when diffing by id using both positional and non-positional args

## 0.2.0

* Feature: Adding settings to allow customising of the parser
* Various packaging and licensing updates

## 0.1.1

* Adding README to package

## 0.1.0

* Initial release
