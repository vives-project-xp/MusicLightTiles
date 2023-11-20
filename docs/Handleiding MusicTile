# De Music Tile
![360° view](./img/360.gif)

## Inleiding
De MusicTile is een tegel die licht en geluid kan produceren wanneer deze geactiveerd wordt. 
Je kunt de tegel activeren door er voldoende kracht op uit te oefenen, bijvoorbeeld wanneer er een persoon op gaat staan. 
In dit bestand zal worden uitgelegd hoe deze tegel werkt en hoe wij deze tegel hebben gemaakt.

## Behuizing
De behuizing van de tegel is 40x40 cm. Dit is groot genoeg voor een volwassen persoon. 
De behuizing is 3D-geprint, waarbij de basis gemaakt is van hout. Dit zorgt voor een stevige basis waarop de 3D-geprinte stukken kunnen worden bevestigd. 
In deze behuizing wordt een afdichtingsstrip bevestigd waarop de bovenste plaat komt. De bovenste plaat bestaat uit een stuk plexiglas dat licht doorschijnend is.
![Person detection](../img/sectionview.png)
Zoals je kunt zien, zitten er aan de buitenkant 2 stukken afdichtingsstrip. Wanneer er op het plexiglas wordt gestaan, wordt de tegel geactiveerd.

## Hardware
De hardware van de tegel bevindt zich binnenin de tegel. Het brein van de tegel is de microcontroller, de ESP32 DevkitM-1.
Deze microcontroller wordt verbonden met de RGB-strip en de luidspreker via de datapinnen. 
Bij het activeren van de tegel zal deze microcontroller een signaal sturen naar deze componenten. Hierbij licht de RGB ledstrip op en zal de luidspreker geluid produceren.

## Voeding
Deze hardware wordt gevoed door een 24V adapter. We hebben deze 24V nodig voor de ledstrip. De ESP32 werkt op een spanning van 5V, dus hebben we een BUCK converter gebruikt die van 24V naar 5V kan converteren.
De luidspreker is aangesloten op de 3.3V pin van de microcontroller.

## Code
We hebben de microcontroller geprogrammeerd via C++. We gebruiken verschillende libraries om de hardware aan te sturen.
We hebben deze libraries nodig om de RGB ledstrip en de luidspreker aan te sturen. Ook hebben we libraries om te kunnen verbinden met de MQTT-server.
De code zorgt ervoor dat we kunnen verbinden met MQTT. Dit is nodig, want we werken samen met een ander project dat het licht en geluid beheert van ons project. 
Via MQTT krijgen wij dan een commando binnen dat zegt wat de hardware moet doen.

## MQTT
Zoals eerder gezegd, gebruiken we MQTT om ons geluid en licht aan te sturen. We hebben een topic gemaakt waarop we een commando kunnen sturen.
Dit commando is een string die een bepaalde waarde heeft. Deze waarde is dan een commando die de hardware moet uitvoeren. 
Zo hebben we een commando om het licht aan te zetten en kunnen we kiezen welke kleur. Ook hebben we een assortiment van geluiden waar we uit kunnen kiezen. 
Deze geluiden zijn opgeslagen op de MP3-speler.

## Websocket
De websocket API wordt gebruikt om berichten te sturen tussen de control server en de client. Er zijn 2 soorten bericten die kunnen verstuurd worden.
Berichten van de server naar de client en vice versa.De client kan subscriben op topics van MQTT, ook kan hij unsubscriben. 
De client kan ook een bericht sturen naar de server. Dit bericht is dan een commando die de server stuurt naar de Music Tiles. 
De commands bestaat uit 'system' , 'audio' en 'light'. De server acties worden verstuurd door de controle server naar de client.
Er zijn 2 commando's die de server kan sturen en dit is 'tiles' en 'state'. 'tiles' stuurt een lijst van alle tiles geconnecteerd aan de controle server. 
Bij het commando 'state' worden updates gestuurd over de state van de tiles.
De controle server zal updates sturen wanneer deze state verandert.
