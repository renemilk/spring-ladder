# -*- coding: utf-8 -*-

fakeoutput = []

fakeoutput.append( """BEGINSETUP
BEGINTEAMS
doofus=1
idiot=2
ENDTEAMS
BEGINAIS
ENDAIS
BEGINALLYTEAMS
1=1
2=2
ENDALLYTEAMS
BEGINOPTIONS
turboboost=on
mapname=Tabula
modname=BADSD
ENDOPTIONS
BEGINRESTRICTIONS
bigbird=1
ENDRESTRICTIONS
ENDSETUP
BEGINGAME
CONNECTED doofus
CONNECTED idiot
GAMEID 0f78fb4aca6594070a1f843c97174d8c
GAMESTART
DISCONNECT 666 1 1
GAMEOVER 667
ENDGAME
""")

fakeoutput.append( """BEGINSETUP
BEGINTEAMS
doofus=1
idiot=2
theman=3
john=4
ENDTEAMS
BEGINAIS
ENDAIS
BEGINALLYTEAMS
1=1
2=2
3=2
4=4
ENDALLYTEAMS
BEGINOPTIONS
turboboost=on
ENDOPTIONS
BEGINRESTRICTIONS
bigbird=1
ENDRESTRICTIONS
ENDSETUP
BEGINGAME
CONNECTED doofus
CONNECTED idiot
CONNECTED theman
CONNECTED john
GAMEID 0f78fb4aca6594070a1f843c97174d8c
GAMESTART
TEAMDIED 666 1
TEAMDIED 300 2
LEAVE 200 john
GAMEOVER 667
ENDGAME
""")
fakeoutput.append( """BEGINSETUP
BEGINTEAMS
doofus=1
idiot=2
ENDTEAMS
BEGINAIS
ENDAIS
BEGINALLYTEAMS
1=1
2=2
ENDALLYTEAMS
BEGINOPTIONS
turboboost=on
mapname=Tabula
modname=BADSD
ENDOPTIONS
BEGINRESTRICTIONS
bigbird=1
ENDRESTRICTIONS
ENDSETUP
BEGINGAME
CONNECTED doofus
CONNECTED idiot
GAMEID 0f78fb4aca6594070a1f843c97174d8c
GAMESTART
DISCONNECT 666 1 doofus
TEAMDIED 300 2
GAMEOVER 667
ENDGAME
""")
