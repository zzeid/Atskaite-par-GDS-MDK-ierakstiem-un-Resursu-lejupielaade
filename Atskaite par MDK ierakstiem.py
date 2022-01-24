__author__ = 'holms@outlook.com'
# 2017/02/09-
# 2021/12/05 Py3 version.
# ----------------------------------------------------------------------------------------------------------------------
import requests
import time, datetime
requests.packages.urllib3.disable_warnings()
#ĢDS MDK URL
base_csw_url = 'https://geometadati.viss.gov.lv/geoportal'
find_docid = '<dc:identifier scheme="urn:x-esri:specification:ServiceType:ArcIMS:Metadata:DocID">'
headers = {
    'Accept': 'application/json',
    'Content-Type': 'text/plain'
}
# ----------------------------------------------------------------------------------------------------------------------
def get_mdk_records_count(csw):
    url = csw + '/csw?request=GetRecords&service=CSW&resultType=hits'
    response = requests.get(url, allow_redirects=False, verify=False, headers = headers)
    if response.status_code == 200:
        a = response.text
        b = response.text[a.find('numberOfRecordsMatched="')+len('numberOfRecordsMatched="'):a.find('"',a.find('numberOfRecordsMatched="')+len('numberOfRecordsMatched="'))]
        return int(b)
    else: return 0
# ----------------------------------------------------------------------------------------------------------------------
print ("Start : %s" % time.ctime())
c = 0
max = get_mdk_records_count(base_csw_url)
print ('-------------------------------------------------------------------------------------------------------------')
atskaite = {}
while (c < max):
    url = ''
    title = ''
    metadataStandardName = ''
    inspire_md_url = ''
    interface_url = ''
    oknok = ''
    atskaites_url = ''
    c += 1
    url = base_csw_url + '/csw?request=GetRecords&service=CSW&resultType=results&maxrecords=1&startPosition=' + str(c)
    response = requests.get(url, allow_redirects=False, verify=False, headers = headers)
    if response.status_code == 200:
        a = response.text
        sakums = a.find('<dc:title>') + len('<dc:title>')
        beigas = a.find('<', sakums)
        title = a[sakums:beigas]
        print (c,'/',max, '|\t', time.ctime(), '\t| ',title),
        sakums = a.find(find_docid) + len(find_docid)
        beigas = a.find('<', sakums)
        inspire_md_url = base_csw_url + '/csw?getxml=' + a[sakums:beigas]
        uuid = a[sakums:beigas]
        response = requests.get(inspire_md_url, allow_redirects=False, verify=False, headers=headers)
        if response.status_code == 200:
            a = response.text
            #metadata = str(a.encode('utf-8'))
            metadata = str(a)
            metadata.find('MD_Metadata')
            test = metadata.find('MD_Metadata')
            if test != -1:
                #--------------------organisationName-------------------------------------------------------------------
                sakums = metadata.find('organisationName>')
                sakums = metadata.find('CharacterString>', sakums) + len('CharacterString>')
                beigas = metadata.find('</', sakums)
                organisationName = metadata[sakums:beigas]
                # -------------------metadataStandardName---------------------------------------------------------------
                sakums = metadata.find('metadataStandardName>')
                sakums = metadata.find('CharacterString>', sakums) + len('CharacterString>')
                beigas = metadata.find('</', sakums)
                metadataStandardName = metadata[sakums:beigas]
                #-------------------------------------------------------------------------------------------------------
                interface_url = base_csw_url + '/catalog/wrapper/ivisgds.page?uuid=' + uuid
        else: print ('failed'), inspire_md_url
    else:
        print ('failed'), url
    if metadataStandardName =='': metadataStandardName = '-'
    if organisationName =='': organisationName = '-'
#                                          0     1            2                  3               4           5         6           7
    if interface_url != '': atskaite[c] = [c, title, metadataStandardName, inspire_md_url, interface_url, oknok, organisationName, url]
    interface_url = ''
    organisationName = ''
print ('-------------------------------------------------------------------------------------------------------------')
print ('=============================================================================================================')
print ('count:', max)
print ("End : %s" % time.ctime())
print ('=============================================================================================================')
print ('-------------------------------------------------------------------------------------------------------------')
print ('Rakstam HTML')
print ('-------------------------------------------------------------------------------------------------------------')
with open (datetime.datetime.fromtimestamp(time.time()).strftime('%Y%m%d%H%M%S_')+'MDK_atskaite.html', 'w', encoding='utf-8') as f:
    f.write('''<html><head><meta http-equiv="content-type" content="text/html; charset=UTF-8">\n<title>Atskaite</title></head><body>\n<table cellspacing="0" cellpadding="0" border="1"><tbody>''')
    f.write('\n')
    f.write('<i>Atskaite par MDK ierakstiem ('+time.ctime()+')</i>\n')
    f.write("""<tr><td align="center" valign="middle"><b>Nr.</b></td><td align="center" valign="middle"><b>Resursa nosaukums (FrontEnd URL)</b></td><td align="center" valign="middle"><b>Resursa tips (BackEnd URL)</b></td><td align="center" valign="middle"><b>Iestāde</b></td></tr>""")
    for ieraksts in atskaite:
        f.write('\n<tr>')
        title = atskaite[ieraksts][1]
        #print (ieraksts, atskaite[ieraksts][2], title)
        text = str('<td align="center">')
        text += '<a href="'
        text += atskaite[ieraksts][7]
        text += '">'
        text += str(atskaite[ieraksts][0])
        text += '</a></td><td>'
        text += '<a href="'+atskaite[ieraksts][4]+'">'
        text = str(text)
        text += str(title)
        text += '</a></td><td>'
        text += '<a href="'
        inspire_md_url = str(atskaite[ieraksts][3])
        text = str(text)
        text += str(inspire_md_url)
        text += '">'+atskaite[ieraksts][2]
        text += '</a></td>'
        text += '<td>' + str(atskaite[ieraksts][6]) + '</td>'
        f.write(text)
        f.write('</tr>')
    f.write('\n</tbody></table></body></html>')
print ('-Gatavs------------------------------------------------------------------------------------------------------')
