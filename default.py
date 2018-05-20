# -*- coding: utf-8 -*-
#Библиотеки, които използват python и Kodi в тази приставка
import re
import sys
import os
import urllib
import urllib2
import xbmc, xbmcplugin,xbmcgui,xbmcaddon
import urlparse
import json
import time
import xbmcvfs
import base64
import requests
#Място за дефиниране на константи, които ще се използват няколкократно из отделните модули
__addon_id__= 'plugin.video.gledaiseriali'
__Addon = xbmcaddon.Addon(__addon_id__)
api_key = xbmcaddon.Addon().getSetting('ocrspace')
__settings__ = xbmcaddon.Addon(id='plugin.video.gledaiseriali')
__icon__ =  xbmc.translatePath(__Addon.getAddonInfo('path') + "/resources/icon.png")
searchicon = xbmc.translatePath(__Addon.getAddonInfo('path') + "/resources/search.png")
folder = xbmc.translatePath(__Addon.getAddonInfo('path') + "/resources/folder.png")
series = xbmc.translatePath(__Addon.getAddonInfo('path') + "/resources/series.png")
subsoload = xbmcaddon.Addon().getSetting('subsoload')
srtsubs_path = xbmc.translatePath('special://temp/gseriali/subs.srt')
baseurl = base64.b64decode('aHR0cHM6Ly9nbGVkYWlzZXJpYWxpLm5ldC8=')
MUA = 'Mozilla/5.0 (Linux; Android 5.0.2; bg-bg; SAMSUNG GT-I9195 Build/JDQ39) AppleWebKit/535.19 (KHTML, like Gecko) Version/1.0 Chrome/18.0.1025.308 Mobile Safari/535.19' #За симулиране на заявка от мобилно устройство
UA = 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:40.0) Gecko/20100101 Firefox/58.0' #За симулиране на заявка от  компютърен браузър
if not api_key or not __settings__:
        xbmcaddon.Addon().openSettings()

#Меню с директории в приставката
def CATEGORIES():
        addDir('Търсене на видео',baseurl+'?s=',2,searchicon)
        addDir('Научно-Популярни',baseurl+'category/%d0%bd%d0%b0%d1%83%d1%87%d0%bd%d0%be-%d0%bf%d0%be%d0%bf%d1%83%d0%bb%d1%8f%d1%80%d0%bd%d0%b8/',1,folder)
        addDir('Спорт',baseurl+'category/%D1%81%D0%BF%D0%BE%D1%80%D1%82/',1,folder)
        req = urllib2.Request(baseurl)
        req.add_header('User-Agent', UA)
        response = urllib2.urlopen(req)
        #print 'request page url:' + url
        data=response.read()
        response.close()
        match = re.compile('<li class="cat-item cat-item-\d+"><a href="(http.+?category.+?)" >(.+?)</a>\n<ul class=.children').findall(data)
        for link,title in match:
         title = title.replace('&#8217;','')
         title = title.replace('&#8211;','')
         addDir(title,link,1,folder)       

#Разлистване видеата на първата подадена страница
def INDEXPAGES(url):
        req = urllib2.Request(url)
        req.add_header('User-Agent', UA)
        response = urllib2.urlopen(req)
        #print 'request page url:' + url
        data=response.read()
        response.close()

        #Начало на обхождането
        br = 0 #Брояч на видеата в страницата - 40 за този сайт
        match = re.compile('a href="(.+?)" title="(.+?)".*\n.*src="(.+?)\?').findall(data)
        for link,title,thumbnail in match:
            title = title.replace('&#8217;','')
            title = title.replace('&#8211;','')
            addLink(title,link,5,'',thumbnail)
            br = br + 1
            #print 'Items counter: ' + str(br)
        if br >= 40: #тогава имаме следваща страница и конструираме нейния адрес
            getpage=re.compile('<a href="(http.+?)/page/(\d+)/" class="next">').findall(data)
            for pageurl,page in getpage:
                newpage = int(page)
                nextpage = int(0) + newpage
                url = pageurl + '/page/' + str(nextpage) + '/'
                print 'URL OF THE NEXT PAGE IS' + url
                thumbnail='DefaultFolder.png'
                addDir('следваща страница>>',url,3,thumbnail)
                
