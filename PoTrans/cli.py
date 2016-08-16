import os
import click
import polib
from .potrans import Translator
from .potrans import YandexTranslateException

@click.group(help="PoTranslator console tool. Used to translate *.po files."
                  + " To display help on command, use <command> --help")
def cli():
    pass

@cli.command(help="Translate source *.po file from one language to another, and save result as *.po or *.mo file")

@click.option("--input_po", "-i", type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True),
              help="Input *.po file to open")
@click.option("--input_lang", "-il", type=click.STRING, help="Source language code (for ex.: ru, en, fr, de)")
@click.option("--output_lang", "-ol", type=click.STRING, help="Destination language code (for ex.: ru, en, fr, de)")
@click.option("--output_po", "-o", type=click.Path(file_okay=True, writable=True, dir_okay=False),
              help="Output *.po file to write to")
@click.option("--output_mo", "-om", type=click.Path(file_okay=True, writable=True, dir_okay=False),
              help="Output *.mo file to write to")
@click.option("--key", "-k", type=click.STRING, help="Yandex API key")
@click.option("--keyfile", "-kf", type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True),
              help="File, containing Yandex API key (if --key not specified)")
@click.option("--debug/--no-debug", default=False, help="Display debug information")
@click.option("--usemsgid/--dont-usemsgid", default=False,
              help="In case, where is no translated string (msgstr), use source one (msgid)")
def translate(
        input_po, input_lang, output_lang, key="", output_po="", output_mo="", keyfile="~/.config/potrans.key",
        debug=False, usemsgid=False
):
    if not key:
        if not keyfile:
            keyfile = "~/.config/potrans.key"
        if keyfile:
            print("Reading API key from file " + keyfile)
            key = get_key_from_conffile(keyfile)
        else:
            print("No --key and no --keyfile specified!")
    if not input_po:
        print("No --input_po specified")
        return
    if not output_po and not output_mo:
        print("No --output_po or --output_mo specified")
        return
    try:
        print("Initializing...")
        if debug:
            print("DBG: Debug enabled")
            print("DBG: mode translate")
        t = Translator(key, input_lang, output_lang, input_po)
        print("Translating from {} to {}...".format(input_lang, output_lang))
        t.go_translate(input_lang, output_lang, debug, usemsgid)
        print("Translation finished")
    except YandexTranslateException as e:
        if str(e) == "ERR_KEY_INVALID":
            print("Invalid yandex translate API key!")
            return
        else:
            print("Error:" + str(e))
    if output_po:
        print("Saving po-file to " + output_po)
        t.save_po_file(output_po)
    if output_mo:
        print("Saveing mo-file to " + output_mo)
        t.save_mo_file(output_mo)


@cli.command(help="Convert source *.po file to *.mo")
@click.option("--input_po", "-i", type=click.Path(exists=True), help="Input *.po file to open")
@click.option("--output_mo", "-o", type=click.Path(writable=True), help="Output *.mo file to write to")
def convert(input_po, output_mo):
    print("Reading PO file " + input_po)
    p = polib.pofile(input_po)
    print("Writing MO file " + output_mo)
    p.save_as_mofile(output_mo)
    print("Done")


def get_key_from_conffile(filename="~/.config/potrans.key"):
    filename = os.path.expanduser(filename)
    if not os.path.exists(filename):
        raise FileNotFoundError("Key file {} not found".format(filename))
    with open(filename) as f:
        key = f.read().strip()
        print("Using Yandex API key from file {}: {}".format(filename, key))
        return key

if __name__ == "__main__":
    cli(obj={})