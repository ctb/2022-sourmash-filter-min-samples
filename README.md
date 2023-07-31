# 2022-sourmash-filter-min-samples

**NOTE** This code has now been moved into a sourmash plugin, [sourmash_plugin_commonhash](https://github.com/ctb/sourmash_plugin_commonhash).

Please see [sourmash#2383](https://github.com/sourmash-bio/sourmash/issues/2383) for lots of discussion ;).

Usage:
```
./filter-min-samples.py *.sig -o filtered.zip
```

Note: if you output to a zip file, you can use `sourmash sig split` to
break them into individual files again. Alternatively, use a directory
(ending with `/`) to save them as individual signature files directly.
