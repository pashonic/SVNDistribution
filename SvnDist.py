# SvnDist (Distribution)  Copyright (C) 2012  Aaron Greene
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from optparse import OptionParser
from xml.dom.minidom import parse, parseString
import os
import sys
import re
import subprocess
import shutil

#
# Define arguments.
#

ArgParse = OptionParser('%prog -d Destination_Path -s Source_Path(s) [Options]')
ArgParse.add_option('-d', '--destination', dest='dest', help='Desination path.')
ArgParse.add_option('-s', '--source', action="append", dest='sources', help='Source path(s), multiple sources can be given.')
ArgParse.add_option('-t', '--tags', action="append", dest='tags', help='XML tags of that define which content in source xml to include or exclude.')
ArgParse.add_option('-x', '--cleandest', action ='store_true', dest='cleanDest', help='Enable cleaning of desintiation before operations. ' +
                                                                                      'This will revert changes and remove unversioned content.')
ArgParse.add_option('-c', '--commit', action='store_true', dest='commit', help='Enabled SVN commit of destination after changes are done')
ArgParse.add_option('-r', '--resettags',action='store_true', dest='resettags', help='Resets Property Tags. This will force content.' +
                                                                                    ' from different sources to be removed from destination.')
ArgParse.add_option('-u', '--username', dest='username', help='SVN username used for SVN operations.')
ArgParse.add_option('-p', '--password', dest='password', help='SVN passowrd used for SVN operations.')

#
# Script configuration variables.
#

PropTag = 'DistUrl'

#
# Define helper functions.
#

