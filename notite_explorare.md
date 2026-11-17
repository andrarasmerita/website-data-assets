# Notite explorare

## Metoda

- Analiza detaliata pe 3 domenii alese pentru contrast: disneystore.com (site mare), lojatatical.com.br (magazin mic), 5starremoval.weebly.com (site pe platforma).
- Explorare rapida pe headere HTTP, cu o bucla curl, pe alte 8 domenii alese pentru varietate (tara, alfabet, caractere speciale, site mare sau mic, institutie, agentie).
- Restul pana la 200 de domenii va fi analizat automat, pe datele descarcate de crawler (nu manual).
- Instrumente folosite: curl, View Source si DevTools in Chrome.
- In dovezi notez doar numele cookie-urilor, nu si valorile (sunt identificatori de sesiune).
- Ce este dovada directa (ex. un header care numeste tehnologia) si ce este ipoteza (dedusa dupa numele unui header sau cookie) este marcat separat.

## Rezumat

- Cele mai sigure semnale se vad in headere si cookie-uri (X-Generator, X-Magento-Tags, X-Host, Server, nume de cookie-uri), fara sa fie nevoie de HTML.
- Semnalele cautate in HTML (de exemplu tag-ul generator sau cuvinte din URL-uri) sunt fragile: absenta lor nu inseamna ca tehnologia lipseste (la lojatatical.com.br nu am gasit "generator", dar headerele indicau Magento).
- In explorare am gasit mai multe tipuri de cazuri care vor aparea si la scara mare:
  - domeniu fara DNS activ (jcmobilecigars.com);
  - domeniu care raspunde 404, dar cu headerele platformei (5starremoval.weebly.com);
  - redirect-uri catre www, aproape peste tot;
  - site care blocheaza cererile automate cu 403 (ecolab.com);
  - site cu mai multe straturi de infrastructura (disneystore.com, footasylum.com);
  - site care isi declara explicit platforma in headere (insieme.stanford.edu, Drupal);
  - site la care headerele spun doar serverul sau CDN-ul (Apache, nginx, Cloudflare).
- Cloudflare apare la 5 din cele 11 domenii explorate, dar este un strat de infrastructura, nu platforma site-ului.
- La site-urile pe platforme (Weebly) tehnologiile vazute sunt ale platformei, nu ale site-ului propriu-zis.
- Concluzie: detectorul trebuie sa combine mai multe tipuri de dovezi (headere, cookie-uri, HTML), sa urmeze redirect-urile, sa salveze si raspunsurile de eroare si sa inregistreze motivul esecului pentru fiecare domeniu.

---

## Analize detaliate

### disneystore.com

- Se incarca? Da. Redirect 301 catre https://www.disneystore.com/, apoi 200 OK.

- Tehnologii observate (din headere si cookie-uri):
  - Akamai (CDN, primul raspuns)
  - Cloudflare (raspunsul final)
  - Queue-it (sala de asteptare)
  - Salesforce Commerce Cloud / Demandware (ipoteza)
  - Salesforce Einstein / CQuotient (ipoteza)
  - Akamai Bot Manager (ipoteza)

- Dovezi (doar numele cookie-urilor):
  - Header "Server: AkamaiGHost" si "X-Disney-Akamai-Rule" la prima cerere -> Akamai
  - Header "Server: cloudflare", "CF-RAY", "cf-cache-status" la a doua cerere -> Cloudflare
  - Header "x-queueit-connector: akamai" si cookie "wr_entry_path" -> Queue-it
  - Header "x-dw-request-base-id" si cookie-uri "dwsid", "dwanonymous_...", "dwac_..." -> prefixul "dw" vine de la Demandware, deci Salesforce Commerce Cloud (ipoteza dupa nume)
  - Cookie-uri "cqcid", "cquid", "__cq_dnt" -> Salesforce Einstein / CQuotient (ipoteza dupa nume)
  - Cookie-uri "_abck", "bm_sz" -> Akamai Bot Manager (ipoteza dupa nume)

