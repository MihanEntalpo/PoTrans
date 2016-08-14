========================================
PoTrans python3 library and console tool
========================================

Purpose
-------

Automatically translate gettext's *.po files to specified language, using Yandex Translate

Install
-------

::
    # pip3 install potrans


Usage of library
----------------

To use it, use must acquire Yandex Translator API key here: https://tech.yandex.ru/keys/get/?service=trnsl
it looks like "trnsl.1.1.20160716T101753Z.a0378f5552843fb4.c5a82afc2a581d1e3717f92d4c753f3f798deb2a"

::
    from potrans import Translator

    key = "trnsl.1.1.20160716T101753Z.a0378f5552843fb4.c5a82afc2a581d1e3717f92d4c753f3f798deb2a"
    translator = Translator(key)
    translator.open_po_file("./en_US.po")
    translator.go_translate("en", "de")
    translator.save_po_file("./de_DE.po")
    translator.save_mo_file("./de_DE.mo")

Usage of console script
-----------------------

Translate from Russian to Italian and save result to po-file:

::
    potrans translate -i ./ru_RU.po -il ru -ol it -o ./it_IT.po --key trnsl.1.1.20160716T101753Z.a0378f5552843fb4.c5a82afc2a581d1e3717f92d4c753f3f798deb2a

if you don't like to specify key every time, you can put it into ~/.config/potrans.key:

::
    echo "trnsl.1.1.20160716T101753Z.a0378f5552843fb4.c5a82afc2a581d1e3717f92d4c753f3f798deb2a" >> ~/.config/potrans.key

now, you can run the same command without key:

::
    potrans translate -i ./ru_RU.po -il ru -ol it -o ./it_IT.po

Translate and save result to *.po and *.mo files:

::
    potrans translate -i ./ru_RU.po -il ru -ol it -o ./it_IT.po -om ./it.IT.mo

Translate with outputting all the phrases and it's translate strings:

::
    potrans translate --debug -i ./ru_RU.po -il ru -ol it -o ./it_IT.po

Translate, using msgid in case msgstr is empty:

::
    potrans translate --usemsgid -i ./ru_RU.po -il ru -ol it -o ./it_IT.po

Just convert *.po to *.mo without translation:

::
    potrans convert -i ./ru_RU.po -o ./ru_RU.mo


