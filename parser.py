### mediawiki parser 
## short version

import pprint, sys, time
sys.path.append( './lib' )

pp = pprint.PrettyPrinter( indent = 4 )
def debug( e ):
    pp.pprint( e );

## dokuwiki xmlrpc https://github.com/chimeric/dokuwikixmlrpc
sys.path.append( './lib/dokuwikixmlrpc' )
import dokuwikixmlrpc
dw = dokuwikixmlrpc.DokuWikiClient( 'http://akira', 'rpc', 'rpc' )
#dw = dokuwikixmlrpc.DokuWikiClient( 'http://orga.cccv.de', 'rpc', 'rpc' )
def save_page( link, text, comment, minor ):
    save = False
    tries = 0
    while save == False:
        time.sleep( 1 ) # better not have edits in same second 
        try:
            dw.put_page( link, text, comment, minor )
            save = True
        except:
            print "save: try failed %s" % tries
            tries += 1
            if tries > 1: return False

## https://github.com/erikrose/mediawiki-parser   
sys.path.append( './lib/mediawiki-parser' )
import mw2dw
mw2dw = mw2dw.mw2dw( )

def save( act, page, rev, info ):
    #print '-- %s: %s' % ( act, page['title'] )
    #page['title'] = page['title'].replace( '/', ':' )

    pre = post = filter = ""
    filter = 'Raumpl'
    prefix = '29c3:'

    pagename = page['title']
    #{{{
    if filter and filter not in pagename: return False
    elif 'File:' in pagename: return False
    elif 'Category:' in pagename: return False
    elif 'Kategorie:' in pagename: return False
    elif 'Property:' in pagename: return False
    elif 'Template:' in pagename: return False

    elif 'User talk:' in pagename: 
        user = pagename.split( ':', 1 )[1]
        pagename = 'User:%s/Talk' % user
        pre += '= %s' % pagename

    elif 'User' in pagename: 
        path = pagename.replace( '/', ':' ).split( ':' )
        if len( path ) < 3: 
            pagename = 'user:%s' % path[1]
            pre += u"""= User:%s
---- dataentry User ----
Eintrag         : %s
Kontakt         : 
DECT            :
----\n""" % ( path[1], path[1] )

        else:
            pagename = 'user:%s/%s' % ( path[1], path[2] )
            pre += '= User:%s/%s' % ( path[1], path[2] )

    elif 'Talk:' in pagename: 
        path = pagename.replace( '/', ':' ).split( ':', 1 )
        pre += '= %s' % pagename
        pagename = 'talk:' + prefix + path[1]

    else:
        pre += '= %s' % pagename
        pagename = prefix + pagename
    #}}}

    link = pagename.replace( '/', ':' )
    if act == 'rev':
        comment = '%s %s - %s' % ( rev['user'], rev['timestamp'], rev.get( 'comment', '' ))
        #print '-- %s -> %s, %s' % ( page['title'].encode( 'utf8' ), link.encode( 'utf8' ), comment.encode( 'utf8' ) )
        #save_page( link, rev['text'], comment, rev.get( 'minor', 0 ))
    elif act == 'page':
        print '++ %s :: %s' % ( pagename, pre )
        comment = 'rpc mediawiki parser'
        if rev['text'] == None: text = ""
        else: text = mw2dw.parse( rev['text'] )
        save_page( link, pre+text+post, comment, rev.get( 'minor', 0 ))

    return True

from lxml import etree
def read_dump( infile ):
    info = {}
    page = {}
    rev = {}
    revcount = 0
    f = open( infile ,'r' )

    for ev, el in etree.iterparse( infile ):
	tag = el.tag
	if   tag == 'sitename':	info['site'] = el.text
	elif tag == 'base':	info['base'] = el.text
	elif tag == 'title':	page['title'] = el.text
	elif tag == 'minor':	    rev['minor'] = 1
        elif tag == 'timestamp':    rev['timestamp'] = el.text; #print "timestamp:"+el.text
	elif tag == 'comment':	    rev['comment'] = el.text
	elif tag == 'text':	    rev['text'] = el.text
	elif tag == 'username':     rev['user'] = el.text
	elif tag == 'revision':
	    save( 'rev', page, rev, info );
            lrev = rev
            rev = {}
            revcount += 1
	elif tag  ==  "page":
	    save( 'page', page, lrev, info );
	    lrev = {}
            page = {}
	el.clear( )

read_dump( "mediawiki-dump2.xml" )

