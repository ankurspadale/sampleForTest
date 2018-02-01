#!/usr/bin/python
#
#
# Uses the robot class in "robot.py" to crawl through the network
# paths stored in the database, searching for new graphic files.
#
asd

from time import mktime, gmtime
import re,Image,copy
from string import split
from urlparse import urlparse
from mylib import opener,robot,connect,imagetypes

filetypes = copy.copy(imagetypes)
filetypes['text/html'] = 'HTML'
filetypes['text/plain'] = 'TEXT'

class iterator:
    netre = re.compile('(?:(\w*):(\w*)@)?((?:\w|[\.\-\&])+)(?::(\d+))?')

    def __init__(self,timeout,db):
        self.types = filetypes
        self.timeout = timeout
        self.db = db
        
    def findpath(self,url,makepath=0):
        protocol,netloc,dirpath,dummy,dummy,dummy = urlparse(url,'http',0)
        if protocol and netloc and dirpath:
            c = self.db.cursor()
            m = self.netre.match(netloc)
            username = m.group(1) or ''
            password = m.group(2) or ''
            hostname = m.group(3) or 'localhost'
            c.execute('select path from shares where protocol="%s" and username="%s" and password="%s" and hostname="%s" limit 1'
                      % (protocol,username,password,hostname))
            pathid = 0
            if c.rowcount>0:
                pathid = c.fetchone()[0]
                subdirs = split(dirpath,'/')
                name=subdirs[-1]
                subdirs=subdirs[:-1]
                recurse = 0
                for subdir in subdirs:
                    c.execute('select path,recurse from paths where parent=%s and dir="%s" limit 1' % (pathid,subdir))
                    if c.rowcount>0:
                        pathid,recurse = c.fetchone()
                    elif recurse or makepath:
                        c.execute('insert into paths (parent,dir,recurse) values (%s,"%s",%s)' % (pathid,subdir,str(recurse)))
                        c.execute('select path from paths where parent=%s and dir="%s" limit 1' % (pathid,subdir))
                        pathid=c.fetchone()[0]
                    else:
                      return(0,0,'')
                if name:
                    c.execute('select path,recurse from paths where parent=%s and dir="%s" limit 1' % (pathid,name))
                    if c.rowcount>0:
                        pathid,recurse=c.fetchone()
                        name=''
                return(pathid,recurse,name)
        return(0,0,'')

    def recurse(self,url):
        return(self.findpath(url)[1])
    
    def fail(self,url):
#        print 'failed to load',url
        path,recurse,name=self.findpath(url)
        if int(path) and name:
            c = self.db.cursor()
            c.execute('update pictures set failures=failures+1 where path=%s and name="%s" limit 1' % (path,name))

    def load(self,url,doc,info,digest):
#        print 'loading',url
        if imagetypes.has_key(info.gettype()):
            self.image(url,doc,info,digest)

    def image(self,url,doc,info,digest):
        path,recurse,name=self.findpath(url,1)
        if not (path and name):
            return
        c = self.db.cursor()
        c.execute('select picture from pictures where path=%s and name="%s" limit 1' % (path,name))
        if c.rowcount>0:
            pic = c.fetchone()[0]
        else:
            pic = None
        filetype=imagetypes[info.gettype()]
        modified=mktime(info.getdate('Last-Modified') or gmtime(0))
        size = info.getheader('Content-Length') or '0'
        # if it has a database entry and we got a date and size
        if pic and modified and size:
            # if the info matches what's in the database
            c.execute('update pictures set failures=0 where picture=%s and modified="%s" and size=%s limit 1' \
                      % (pic,modified,size))
            if c.rowcount>0:
                # don't mess with it.
                return
        # check for an existing entry with the same digest
        c.execute('select picture from pictures where digest="%s" limit 1' % digest)
        # if it already exists
        if c.rowcount>0:
            pic = c.fetchone()[0]
            # just update the path and filename
            c.execute('update pictures set path=%s, name="%s", failures=0 where picture=%s' % (path,name,pic))
        else:
            # load it into the imaging library
            try:
                img = Image.open(doc,"r")
                img.load()
            except IOError:
                print 'IO Error opeining image file'
                self.fail(url)
                return
            except RuntimeError:
                print 'Runtime Error opening image file'
                self.fail(url)
                return
            except ValueError:
                print 'Value Error opening image file'
                self.fail(url)
                return
            # Get its attributes
            width,height = img.size
            # Make a .png thumbnail
            minsize = min(width,height)
            xdiff = (width-minsize)/2
            ydiff = (height-minsize)/2
            img.crop((xdiff,ydiff,minsize+xdiff,minsize+ydiff)).resize((100,100)).save('thumbnails/'+digest+'.png')
            # check to see if the path and name exists already
            if pic:
                c.execute('update pictures set '+\
                          'filetype="%s",width=%s,height=%s,' % (filetype,width,height) +\
                          'modified="%s",size=%s,digest="%s",' % (modified,size,digest) + \
                          'failures=0 where picture=%s' % pic)
                          
            else:
                # print 'Adding image',url
                # add it to the database
                c.execute('insert into pictures ' + \
                          '(path,name,filetype,width,height,modified,size,digest) '+ \
                          'values (%s,"%s","%s",%s,%s,"%s",%s,"%s")' \
                          % (path,name,filetype,width,height,modified,size,digest))

    def searchpaths(self,url,path,opener,robot):
        c = self.db.cursor()
        c.execute('select path,recurse,dir from paths where parent=%s' % path)
        count = c.rowcount
        while count>0:
            count = count-1
            newpath,recurse,dir = c.fetchone()
            newurl = url+dir
            if dir:
                newurl = newurl+'/'
            if recurse:
                robot.run(newurl,opener)
            if newpath!=path:
                self.searchpaths(newurl,newpath,opener,robot)

    def iterate(self,robot):
        c = self.db.cursor()
        c.execute('select protocol,username,password,hostname,shares.path from shares,paths where shares.path=paths.path')
        count = c.rowcount
        while count>0:
            count = count-1
            protocol,username,password,hostname,basepath = c.fetchone()
            newopener = opener(username,password)
            self.searchpaths(protocol+'://'+hostname+'/',basepath,newopener,robot)
            newopener.cleanup()


if __name__ == '__main__':
  fetcher = iterator(30,connect())
  robot = robot(fetcher)
  fetcher.iterate(robot)
