__author__ = 'holms@outlook.com'
# 2021/12/26-
import requests
requests.packages.urllib3.disable_warnings()
headers = {
    'Accept': 'application/json',
    'Content-Type': 'text/plain'
}
#ievaddati
CSV_read_file = 'Saraksts ar URL un Telpisko iezīmju tipiem._Ievaddati lejupielādei.csv'
#output
csv_write = CSV_read_file.split('_')[0]+'_statistika.csv'
maxF = 3000 #maxfeature skaits
download = True    #download or not
max_koord = 1000000.0
CRS = 'EPSG:3059'
# ------------------------------------------------------------------------------------
def GETnumberOfFeaturesFromVaic(vaic):
    try:
        page = requests.get(vaic,  verify=False, headers=headers, timeout=120)
    except: return 0
    else:
        chunk = page.text
        if 'arcgis server error' in chunk.lower(): return 0
        else:
            s1 = chunk.find('numberOfFeatures=')+len('numberOfFeatures=')+1
            if chunk.find('"', s1) != -1:
                s2 = chunk.find('"', s1)
            else: s2 = chunk.find("'", s1)
            numberOfFeatures = int(chunk[s1:s2])
            return numberOfFeatures
# ------------------------------------------------------------------------------------
def geom_check(url, FeatureType):
    vaic = url + "request=DescribeFeaturetype&version=1.1.0&service=WFS&TYPENAME="
    vaic += FeatureType
    try:
        page = requests.get(vaic, allow_redirects=True, verify=False, headers=headers, timeout=60)
    except: return False
    else:
        chunk = page.text
        if 'name="shape"' in chunk.lower():
            return 'SHAPE'
        elif 'name="geom"' in chunk.lower():
            return 'geom'
        else: return ''
# ------------------------------------------------------------------------------------
def GETnumberOfFeatures(url, FeatureType):
    vaic = url + 'request=GetFeature&ResultType=hits&version=1.1.0&service=WFS'
    vaic = vaic + '&TYPENAME=' + FeatureType
    try:
        page = requests.get(vaic, allow_redirects=True, verify=False, headers=headers, timeout=60)
    except: return 0
    else:
        chunk = page.text
        s1 = chunk.find('numberOfFeatures=')+len('numberOfFeatures=')+1
        if chunk.find('"', s1) != -1:
            s2 = chunk.find('"', s1)
        else: s2 = chunk.find("'", s1)
        numberOfFeatures = int(chunk[s1:s2])
        return numberOfFeatures
# ------------------------------------------------------------------------------------
def gmlGetRBBOX(url, FeatureType, LLN, LLE, URN, URE):
    global req_queue
    vaic = url + "request=GetFeature&version=1.1.0&service=WFS"
    vaic += '&TYPENAME='
    vaic += FeatureType
    vaic += """&Filter=<ogc:Filter xmlns:ogc="http://www.opengis.net/ogc"><ogc:BBOX>"""
    vaic += """<ogc:PropertyName>"""
    vaic += req_queue[url, FeatureType][1]
    vaic +="""</ogc:PropertyName>"""
    vaic += '<gml:Envelope xmlns:gml="http://www.opengis.net/gml" srsName="'
    vaic += CRS
    vaic += '"><gml:lowerCorner>'
    vaic += str(round(LLN,3))+' '+str(round(LLE,3))
    vaic += """</gml:lowerCorner><gml:upperCorner>"""
    vaic += str(round(URN,3))+' '+str(round(URE,3))
    vaic += "</gml:upperCorner></gml:Envelope></ogc:BBOX></ogc:Filter>"
    numberOfFeaturesFromVaic = GETnumberOfFeaturesFromVaic(vaic + "&resulttype=hits")
    print ('\tGetting features for BBOX:', FeatureType, LLN, LLE, URN, URE,'...', numberOfFeaturesFromVaic)
    if numberOfFeaturesFromVaic < maxF:
        if numberOfFeaturesFromVaic > 0:
            if download:
                f = FeatureType.split(':')[1]+'_'+str(round(LLN,3))+'_'+str(round(LLE,3))+'_'+str(round(URN,3))+'_'+str(round(URE,3))+'.gml'
                with open(f, 'w', encoding='utf-8') as fp:
                    page = requests.get(vaic,  verify=False, headers=headers, allow_redirects=True)
                    chunk = page.text.strip()
                    fp.write(chunk)
    else:
        print ('>Rekursija<')
        vidN = float(LLN)+(float(URN)-float(LLN))/2
        vidE = float(LLE)+(float(URE)-float(LLE))/2

        if vidN <= max_koord and vidE <= max_koord and float(URN) <= max_koord and float(URE) <= max_koord:
            gmlGetRBBOX(url, FeatureType, vidN, vidE, float(URN), float(URE))  #1
        if float(LLN) <= max_koord and vidE <= max_koord and vidN <= max_koord and float(URE) <= max_koord:
            gmlGetRBBOX(url, FeatureType, float(LLN), vidE, vidN, float(URE))  #2
        if float(LLN) <= max_koord and float(LLE) <= max_koord and vidN <= max_koord and vidE <= max_koord:
            gmlGetRBBOX(url, FeatureType, float(LLN), float(LLE), vidN, vidE)  #3
        if vidN <= max_koord and float(LLE) <= max_koord and float(URN) <= max_koord and vidE <= max_koord:
            gmlGetRBBOX(url, FeatureType, vidN, float(LLE), float(URN), vidE)  #4
# ------------------------------------------------------------------------------------
#==============================BEGIN===================================================================================
req_queue = {}
print('Lasu no:', CSV_read_file)
total = 0
with open (CSV_read_file, 'r', encoding='utf-8') as f_read:
    for line in f_read:
        s = line.split("""', '""")
        baseUrl = s[0][2:]+'?'
        Ft_name = s[1][:-3]
        numberOfFeatures = GETnumberOfFeatures(baseUrl, Ft_name)
        lauks_ar_geometriju = geom_check(baseUrl, Ft_name)
        if numberOfFeatures > 0 and lauks_ar_geometriju != '':
            req_queue[baseUrl, Ft_name] = [numberOfFeatures, lauks_ar_geometriju]
        total += numberOfFeatures
print('=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=')
c = 0
#FeatureTypes
for FT in req_queue:
    c  += 1
    print(c, FT,req_queue[FT][0])
    LLN, LLE, URN, URE = 0, 0, max_koord, max_koord
    gmlGetRBBOX(FT[0], FT[1], LLN, LLE, URN, URE)
#Atskaite
with open (csv_write,'w', encoding='utf-8') as f_write:
    for ieraksts in req_queue:
        f_write.write(str(ieraksts)+ ',\tHits: ' +str(req_queue[ieraksts][0])+',\tgeomName: '+req_queue[ieraksts][1]+'\n')
print('Statistika >',csv_write)
print('Gatavs.', total)