- Ce se vede doar in HTML / Network / dupa JavaScript:
  Nu am verificat manual. Va fi acoperit prin analiza automata pe paginile descarcate.

- Probleme sau surprize:
  - Acelasi site arata doua valori diferite pentru "Server": Akamai la prima cerere si Cloudflare la a doua. Trebuie sa decid ce analizez: raspunsul final sau si pasii intermediari.
  - Site-ul are protectie anti-bot (cookie-urile "_abck" si "bm_sz"), deci un crawler simplu poate primi continut diferit sau poate fi blocat.
  - Cookie-urile si headerele se vad fara JavaScript, deci sunt semnale usor de detectat intr-un crawler.

### lojatatical.com.br

- Se incarca? Da. Redirect 302 catre https://www.lojatatical.com.br/, apoi 200 OK.

- Tehnologii observate (din headere si cookie-uri):
  - Magento (e-commerce)
  - PHP
  - GoCache (CDN / cache, ipoteza dupa nume)

- Dovezi (doar numele cookie-urilor):
  - Header "X-Magento-Tags: FPC" -> Magento
  - Cookie "PHPSESSID" -> PHP
  - Header "Server: gocache", "X-GoCache-CacheStatus" si cookie "__goc_session__" -> GoCache (ipoteza dupa nume)

- Ce se vede doar in HTML / Network / dupa JavaScript:
  - In View Source: "generator" si "cdn" nu au fost gasite. Absenta lor nu inseamna ca tehnologia lipseste (Magento ascunde des tag-ul generator), deci sunt semnale fragile.
  - Restul cautarilor in HTML si zona Network / Console nu le-am verificat manual la acest domeniu. Vor fi acoperite prin analiza automata.

- Probleme sau surprize:
  - Header-ul care dezvaluie Magento apare doar in raspunsul final, nu in redirect. Crawlerul trebuie sa urmeze redirect-urile si sa analizeze raspunsul final.
  - Platforma de e-commerce se vede din headere, fara sa citesc HTML-ul.
  - Semnalele din headere si cookie-uri sunt mai sigure decat cele cautate in HTML, deci solutia trebuie sa combine mai multe tipuri de dovezi.
- Observatie pentru scenariul taskului: un magazin pe Magento este un posibil candidat pentru migrarea catre Shopify (observatie de business, nu o detectie).

### 5starremoval.weebly.com

- Se incarca? Nu in mod real. Raspunde cu HTTP 404 Not Found, deci site-ul nu mai exista, dar platforma Weebly inca raspunde.

- Tehnologii observate (doar la nivel de platforma):
  - Weebly (platforma de site builder)
  - Cloudflare (CDN / protectie)

- Dovezi (doar numele cookie-urilor):
  - Header "X-Host: blu142.sf2p.intern.weebly.net" -> Weebly
  - Header "Server: cloudflare", "CF-Ray", "CF-Cache-Status" -> Cloudflare
  - Cookie "__cf_bm" -> Cloudflare Bot Management (ipoteza dupa nume)

- Ce se vede doar in HTML / Network / dupa JavaScript:
  Nu se aplica, pagina este o eroare 404.

- Probleme sau surprize:
  - Un cod 404 nu inseamna ca nu apar tehnologii: headerele platformei se vad oricum. Crawlerul trebuie sa salveze codul de stare (200, 404 etc.) si sa distinga intre un site real si o pagina de eroare, altfel apar detectii false.
  - La site-urile gazduite pe o platforma (weebly.com), urmele sunt ale platformei, deci stack-ul real al site-ului este ascuns. Multe domenii de pe aceeasi platforma vor avea detectii aproape identice.

---

## Cazuri speciale

### jcmobilecigars.com (domeniu inactiv)