def INDEXNEXTPAGE(url):
        req = urllib2.Request(url)
        req.add_header('User-Agent', UA)
        response = urllib2.urlopen(req)
        #print 'request page url:' + url
        data=response.read()
        response.close()

        #Начало на обхождането
        br = 0 #Брояч на видеата в страницата - 40 за този сайт
        match = re.compile('a href="(.+?)" title="(.+?)".*\n.*src="(.+?)\?').findall(data)
        for link,title,thumbnail in match:
            title = title.replace('&#8217;','')
            title = title.replace('&#8211;','')
            addLink(title,link,5,'',thumbnail)
            br = br + 1
            #print 'Items counter: ' + str(br)
        if br >= 40: #тогава имаме следваща страница и конструираме нейния адрес
            getpage=re.compile('</a> <a href="(https.+?)/page/(\d+)/" class="next">').findall(data)
            for pageurl,page in getpage:
                newpage = int(page)
                nextpage = int(0) + newpage
                url = pageurl + '/page/' + str(nextpage) + '/'
                print 'URL OF THE NEXT PAGE IS' + url
                thumbnail='DefaultFolder.png'
                addDir('следваща страница>>',url,3,thumbnail)
#Търсачка
def SEARCH(url):
        keyb = xbmc.Keyboard('', 'Търсачка')
        keyb.doModal()
        searchText = ''
        if (keyb.isConfirmed()):
            searchText = urllib.quote_plus(keyb.getText())
            searchText=searchText.replace(' ','+')
            searchurl = url + searchText
            searchurl = searchurl.encode('utf-8')
            #print 'SEARCHING:' + searchurl
            INDEXPAGES(searchurl)

        else:
             addDir('Върнете се назад в главното меню за да продължите','','',"DefaultFolderBack.png")
def remove_dir (path):
       dirList, flsList = xbmcvfs.listdir(path)
       for fl in flsList: 
            xbmcvfs.delete(os.path.join(path, fl))
       for dr in dirList: 
            remove_dir(os.path.join(path, dr))
       xbmcvfs.rmdir(path)
       
def SHOW(url):
       remove_dir(xbmc.translatePath('special://temp/gseriali')) 
       req = urllib2.Request(url)
       req.add_header('User-Agent', UA)
       response = urllib2.urlopen(req)
       data=response.read()
       response.close()
       match1 = re.compile('id="content-protector-captcha.+?".*\n.*value="(.+?)"').findall(data)
       match2 = re.compile('id="content-protector-token.*\n.*value="(.+?)"').findall(data)
       match3 = re.compile('id="content-protector-ident.*".*\n.*value="(.+?)"').findall(data)
       match4 = re.compile('id="content-protector-submit.*".*\n.*\n.*value="(.+?)"').findall(data)
       basepicture = re.compile('src="(data.+?)"').findall(data)
       for captcha in match1:
        for token in match2:
         for ident in match3:
          for submit in match4:
           for codedpic in basepicture:
             endpoint = "https://api.ocr.space/parse/image"
             payload = {"apikey":api_key,"base64Image":codedpic, "language":"eng", "isOverlayRequired":"false" }
             res = requests.post(endpoint,data=payload)
             match = re.findall('ParsedText":"(\d+)', res.text)
             for numbers in match:
              data = {"content-protector-captcha": captcha,
              "content-protector-password": numbers,
               "content-protector-token": token,
               "content-protector-ident": ident,
               "content-protector-submit": submit}
              req = urllib2.Request(url, urllib.urlencode(data))
              req.add_header('User-Agent', UA)
              response = urllib2.urlopen(req)
              data = response.read()
              response.close()
              xbmc.executebuiltin(('Notification(%s,%s,%s,%s)' % ('Success', 'Кодът е успешно въведен', '1000', __icon__)))
              match = re.compile('<iframe src="(.+?)" scrolling="no"').findall(data)
              for link in match:      
                 if 'openload' in link:
                   addLink2(name,link,8,'','DefaultVideo.png')
                 if not 'openload' in link:
                   addLink2(name,link,7,'','DefaultVideo.png')


