SVN Distribution
=============

Description
-------
SVN Distribution is a tool used to merge content between SVN sources to a specifc SVN desitation.
The source content can come from different repositories or the same (just different path). The 
desitation can also be a different respository or the same (just different path). Which content is
added to the destination is determined by an XML file residing at the base of the SVN sources.
Content removed from these XML files will be automatically removed from the destination repository.

The most likely scenario for using this tool would be for merging build-product (or artifact) content into
one SVN source or repository after executing a automated build form different source code projects. 
Adding or removing content can done by simply editing the XML file at the base of the sources; 
this allows clear visability of what is being added and non-engineers to edit content.

Restrictions
-------
Unix (Ubuntu, Fedora, etc.) or Cygwin. (Ask if you want to support Windows)
Python 2.6 to 2.7
SVN Subversion 1.6+

Usage
-------
SvnDist.py -d Destination_Path -s Source_Path(s) [Options]

Options:
 -h, --help            show this help message and exit
  -d DEST, --destination=DEST
                        Desination path.
  -s SOURCES, --source=SOURCES
                        Source path(s), multiple sources can be given.
  -t TAGS, --tags=TAGS  XML tags of that define which content in source xml to
                        include or exclude.
  -x, --cleandest       Enable cleaning of desintiation before operations.
                        This will revert changes and remove unversioned
                        content.
  -c, --commit          Enabled SVN commit of destination after changes are
                        done
  -r, --resettags       Resets Property Tags. This will force content. from
                        different sources to be removed from destination.
  -u USERNAME, --username=USERNAME
                        SVN username used for SVN operations.
  -p PASSWORD, --password=PASSWORD
                        SVN passowrd used for SVN operations.


