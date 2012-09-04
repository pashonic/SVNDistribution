SVN Distribution
=============

Description
-------
SVN Distribution is a tool used to merge content between SVN sources to a specifc SVN destination. The source content can come from different repositories or the same (just different path). The destination can also be a different repository or the same. Which content is added to the destination is determined by an XML file residing at the base of the SVN sources.Content removed from these XML files will be automatically removed from the destination repository.

The most likely scenario for using this tool would be for merging build-product (or artifact) content into one SVN path or repository after executing a automated build form different source code projects. Adding or removing content can done by simply editing the XML file at the base of the sources; this allows for clear visibility of what is contributed and non-engineers to edit the content.

Restrictions
-------
 *  Unix (Ubuntu, Fedora, etc.) or Cygwin. (Ask if you want to support Windows)
 *  Python 2.6 to 2.7
 *  SVN Subversion 1.6+

Usage
-------
SvnDist.py -d Destination_Path -s Source_Path(s) [Options]

Options:
<table>
    <tr>
        <td><b>Short CMD<b></td>
        <td WIDTH="100"><b>Long CMD<b></td>
        <td><b>Description<b></td>
    </tr>
    <tr>
        <td>-h</td>
        <td>--help</td>
        <td>show this help message and exit.</td>
    </tr>
    <tr>
        <td>-d</td>
        <td>--destination</td>
        <td>Desination path. Local folder path.</td>
    </tr>
    <tr>
        <td>-s</td>
        <td>--source</td>
        <td>Source path(s), multiple sources can be given. Local folder path.</td>
    </tr>
    <tr>
        <td>-t</td>
        <td>--tags</td>
        <td>XML tags of that define which content in source xml to include or exclude.</td>
    </tr>
    <tr>
        <td>-x</td>
        <td>--cleandest</td>
        <td>Enable cleaning of desintiation before operations. This will revert changes and remove unversioned content.</td>
    </tr>
    <tr>
        <td>-c</td>
        <td>--commit</td>
        <td>Enabled SVN commit of destination after changes are done.</td>
    </tr>
    <tr>
        <td>-r</td>
        <td>--resettags</td>
        <td>Resets property tags. This will force content from different sources to be removed from destination.</td>
    </tr>
    <tr>
        <td>-u</td>
        <td>--username</td>
        <td>SVN username used for SVN operations.</td>
    </tr>
    <tr>
        <td>-p</td>
        <td>--password</td>
        <td>SVN passowrd used for SVN operations.</td>
    </tr>
</table>

Example Calls
-------
    python dist/SvnDist.py -s source/ -d dist/ -c -x -r 
    python dist/SvnDist.py -s source1/ -s source2 -d dist/ -c -x
    
Source XML Format
-------
Element Types:

<table>
    <tr>
        <td><b>Element<b></td>
        <td WIDTH="100"><b>Attributes<b></td>
        <td><b>Description<b></td>
    </tr>
    <tr>
        <td>include</td>
        <td>tags='[name]'</td>
        <td>Includes items with a specific tag name. If valid, children will be processed.
            Multiple tags can be given; example: tag='linux,windows'.
            If a tag Attribute is not given children are processed by default</td>
    </tr>
    <tr>
        <td>exclude</td>
        <td>tags='[name]'</td>
        <td>Excludes items with a specific tag name. Same similar rules as include.</td>
    </tr>
    <tr>
        <td>content</td>
        <td>dest='[destination path]';source='[source path]';</td>
        <td>Represents content. For transfering one source to a destination a source and dest attribute can be used within one content element. 
            For transfering multiple sources to one destination a content element with only a dest attribute can be used; it is then expected 
            this element will contain other context elements that only have a source attribute.</td>
    </tr>
</table>

Example:
```
<?xml version="1.0"?>
<include>
    <include tag="linux">
        <content dest="linux/destinationFolder1/">
            <content source="sourceFolder1/sourcefolder2/file1.jar"/>
            <content source="sourceFolder2/sourcefolder2/file2.jar"/>
            <content source="sourceFolder3/sourcefolder2/file3.jar"/>
            <content source="sourceFolder4/sourcefolder2/*"/>
        </content>
    </include>
    <exclude tag="linux">
        <content dest="notlinux/newtfilename.txt" source="sourcefolder/textfile.txt"/>
    </exclude>
</include>
```