#Зареждане на видео
def PLAY(url):
        import urlresolver
        li = xbmcgui.ListItem(iconImage=iconimage, thumbnailImage=iconimage, path=url)
        li.setInfo('video', { 'title': name })
        link = url
        try: stream_url = urlresolver.HostedMediaFile(link).resolve()
        except:
               deb('Link URL Was Not Resolved',link); deadNote("urlresolver.HostedMediaFile(link).resolve()","Failed to Resolve Playable URL."); return

        ##xbmc.Player().stop()
        play=xbmc.Player() ### xbmc.PLAYER_CORE_AUTO | xbmc.PLAYER_CORE_DVDPLAYER | xbmc.PLAYER_CORE_MPLAYER | xbmc.PLAYER_CORE_PAPLAYER
        try: _addon.resolve_url(url)
        except: t=''
        try: _addon.resolve_url(stream_url)
        except: t=''
        play.play(stream_url, li); xbmcplugin.setResolvedUrl(handle=int(sys.argv[1]), succeeded=True, listitem=li)
        try: _addon.resolve_url(url)
        except: t=''
        try: _addon.resolve_url(stream_url)
        except: t=''


       
def PLAYOL(url):
        if xbmcaddon.Addon().getSetting('subsoload') == 'true': 
         remove_dir(xbmc.translatePath('special://temp/gseriali'))
         xbmcvfs.mkdir(xbmc.translatePath('special://temp/gseriali'))
         from bs4 import BeautifulSoup              
         subsoload = True
         req = urllib2.Request(url)
         req.add_header('User-Agent', UA)
         response = urllib2.urlopen(req)
         data=response.read()
         response.close()
         soup = BeautifulSoup(data, "html.parser")
         for caption in soup.find_all(id="olvideo"):
            for link in caption.find_all("track",{"src":True}):
              print link['src']
              try:
               suburl = link['src']
               print suburl
               req = urllib2.Request(suburl)
               req.add_header('User-Agent', UA)
               response = urllib2.urlopen(req)
               datasubs = response.read()
               response.close()
               file = open(xbmc.translatePath('special://temp/gseriali/subs.srt'), 'wb')
               file.write(datasubs)
               file.close()
              except:
               sub = 'false'
        else:
          subsoload = False
          sub = 'false'
        match = re.compile('https.+?embed/(.+?)/').findall(url)
        for  link in match:
         link = 'https://api.openload.co/1/streaming/get?file=' + link
         req = urllib2.Request(link)
         req.add_header('User-Agent', UA)
         response = urllib2.urlopen(req)
         data=response.read()
         response.close()
         jsonrsp = json.loads(data)
         status = jsonrsp['status']
         msg = jsonrsp['msg']
         if status == 404:
          xbmc.executebuiltin((u'Notification(%s,%s,%s,%s)' % (status, msg, '5000', __icon__)).encode('utf-8'))
         if status == 403:
          xbmc.executebuiltin((u'Notification(%s,%s,%s,%s)' % (status, msg, '5000', __icon__)).encode('utf-8'))
         if status == 200:
          path = jsonrsp['result']['url'].replace('?mime=true','')
          li = xbmcgui.ListItem(iconImage=iconimage, thumbnailImage=iconimage, path=path)
          li.setInfo('video', { 'title': name })
          #if sub=='true':
           #li.setSubtitles([srtsubs_path])
          #else:
           #sub=='false'     
          xbmcplugin.setResolvedUrl(handle=int(sys.argv[1]), succeeded=True, listitem=li)
          try:
            if os.path.exists(xbmc.translatePath('special://temp/gseriali/subs.srt')):   
                  print "Намерени субтитри!"         
                  sub = 'true'
                  xbmc.executebuiltin(('Notification(%s,%s,%s,%s)' % ('Success', 'Успешно заредени субтитри', '500', __icon__)))
            else:
                  print "Не са открити субтитри!"
                  sub = 'false'      
            xbmc.Player().play(path, li)
           #Задаване на субтитри, ако има такива или изключването им
            if sub=='true':
                while not xbmc.Player().isPlaying():
                    xbmc.sleep(1000) #wait until video is being played
                    xbmc.Player().setSubtitles(srtsubs_path)
            else:
                xbmc.Player().showSubtitles(False)
   
          except:
           xbmc.executebuiltin("Notification('Грешка','Видеото липсва на сървъра!')")

