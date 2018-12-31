# gocam-sif-pyexport
Export GO-CAMs to SIF

## Usage
```
python ttl2sif.py -i <input:directory> [-o <output:directory> -a <output:archive> -l -d]
```

### Parameters
* `l`: try to convert URIs in human readable labels
* `d`: when true, if a given entity (e.g. GO term) has multiple instances, the name will also be duplicated _2, _3, etc, so that it appears as different nodes in the SIF format

## SIF files
* Documentation about the [SIF Format](http://manual.cytoscape.org/en/stable/Supported_Network_File_Formats.html)
* SIF files can be viewed with [cytoscape](https://cytoscape.org)
* They can also be exported with cytoscape as a web application ([example](http://gocams-sif.s3-website-us-west-1.amazonaws.com/#/){:target="blank"})