def RunSysCommand(command):
    proc = subprocess.Popen(command, shell = True, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
    proc.wait()
    stdErr = proc.stderr.read()
    if re.match('\S', stdErr):
        sys.exit('ERROR: System Command Error: {0}'.format(stdErr))
    return proc.stdout.read()

def RunSvnCommand(command):
    loginInfo = ''
    if not (Options.username == None) and not (Options.password == None) :
        loginInfo = ' --username {0} --password {1} '.format(Options.username, Options.password)
    return RunSysCommand('svn {0} {1}'.format(loginInfo, command))

def CleanRepository(repositoryPath):
    print 'Cleaning Destination Repository...'

    #
    # Clean repository.
    #

    RunSvnCommand('cleanup %s' % repositoryPath)

    #
    # Revert changes.
    #

    RunSvnCommand('revert -R %s' % repositoryPath)

    #
    # Remove unversioned items.
    #

    outputMatch = RunSysCommand('svn status %s' % repositoryPath)
    delTargets = re.findall(r'(?<= {5})\S[^\r\n]+', str(outputMatch))
    for delTarget in delTargets:
        if os.path.isdir(delTarget):
            shutil.rmtree(delTarget)
            print ('Deleted: ' + delTarget)
        elif os.path.isfile(delTarget):
            os.remove(delTarget)
            print ('Deleted: ' + delTarget)

    #
    # Update.
    #

    RunSvnCommand('update %s' % (repositoryPath))

def IsSubversioned(svnInfoOutPut):
    return re.search('Path\:', svnInfoOutPut)

def Copy(sourcePath, destPath):
    global copyList

    #
    # Capture folder path.
    #

    folderBase2Make = None
    if re.search('/\Z', destPath): # Destination is folder.
        folderBase2Make = destPath
    else: # Destination is file.
        folderBaseMatch = re.match('(?P<base>.+?)/[^/]+\Z', destPath)
        if folderBaseMatch:
            folderBase2Make = folderBaseMatch.group('base')

    #
    # Create folder path.
    #

    if not (folderBase2Make == None):
        folderBase2Make = re.sub('(/\Z)|(\A\./)', '', folderBase2Make)
        if not folderBase2Make in copyList:
            copyList.append(folderBase2Make)
        RunSysCommand('mkdir -p "{0}"'.format(folderBase2Make))

    #
    # Perform copy operation.
    #

    sourcePath = re.sub(' ', '\ ', sourcePath)
    destPath = re.sub(' ', '\ ', destPath)
    copyOutPut = RunSysCommand('cp -R -v {0} {1}'.format(sourcePath, destPath))
    return copyOutPut

#
# Procces dist.xml file.
#

def HandleXmlNode(node):
    global currentDest
    global copyList
    if (node == None):
        return

    #
    # Handle include/exclude tags.
    #

    if re.match('(include)|(exclude)', node.nodeName):

        #
        # No tag = processes children.
        #

        attuTag = node.getAttributeNode('tag')
        if (attuTag == None) and(node.nodeName == 'include'):
            HandleXmlNode(node.firstChild)

        #
        # Handle tags.
        #

        else:
            nodeTagList = re.findall('\w+', attuTag.nodeValue)
            isMatchingTags = (len(set(Tags) & set(nodeTagList)) > 0)
            if (isMatchingTags and(node.nodeName == 'include')) or \
               (not isMatchingTags and(node.nodeName == 'exclude')):
                    HandleXmlNode(node.firstChild)
    #
    # Handle content tag.
    #

    if (node.nodeName == 'content'):
        destTag = node.getAttributeNode('dest')
        srcTag = node.getAttributeNode('source')
        if (destTag != None):
            currentDest = os.path.join(DestPath, destTag.nodeValue)
        if (srcTag == None):
            HandleXmlNode(node.firstChild)
            HandleXmlNode(node.nextSibling)
            return
        elif (currentDest == None):
            sys.exit('ERROR: XML source has no destination')

        #
        # Perform copy.
        #

        sourcePath = os.path.join(source['Path'], srcTag.nodeValue)
        copyOutput = Copy(sourcePath, currentDest)
        copyList = copyList + re.findall('\-\> \`\.?/?(?P<path>[^\']+)', copyOutput)

    #
    # Handle next sibling
    #

    HandleXmlNode(node.nextSibling)

def GetPropTagsFromSvnPath(svnPath):
    distURLListOutput = RunSvnCommand('propget -R {0} {1}'.format(PropTag, svnPath))
    props = re.finditer('(?P<path>[^\r\n]+) \- (?P<sources>[^\r\n]*)', distURLListOutput)
    returnList = []
    for prop in props:
        pathB = re.sub('\\\\', '/',  prop.group('path'))
        returnList.append({'path':pathB, 'sources':prop.group('sources')})
    return returnList


# *****************************************
# *****************************************
# Script Starts Here.
# *****************************************
# *****************************************

#
# Process arguments.
#

(Options, args) = ArgParse.parse_args()
SourcePaths = Options.sources
if (SourcePaths == None):
    sys.exit('ERROR: No Source Path(s) Given')
DestPath = Options.dest
if (DestPath == None):
    sys.exit('ERROR: No Destination Path Given')
Tags = Options.tags if not (Options.tags == None) else []

#
# Check and gather source(s) information.
#

Sources = []
for sourcePath in SourcePaths:
    source = {'Path':sourcePath, 'DistXmlPath':os.path.join(sourcePath, 'dist.xml')}

    #
    # Check source directory.
    #

    if not os.path.isdir(source['Path']):
        sys.exit('ERROR: Invalid source directory: {0}'.format(sourcePath))

    #
    # Check for dist.xml file.
    #

    if not os.path.isfile(source['DistXmlPath']):
        sys.exit('ERROR: No dist.xml found in source: {0}'.format(sourcePath))

    #
    # Check SVN and capture revision.
    #

    source['SVNInfo'] = RunSvnCommand('info {0}'.format(sourcePath))
    if not IsSubversioned(source['SVNInfo']):
        sys.exit('ERROR: Source is not subversioned or subversion is missing/broken: {0}'.format(sourcePath))
    source['SVNRevision'] = re.search('Revision\:\s+(?P<rev>\d+)', source['SVNInfo']).group('rev')

    #
    # Capture SVN URL.
    #

    source['SVNUrl'] = re.search('URL\:\s+(?P<url>[^\r\n]+)', source['SVNInfo']).group('url')
    Sources.append(source)

#
# Check destination.
#

if not os.path.isdir(DestPath):
    sys.exit('ERROR: Invalid destination directory: {0}'.format(DestPath))
DestSVNInfo = RunSvnCommand('info {0}'.format(DestPath))
if not IsSubversioned(DestSVNInfo):
    sys.exit('ERROR: Destination is not subversioned or subversion is missing/broken')

#
# Clean destination repository, if option was given.
#

if Options.cleanDest:
    CleanRepository(DestPath)

#
# Reset tags, if option was given.
#

if Options.resettags:
    for property in GetPropTagsFromSvnPath(DestPath):
        RunSvnCommand('propset {0} "" "{1}"'.format(PropTag, property['path']))

#
# Process given sources.
#

for source in Sources:

    #
    # Process source xml, copy operations begin here.
    #

    xmlDom = parse(source['DistXmlPath'])
    currentDest = None
    copyList = []
    HandleXmlNode(xmlDom.childNodes[0])

    #
    # Remove items from destination that came from the source but were not added.
    #

    for property in GetPropTagsFromSvnPath(DestPath):
        if (source['SVNUrl'] in property['sources']):
            pathA = property['path']
            if not pathA in copyList:
                newSource = property['sources'].replace(source['SVNUrl'] + ',', '')
                pathA = re.sub(' ', '\ ', pathA)
                RunSvnCommand('propset {0} "{1}" {2}'.format(PropTag, newSource, pathA))

    #
    # SVN add new content that was added (if any).
    #

    RunSvnCommand('add {0}* --force'.format(DestPath))

    #
    # Add property tags to the added items.
    #

    for addItem in copyList:
        addItem = re.sub(' ', '\ ', addItem)
        currentUrlSources = RunSvnCommand('propget {0} {1}'.format(PropTag, addItem))
        currentUrlSources = re.sub('[\r\n]', '', currentUrlSources)
        if not source['SVNUrl'] in currentUrlSources: # Property tag already exists?
            RunSvnCommand('propset {0} "{1}," {2}'.format(PropTag, currentUrlSources + source['SVNUrl'], addItem))

#
# Delete items that have no DistURL.
#

for property in GetPropTagsFromSvnPath(DestPath):
    if not re.search('\w', property['sources']):
        path = re.sub(' ', '\ ', property['path'])
        RunSvnCommand('delete --force {0}'.format(path))

#
# Exit if no commit argument was given.
#

if not Options.commit:
    sys.exit(0)

#
# Create commit message.
#

commitMessage = 'Distribution Sources:'
for source in Sources:
    sourceUrl = re.sub('\A.+?/+', '', source['SVNUrl'])
    commitMessage += '\r\n{0} @ {1}'.format(sourceUrl, source['SVNRevision'])
commitMessage = re.sub('\%20', ' ', commitMessage)

#
# Commit Changes.
#

RunSvnCommand('commit -m "{0}" {1}'.format(commitMessage, DestPath))
