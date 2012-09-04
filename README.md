SVN Distribution
=============

Description
-------
SVN Distribution is a tool used to merge content between SVN sources to a specifc SVN desitation.
The source content can come from different repositories or the same (just different path). The 
desitation can also be a different respository or the same (just different path). Which content is
added to the destination is determined by an xml file residing at the base of the SVN sources.
Content removed from these XML files will be automatically removed from the destination repository.

The most likely scenario for using this tool would be for merging build-product (or artifact) content into
one SVN source or repository after executing a build. Adding or removing content can done by simply
editing the XML file at the base of the sources.
