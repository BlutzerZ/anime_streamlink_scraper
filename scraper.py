from bs4 import BeautifulSoup
import requests, base64, os


# NEED TO DEBUG
def entering_loc(loc):
    page = requests.get(loc.text)
    soup = BeautifulSoup(page.text, 'html.parser')

    try:
        main_info = soup.find('div',{"class":"info_single"}).find_all('li')
    except Exception as e:
        print(e)
        return
    judulAnime = main_info[0].text
    for info in main_info:
     if info.find('strong').text == "Total Episode: ":
            totalEps = info.text
            
    epsList = soup.find_all('li', {"class":"this_episode_list"})
    
    #LOOP GET ALL EPS URL
    epsUrlList = [eps.find('a')['href'] for eps in epsList]

    return judulAnime, totalEps, epsUrlList


def get_info_eps(epsUrl):
    page = requests.get(epsUrl)
    soup = BeautifulSoup(page.content, 'html.parser')
    judulEps = soup.find('h1').text
    
    # GET STREAM MIRROR AS DICT ============================================================
    streamMirrorList = soup.find('div', {"class":"nonton-server"}).find_all('div')
    streamMirrorDict = {}
    for streamMirror in streamMirrorList:
        mirrorName = streamMirror.text
        Streamurl = base64.b64decode(streamMirror['url']).decode("utf-8")
        streamMirrorDict[mirrorName] = Streamurl
    # =======================================================================================

    # GET DOWNLOAD 
    downloadMirrorList = soup.find("div", {"class":"download-content"}).find('p').find_all('a')
    downloadMirrorDict = {}
    for downloadMirror in downloadMirrorList:
        downloadMirrorName = downloadMirror.text
        downloadMirrorUrl = downloadMirror['href']
        downloadMirrorDict[downloadMirrorName] = downloadMirrorUrl





    return judulEps, streamMirrorDict, downloadMirrorDict



if __name__ == "__main__":
    url = "https://nobarnime.com/post-sitemap.xml"
    sitemap = requests.get(url)
    soup = BeautifulSoup(sitemap.content, 'html.parser')
    loc_sitemap = soup.find_all('loc')
    loc_sitemap = loc_sitemap[-6:-1]
    print(len(loc_sitemap))

    i = 0
    for loc in loc_sitemap:
        i+=1
        judulAnime, totalEps, epsUrlList = entering_loc(loc)
        # FILTER ===========================================================
        judulAnime = judulAnime.replace('\n','').replace('Judul:  ','')
        judulAnime = judulAnime.replace("/", "").replace('"', "").replace('<', "").replace('>', "").replace('|', "").replace("?","").replace(":", "")
        totalEps = totalEps.replace('\n','').replace('Total Episode:  ','').replace("?","-")
        # ===================================================================
        if os.path.exists(f'[{i}] {judulAnime} [{totalEps} eps].txt'):
            print(f'[{i}] {judulAnime} [{totalEps} Eps].txt is exist')
            continue
        with open(f'[{i}] {judulAnime} [{totalEps} Eps].txt', 'w', encoding='utf-8') as file_handler:
            print("======================================")
            print(f"Judul: {judulAnime}")
            file_handler.write(f"JUDUL: {judulAnime}\n")
            print(f"Total Eps: {totalEps}")
            file_handler.write(f"TOTAL: {totalEps}\n\n")
            for epsUrl in epsUrlList:
                try:
                    judulEps, streamMirrorDict, downloadMirrorDict = get_info_eps(epsUrl)
                except Exception as e:
                    print(e)
                # FILTER ===================================================================================
                judulEps = judulEps.replace("Nonton Anime ", "").replace("Sub Indo", "").replace("\n", "")
                # ==========================================================================================
                print(f"=> {judulEps}")
                file_handler.write(f"> {judulEps}\n")
                
                print(f"===[ STREAM MIRROR ]===")
                file_handler.write("===[ STREAM MIRROR ]===\n")
                for streamMirrorName, streamMirrorUrl in streamMirrorDict.items():
                    print(f"- {streamMirrorName}: {streamMirrorUrl}")
                    file_handler.write(f"- {streamMirrorName}: {streamMirrorUrl}\n")

                print(f"===[ DOWNLOAD MIRROR ]===")
                file_handler.write("===[ DOWNLOAD MIRROR ]===\n")
                for downloadMirrorName, downloadMirrorUrl in downloadMirrorDict.items():
                    print(f"- {downloadMirrorName}: {downloadMirrorUrl}")
                    file_handler.write(f"- {downloadMirrorName}: {downloadMirrorUrl}\n")
                file_handler.write("\n")

            print("======================================")
