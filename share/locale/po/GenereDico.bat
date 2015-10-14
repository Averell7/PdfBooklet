@echo on
@echo .
@echo Génération de pdfbooklet.pot et pdfshuffler.pot
@echo -----------------------------------------------
@echo .
@echo Supprime l'ancien fichier pdfbooklet.pot
del pdfbooklet.pot
@echo .
C:\Python26\GetText14\bin\xgettext.exe -o pdfbooklet.pot --from-code=UTF-8 ..\..\..\pdfbooklet.py
@echo .
C:\Python26\GetText14\bin\xgettext.exe -o pdfbooklet.pot --from-code=UTF-8 -j ..\..\..\files_chooser.py
@echo .
C:\Python26\GetText14\bin\xgettext.exe -o pdfbooklet.pot --from-code=UTF-8 -j ..\..\..\pdfshuffler_g.py
@echo .
C:\Python26\GetText14\bin\xgettext.exe -o pdfbooklet.pot --from-code=UTF-8 -j -L Glade ..\..\..\data\pdfbooklet2.glade
@echo .
C:\Python26\GetText14\bin\xgettext.exe -o pdfbooklet.pot --from-code=UTF-8 -j -L Glade ..\..\..\data\chooser_dialog.glade
@echo .
C:\Python26\GetText14\bin\xgettext.exe -o pdfbooklet.pot --from-code=UTF-8 -j -L Glade ..\..\..\data\pdfshuffler_g.glade

@echo Supprime l'ancien fichier pdfshuffler.pot
del pdfshuffler.pot
@echo .
C:\Python26\GetText14\bin\xgettext.exe -o pdfshuffler.pot --from-code=UTF-8 ..\..\..\pdfshuffler_g.py
@echo .
C:\Python26\GetText14\bin\xgettext.exe -o pdfshuffler.pot --from-code=UTF-8 -j -L Glade ..\..\..\data\pdfshuffler_g.glade
pause