- Se incarca? Nu. curl -v da eroarea "Could not resolve host" (curl: (6)), adica domeniul nu are inregistrare DNS activa.
- Tehnologii observate: niciuna, nu exista raspuns de la server.
- Dovezi: eroarea curl (6) Could not resolve host.
- Probleme sau surprize: nu toate domeniile din lista sunt active. Crawlerul trebuie sa prinda erorile (DNS, timeout, SSL), sa incerce si varianta cu www. si http://, si sa salveze motivul esecului pentru fiecare domeniu in loc sa se opreasca. La scara mare, o parte din domenii vor fi moarte, deci trebuie sa urmaresc rata de esec.

### ecolab.com (acces blocat)

- Se incarca? Nu pentru un client automat. Redirect 301 catre www, apoi 403 Forbidden.
- Am incercat si cu User-Agent de browser, apoi cu headere complete (Accept, Accept-Language). Raspunsul a ramas 403, fara "Server" sau cookie-uri.
- Corpul raspunsului este o pagina "Access Denied" cu un link catre errors.edgesuite.net -> Akamai (ipoteza dupa domeniul edgesuite.net si formatul paginii de eroare).
- Tehnologia site-ului in sine nu se poate determina, dar se vede stratul de protectie anti-bot.
- Concluzii pentru crawler:
  - headerele de browser nu sunt suficiente pentru site-uri cu protectie anti-bot;
  - trebuie salvat si corpul raspunsurilor de eroare (403, 404), pentru ca poate contine dovezi;
  - site-urile de acest tip raman o limitare si ar necesita un browser headless (de exemplu Playwright).

---

## Explorare rapida pe headere (alte 8 domenii, bucla curl)

- footasylum.com: redirect 301 prin "Server: awselb/2.0" (AWS load balancer) catre www, apoi 200 cu "Server: cloudflare" si "CF-Ray" (Cloudflare). Apar si "Server-Timing: ak_p" si cookie-urile "akacd_www-ab-default", "AK_PBassets" -> urme de Akamai (ipoteza dupa nume). Cookie-ul "x-new-site-version" este neidentificat. Mai multe straturi de infrastructura la un singur site.
- ecolab.com: vezi sectiunea "Cazuri speciale".
- insieme.stanford.edu: "X-Generator: Drupal 11", "X-Drupal-Cache", "X-Drupal-Dynamic-Cache" -> Drupal, dovada explicita in headere.
- szentkristofudvarhaz.hu: doar "Server: Apache". Fara cookie-uri. Headerele spun putin, trebuie citit HTML-ul.
- gutendorf.ru: doar "Server: nginx/1.30.6". Versiunea este expusa. Fara cookie-uri.
- xn--kleoghvidevareservice-qfc.dk: doar "Server: nginx/1.31.7". Domeniul cu caractere speciale (punycode) functioneaza normal.
- 253media.com: redirect 301 catre www, "Server: cloudflare", cookie "_cfuvid" -> Cloudflare.
- doortodoororganics.com: doar "Server: cloudflare" si "CF-RAY", fara cookie-uri. Platforma reala (CMS sau e-commerce) nu se vede din headere.

Observatii:
- La 4 din cele 8 domenii headerele dau doar serverul sau CDN-ul, deci detectorul trebuie sa analizeze si HTML-ul.
- Doar un domeniu (Drupal) si-a declarat explicit platforma in headere.
- Site-urile pot bloca crawlerul (ecolab.com), deci trebuie tratate codurile de eroare si salvat corpul raspunsului.

---

## Ce urmeaza

1. Crawler (src/crawler.py): descarca cele 200 de domenii, urmeaza redirect-urile, salveaza in raw/ headerele, HTML-ul (inclusiv la erori) si motivul esecului.
2. Analiza pe date: cele mai frecvente headere, cookie-uri, scripturi externe si valori "generator" din cele 200 de pagini, ca baza pentru semnaturi.
3. Detector bazat pe semnaturi, cu dovada salvata pentru fiecare detectie.
4. Dupa rulare, voi adauga aici rezultatele reale pe cele 200 de domenii (cate au raspuns, cate au dat 403 sau eroare, cele mai frecvente tehnologii).