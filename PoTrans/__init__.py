import polib
import io
import os
import click
from yandex_translate import YandexTranslate, YandexTranslateException

class Translator:
    """
    Класс для перевода po-файлов
    """
    def __init__(self, yandex_key, src_lang=None, dest_lang=None, src_po_file=None):
        """
        Конструктор
        :param yandex_key: ключ для доступа к API яндекс-переводчика
        :param src_lang: исходный язык
        :param dest_lang: язык назначения
        :param src_po_file: исходный po-файл
        :return:
        """
        self.yandex_key = yandex_key
        self.src_lang = src_lang
        self.dest_lang = dest_lang
        self.yandex_translate = YandexTranslate(self.yandex_key)
        if src_po_file is not None:
            self.open_po_fle(src_po_file)

    def open_po_fle(self, po_filename):
        """
        Открыть po-файл
        :param po_filename:
        :return:
        """
        if isinstance(po_filename, io.TextIOWrapper):
            po_filename = po_filename.name
        self.po = polib.pofile(po_filename)

    def _translate_str(self, text, src_lang, dest_lang, return_src_if_empty_result=True, need_print=False):
        """
        Перевести текстовую строку (приватный метод)
        :param text: текст, который нужно перевести
        :param src_lang: исходный язык
        :param dest_lang: конечный язык
        :param return_src_if_empty_result: вернуть исходную строку, если перевод не найден?
        :param need_print: Выводить на экран информацию о результате перевода (для отладки)
        :return: переведённая строка (или исходная, если перевод не найден, и return_src_if_empty_result==True)
        """
        tr = self.yandex_translate.translate(text, "{}-{}".format(self.src_lang, self.dest_lang))
        if tr['code'] == 200 and len(tr['text']) and tr['text'][0]:
            tr_text = tr['text'][0]
        else:
            tr_text = ""
        if need_print:
            print(text + " => " + tr_text)
        if not tr_text and return_src_if_empty_result:
            tr_text = text
        return tr_text

    def go_translate(self, src_lang=None, dest_lang=None, debug=False, usemsgid=False, **kwargs):
        """
        Запустить перевод po-файла
        :param src_lang: исходный язык
        :param dest_lang: конечный язык
        :param break_on: номер строки, на которой нужно остановить процесс, используется для отладки
        :return:
        """
        break_on = kwargs.get("break_on", False)
        if src_lang is None:
            src_lang = self.src_lang
        if dest_lang is None:
            dest_lang = self.dest_lang
        count = len(self.po)
        pos = 0
        prev_percent = -1
        for item in self.po:
            if break_on and break_on == pos:
                break
            pos += 1
            translated = False
            if item.msgstr:
                item.msgstr = self._translate_str(item.msgstr, src_lang, dest_lang, True, debug)
                translated = True
            if item.msgstr_plural:
                for num in item.msgstr_plural:
                    item.msgstr_plural[num] = self._translate_str(item.msgstr_plural[num], True, debug)
                    translated = True
            if not translated and usemsgid:
                if item.msgid:
                    item.msgstr = self._translate_str(item.msgid, src_lang, dest_lang, True, debug)
                    translated = True
                if item.msgid_plural:
                    for num in item.msgid_plural:
                        item.msgstr_plural[num] = self._translate_str(item.msgid_plural[num], True, debug)
                        translated = True
            percent = int(pos * 100 / count)
            if percent != prev_percent:
                prev_percent = percent
                print("### Progress: " + str(percent) + "% ###")

    def save_po_file(self, dest_po_file=None):
        """
        Сохранить результирующий po-файл
        :param dest_po_file: Имя файла
        :return:
        """
        if dest_po_file is None:
            dest_po_file = self.dest_po_file
        self.po.save(dest_po_file)

    def save_mo_file(self, dest_mo_file=None):
        """
        Сохранить mo-файл
        :param dest_mo_file: имя файла
        :return:
        """
        if dest_mo_file is None:
            dest_mo_file = self.dest_mo_file
        self.po.save_as_mofile(dest_mo_file)

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
        #if issubclass(input_po, click.
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
@click.option("--input_po", "-i", type=click.File("r"), help="Input *.po file to open")
@click.option("--output_mo", "-o", type=click.File("w"), help="Output *.mo file to write to")
def convert(input_po, output_mo):
    t = Translator("", None, None, input_po)
    t.save_mo_file(output_mo)


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