#Модул за добавяне на отделно заглавие и неговите атрибути към съдържанието на показваната в Kodi директория - НЯМА НУЖДА ДА ПРОМЕНЯТЕ НИЩО ТУК
def addLink(name,url,mode,plot,iconimage):
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
        ok=True
        liz=xbmcgui.ListItem(name, iconImage=iconimage, thumbnailImage=iconimage)
        liz.setArt({ 'thumb': iconimage,'poster': iconimage, 'banner' : iconimage, 'fanart': iconimage })
        liz.setInfo( type="Video", infoLabels={ "Title": name, "plot": plot } )
        liz.setProperty("IsPlayable" , "true")
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
        return ok

def addLink2(name,url,mode,plot,iconimage):
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
        ok=True
        liz=xbmcgui.ListItem(name, iconImage=iconimage, thumbnailImage=iconimage)
        liz.setArt({ 'thumb': iconimage,'poster': iconimage, 'banner' : iconimage, 'fanart': iconimage })
        liz.setInfo( type="Video", infoLabels={ "Title": name, "plot": plot } )
        liz.setProperty("IsPlayable" , "false")
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=False)
        return ok

#Модул за добавяне на отделна директория и нейните атрибути към съдържанието на показваната в Kodi директория - НЯМА НУЖДА ДА ПРОМЕНЯТЕ НИЩО ТУК
def addDir(name,url,mode,iconimage):
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
        ok=True
        liz=xbmcgui.ListItem(name, iconImage=iconimage, thumbnailImage=iconimage)
        liz.setArt({ 'thumb': iconimage,'poster': iconimage, 'banner' : iconimage, 'fanart': iconimage })
        liz.setInfo( type="Video", infoLabels={ "Title": name } )
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
        return ok

#НЯМА НУЖДА ДА ПРОМЕНЯТЕ НИЩО ТУК
def get_params():
        param=[]
        paramstring=sys.argv[2]
        if len(paramstring)>=2:
                params=sys.argv[2]
                cleanedparams=params.replace('?','')
                if (params[len(params)-1]=='/'):
                        params=params[0:len(params)-2]
                pairsofparams=cleanedparams.split('&')
                param={}
                for i in range(len(pairsofparams)):
                        splitparams={}
                        splitparams=pairsofparams[i].split('=')
                        if (len(splitparams))==2:
                                param[splitparams[0]]=splitparams[1]
                                
        return param







params=get_params()
url=None
name=None
iconimage=None
mode=None

try:
        url=urllib.unquote_plus(params["url"])
except:
        pass
try:
        name=urllib.unquote_plus(params["name"])
except:
        pass
try:
        name=urllib.unquote_plus(params["iconimage"])
except:
        pass
try:
        mode=int(params["mode"])
except:
        pass


#Списък на отделните подпрограми/модули в тази приставка - трябва напълно да отговаря на кода отгоре
if mode==None or url==None or len(url)<1:
        print ""
        CATEGORIES()
    
elif mode==1:
        print ""+url
        INDEXPAGES(url)

elif mode==2:
        print ""+url
        SEARCH(url)

elif mode==3:
        print ""+url
        INDEXNEXTPAGE(url)

elif mode==5:
        print ""+url
        SHOW(url)
        
elif mode==7:
        print ""+url
        PLAY(url)

elif mode==8:
        print ""+url
        PLAYOL(url)

xbmcplugin.endOfDirectory(int(sys.argv[1]))
